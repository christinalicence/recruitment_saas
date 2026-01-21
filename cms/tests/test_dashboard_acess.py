from django.test import override_settings
from django.urls import reverse, clear_url_caches
from customers.models import Client as TenantClient, Domain
from django_tenants.utils import schema_context, get_public_schema_name
from customers.tests import TenantCleanupTestCase

@override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
class DashboardAccessTest(TenantCleanupTestCase):
    def setUp(self):
        clear_url_caches()
        super().setUp()
        with schema_context(get_public_schema_name()):
            self.tenant = TenantClient.objects.create(schema_name='test-co', name='Test Co')
            Domain.objects.create(domain='test-co.localhost', tenant=self.tenant, is_primary=True)

    def test_dashboard_requires_login(self):
        dashboard_url = reverse('cms:dashboard')
        response = self.client.get(dashboard_url, HTTP_HOST='test-co.localhost')
        self.assertEqual(response.status_code, 302)