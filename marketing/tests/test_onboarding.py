from django.test import Client
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import get_public_schema_name
from django.conf import settings
from django.urls import clear_url_caches, set_urlconf

class OnboardingFlowTest(TenantTestCase):
    # This tells the test runner to treat the 'public' tenant as the 'tenant' for this test
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.schema_name = get_public_schema_name()
        tenant.name = "Public"
        return tenant

    def setUp(self):
        super().setUp()
        # Ensure we are using Public URLs for these marketing tests
        clear_url_caches()
        set_urlconf(settings.PUBLIC_SCHEMA_URLCONF)
        self.client = Client()

    def test_pages_load(self):
        # We test the paths directly to ensure the logic works 
        # independently of the reverse() resolver's state
        for path in ['/', '/about/', '/choose-template/']:
            response = self.client.get(path, HTTP_HOST="testserver")
            self.assertEqual(response.status_code, 200, f"Error on {path}")

    def tearDown(self):
        set_urlconf(None)
        super().tearDown()