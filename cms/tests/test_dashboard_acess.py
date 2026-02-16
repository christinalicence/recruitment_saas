from django.test import override_settings
from django.urls import reverse, clear_url_caches
from django_tenants.utils import schema_context, get_public_schema_name
from django_tenants.test.cases import TenantTestCase

class DashboardAccessTest(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.schema_name = 'access_test'
        return tenant

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = 'access-test.localhost'
        return domain

    def setUp(self):
        clear_url_caches()


    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_dashboard_requires_login(self):
        dashboard_url = reverse('cms:dashboard')
        response = self.client.get(dashboard_url, HTTP_HOST='access-test.localhost')
        self.assertEqual(response.status_code, 302)

    @classmethod
    def tearDownClass(cls):
        pass