from django.test import RequestFactory, override_settings
from django.urls import reverse, clear_url_caches
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

    The security mechanism being tested:
      - django_session is a TENANT table (not shared), so sessions created in
        tenant A's Postgres schema cannot be read in tenant B's schema.
      - When a request arrives at tenant B's domain, TenantMiddleware sets the
        search_path to tenant B's schema. SessionMiddleware then reads
        django_session in that schema. If the session was written to tenant A,
        it is simply not found, and @login_required redirects to login.

    We test these two things separately to avoid the fragile interaction between
    the Django test client, TenantMiddleware, and schema_context.
    """

    @classmethod
    def setUpClass(cls):
        clear_url_caches()
        super().setUpClass()

        # Force cms migrations into the base tenant schema.
        cls.tenant.create_schema(check_if_exists=True)

        # tenant_b must be created and provisioned here (outside per-test
        # transactions) so DDL can run without the Postgres "pending trigger
        # events" error.
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
        # TenantTestCase points the connection at self.tenant before each test.
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

        # RequestFactory skips TenantMiddleware, so the DB connection isn't
        # automatically pointed at the tenant schema. Set it explicitly so
        # the dashboard view can find cms_companyprofile.
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

        This is the core isolation mechanism. In production, when user_a logs
        in via tenant A's domain, the session row is written to tenant A's
        django_session table. When the same browser later hits tenant B's
        domain, TenantMiddleware sets the search_path to tenant B's schema —
        and the session simply doesn't exist there, so @login_required fires.
        """
        # Write a session in tenant A's schema
        with schema_context(self.tenant.schema_name):
            session_a = SessionStore()
            session_a['user_id'] = self.user_a.pk
            session_a.save()
            session_key = session_a.session_key

            # Confirm it exists in tenant A
            from django.contrib.sessions.models import Session
            self.assertTrue(
                Session.objects.filter(session_key=session_key).exists(),
                "Session should exist in tenant A's schema."
            )

        # Confirm it does NOT exist in tenant B's schema
        with schema_context(self.tenant_b.schema_name):
            from django.contrib.sessions.models import Session
            self.assertFalse(
                Session.objects.filter(session_key=session_key).exists(),
                "Session from tenant A must not be visible in tenant B's schema — "
                "this is the core cross-tenant security mechanism."
            )

    def tearDown(self):
        connection.set_schema_to_public()