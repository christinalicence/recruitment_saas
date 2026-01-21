from django.test import override_settings
from django.urls import reverse, clear_url_caches
from customers.models import Client as TenantClient, Domain
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context, get_public_schema_name
from customers.tests import TenantCleanupTestCase

User = get_user_model()

@override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
class DashboardSecurityTest(TenantCleanupTestCase):
    def setUp(self):
        clear_url_caches()
        super().setUp()
        
        with schema_context(get_public_schema_name()):
            # Create Tenant A
            self.tenant_a = TenantClient.objects.create(schema_name='tenant-a', name='Tenant A')
            Domain.objects.create(domain='a.localhost', tenant=self.tenant_a, is_primary=True)
            self.user_a = User.objects.create_user(
                username='user@a.com', email='user@a.com', password='password123'
            )

            # Create Tenant B
            self.tenant_b = TenantClient.objects.create(schema_name='tenant-b', name='Tenant B')
            Domain.objects.create(domain='b.localhost', tenant=self.tenant_b, is_primary=True)
            self.user_b = User.objects.create_user(
                username='user@b.com', email='user@b.com', password='password123'
            )

    def test_cross_tenant_access_is_forbidden(self):
        self.client.login(email='user@a.com', password='password123')
        dashboard_url = reverse('cms:dashboard')
        # Try to access Tenant B while logged in as User A
        response = self.client.get(dashboard_url, HTTP_HOST='b.localhost')
        
        # This is expected to FAIL (200 != 403) until middleware is added
        self.assertEqual(response.status_code, 403)