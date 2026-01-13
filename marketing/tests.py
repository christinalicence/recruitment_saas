from django.test import Client, TransactionTestCase, override_settings
from django.urls import reverse
from customers.models import Client as TenantClient, Domain


class TenantCleanupTestCase(TransactionTestCase):
    """Base class that ensures tenant schemas are cleaned up after each test"""
    def tearDown(self):
        super().tearDown()
        # Clean up all tenant schemas except 'public'
        for tenant in TenantClient.objects.exclude(schema_name='public'):
            try:
                tenant.delete(force_drop=True)
            except Exception as e:
                print(f"Warning: Could not delete tenant {tenant.schema_name}: {e}")


@override_settings(ROOT_URLCONF='recruit_saas.urls')  # Force public URLs
class OnboardingFlowTest(TenantCleanupTestCase):
    def setUp(self):
        self.client = Client()

    def test_onboarding_to_signup_flow(self):
        response = self.client.get(reverse('marketing:template_select'))
        self.assertEqual(response.status_code, 200)
        preview_url = reverse('marketing:template_preview', kwargs={'template_id': 'professional'})
        response = self.client.get(f"{preview_url}?company_name=Sterling+Search")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sterling Search")
        signup_url = reverse('marketing:tenant_signup')
        response = self.client.get(f"{signup_url}?template=professional&company_name=Sterling+Search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].initial['company_name'], "Sterling Search")
        signup_data = {
            'company_name': 'Sterling Search',
            'subdomain': 'sterling',
            'admin_email': 'admin@sterling.com',
            'password': 'StrongPassword123!',
        }
        post_url = f"{signup_url}?template=professional"
        response = self.client.post(post_url, data=signup_data)
        self.assertRedirects(response, "http://sterling.localhost/login/", fetch_redirect_response=False)
        self.assertTrue(TenantClient.objects.filter(schema_name='sterling').exists())
        self.assertTrue(Domain.objects.filter(domain='sterling.localhost').exists())
        