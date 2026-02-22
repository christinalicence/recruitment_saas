from django.test import override_settings
from django.urls import reverse, clear_url_caches
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db import connection
from django_tenants.utils import schema_context, get_tenant_model, get_public_schema_name
from customers.models import Domain
from django_tenants.test.cases import TenantTestCase


class DashboardSecurityTest(TenantTestCase):
    """
    Security test: proves a logged-in user from Tenant A cannot access Tenant B's dashboard.
    """

    @classmethod
    def setUpClass(cls):
        clear_url_caches()
        super().setUpClass()
        cls.tenant.create_schema(check_if_exists=True)
        TenantModel = get_tenant_model()
        with schema_context(get_public_schema_name()):
            cls.domain.domain = 'test.localhost'
            cls.domain.save()

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
        self.user_a = User.objects.create_user(
            username='user_a@test.com',
            password='password',
        )
        with schema_context(self.tenant_b.schema_name):
            self.user_b = User.objects.create_user(
                username='user_b@test.com',
                password='password',
            )

    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_cross_tenant_access_is_blocked(self):
        """SECURITY: User A must not be able to access Tenant B's dashboard."""
        dashboard_url = reverse('cms:dashboard')
        from django.contrib.auth.models import update_last_login
        user_logged_in.disconnect(update_last_login)
        try:
            with schema_context(self.tenant.schema_name):
                self.client.force_login(self.user_a)
        finally:
            user_logged_in.connect(update_last_login)

        res_ok = self.client.get(dashboard_url, HTTP_HOST='test.localhost')
        self.assertEqual(res_ok.status_code, 200)
        res_blocked = self.client.get(dashboard_url, HTTP_HOST='b.localhost')
        self.assertIn(res_blocked.status_code, [302, 404, 403])

    def tearDown(self):
        connection.set_schema_to_public()