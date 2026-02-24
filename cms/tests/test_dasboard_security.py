from django.test import RequestFactory, override_settings
from django.urls import clear_url_caches
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import connection
from django_tenants.utils import schema_context, get_tenant_model, get_public_schema_name
from customers.models import Domain
from django_tenants.test.cases import TenantTestCase
from cms.views import dashboard


def _attach_middleware(request):
    """Attach session and message storage so views don't crash on missing middleware."""
    session = SessionStore()
    session.save()
    request.session = session
    request._messages = FallbackStorage(request)
    return request


class DashboardSecurityTest(TenantTestCase):
    """
    Security tests for cross-tenant isolation.
    """

    @classmethod
    def setUpClass(cls):
        clear_url_caches()
        super().setUpClass()
        cls.tenant.create_schema(check_if_exists=True)
        TenantModel = get_tenant_model()
        with schema_context(get_public_schema_name()):
            cls.tenant_b = TenantModel.objects.create(
                schema_name='security_tenant_b',
                name='Tenant B',
            )
            cls.domain_b = Domain.objects.create(
                domain='b.localhost',
                tenant=cls.tenant_b,
                is_primary=True,
            )

        cls.tenant_b.create_schema(check_if_exists=True)
        from cms.models import CompanyProfile
        with schema_context(cls.tenant.schema_name):
            CompanyProfile.objects.get_or_create(
                tenant_slug=cls.tenant.schema_name,
                defaults={'display_name': 'Test Tenant'}
            )

    @classmethod
    def tearDownClass(cls):
        with connection.cursor() as cursor:
            cursor.execute(f'DROP SCHEMA IF EXISTS "{cls.tenant_b.schema_name}" CASCADE')
        with schema_context(get_public_schema_name()):
            cls.domain_b.delete()
            cls.tenant_b.delete()
        super().tearDownClass()

    def setUp(self):
        self.factory = RequestFactory()
        self.user_a = User.objects.create_user(
            username='user_a@test.com',
            password='testpassword123',
        )
        with schema_context(self.tenant_b.schema_name):
            self.user_b = User.objects.create_user(
                username='user_b@test.com',
                password='testpassword123',
            )

    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_authenticated_user_can_access_own_dashboard(self):
        """An authenticated user must receive a 200 on their own tenant's dashboard."""
        request = self.factory.get('/dashboard/')
        request.tenant = self.tenant
        request.user = self.user_a
        _attach_middleware(request)
        connection.set_tenant(self.tenant)
        response = dashboard(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_unauthenticated_request_is_blocked(self):
        """An unauthenticated request to the dashboard must be redirected."""
        request = self.factory.get('/dashboard/')
        request.tenant = self.tenant
        request.user = AnonymousUser()
        _attach_middleware(request)

        connection.set_tenant(self.tenant)
        response = dashboard(request)
        self.assertEqual(response.status_code, 302)

    def test_sessions_are_scoped_to_tenant_schema(self):
        """
        SECURITY: Sessions written in tenant A's schema must not be visible
        in tenant B's schema.
        """
        with schema_context(self.tenant.schema_name):
            session_a = SessionStore()
            session_a['user_id'] = self.user_a.pk
            session_a.save()
            session_key = session_a.session_key
            from django.contrib.sessions.models import Session
            self.assertTrue(
                Session.objects.filter(session_key=session_key).exists(),
                "Session should exist in tenant A's schema."
            )
        with schema_context(self.tenant_b.schema_name):
            from django.contrib.sessions.models import Session
            self.assertFalse(
                Session.objects.filter(session_key=session_key).exists(),
                "Session from tenant A must not be visible in tenant B's schema — "
                "this is the core cross-tenant security mechanism."
            )

    def tearDown(self):
        connection.set_schema_to_public()
