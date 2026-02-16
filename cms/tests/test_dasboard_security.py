from django.test import override_settings
from django.urls import reverse, clear_url_caches
from django.contrib.auth.models import User
from django.db import connection
from django_tenants.utils import schema_context, get_tenant_model, get_public_schema_name
from customers.models import Domain
from django_tenants.test.cases import TenantTestCase

class DashboardSecurityTest(TenantTestCase):
    """
    Comprehensive security test to ensure cross-tenant isolation.
    """
    
    @classmethod
    def setUpClass(cls):
        clear_url_caches()
        super().setUpClass()

    def setUp(self):
        TenantModel = get_tenant_model()
        with schema_context(get_public_schema_name()):
            self.domain.domain = 'test.localhost'
            self.domain.save()

            self.tenant_b = TenantModel.objects.create(
                schema_name='security_tenant_b',
                name='Tenant B'
            )
            self.domain_b = Domain.objects.create(
                domain='b.localhost',
                tenant=self.tenant_b,
                is_primary=True
            )
        
        with schema_context(self.tenant.schema_name):
            self.user_a = User.objects.create_user(
                username='user_a@test.com', 
                password='password'
            )

        with schema_context(self.tenant_b.schema_name):
            self.user_b = User.objects.create_user(
                username='user_b@test.com', 
                password='password'
            )

    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_cross_tenant_access_is_blocked(self):
        """SECURITY: User A must not be able to access Tenant B's dashboard."""
        dashboard_url = reverse('cms:dashboard')
        
        # Login as User A
        self.client.force_login(self.user_a)
        
        res_ok = self.client.get(dashboard_url, HTTP_HOST='test.localhost')
        self.assertEqual(res_ok.status_code, 200)
        res_blocked = self.client.get(dashboard_url, HTTP_HOST='b.localhost')
        self.assertIn(res_blocked.status_code, [302, 404, 403])

    @classmethod
    def tearDownClass(cls):
        pass

    def tearDown(self):
        from django.db import connection
        connection.set_schema_to_public()