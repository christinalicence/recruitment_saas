# marketing/tests/test_onboarding.py
from django.test import Client, override_settings
from django.urls import reverse
from customers.models import Client as TenantClient
from customers.tests import TenantCleanupTestCase


@override_settings(ROOT_URLCONF='recruit_saas.urls') 
class OnboardingFlowTest(TenantCleanupTestCase):
    """Tests the complete user journey from template selection to signup"""
    def setUp(self):
        self.client = Client()

    def test_onboarding_to_signup_flow(self):
        """Tests the journey from selection -> preview -> signup"""
        # template selection page
        response = self.client.get(reverse('marketing:template_select'))
        self.assertEqual(response.status_code, 200)
        # preview creation
        preview_url = reverse('marketing:template_preview', kwargs={'template_id': 'professional'})
        response = self.client.get(f"{preview_url}?company_name=Sterling+Search")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sterling Search")
        # signup page GET with prefilled data
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
        # redirect to the new subdomain login
        self.assertRedirects(
            response, 
            "http://sterling.localhost/login/", 
            fetch_redirect_response=False
        )
        # Check tenant created
        self.assertTrue(TenantClient.objects.filter(schema_name='sterling').exists())