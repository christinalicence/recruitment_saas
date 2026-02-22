from django.test import override_settings
from django.urls import reverse, clear_url_caches
from django.contrib.auth.models import User
from django_tenants.utils import schema_context
from cms.models import CompanyProfile
from django_tenants.test.cases import TenantTestCase

class PreviewFrameTest(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.schema_name = 'preview_test'
        return tenant

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = 'preview-test.localhost'
        return domain

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tenant.create_schema(check_if_exists=True)

    def setUp(self):
        clear_url_caches()
        with schema_context(self.tenant.schema_name):
            User.objects.create_user(username='admin@test.com', password='password')
            CompanyProfile.objects.create(
                tenant_slug=self.tenant.schema_name,
                hero_title='Test Corp Branding'
            )

    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_preview_frame_access(self):
        with schema_context(self.tenant.schema_name):
            user = User.objects.get(username='admin@test.com')
            self.client.force_login(user)

        url = reverse('cms:live_preview')
        response = self.client.get(url, HTTP_HOST='preview-test.localhost')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Corp Branding")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()