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
        """Tests the journey from selection to preview to signup"""
        # select a template
        response = self.client.get(reverse('marketing:template_select'))
        self.assertEqual(response.status_code, 200)

        # preview a template with company name
        preview_url = reverse('marketing:template_preview', kwargs={'template_id': 'executive'})
        response = self.client.get(f"{preview_url}?company_name=Sterling+Search")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sterling Search")

        # navigate to signup with prefilled data
        signup_url = reverse('marketing:tenant_signup')
        response = self.client.get(f"{signup_url}?template=executive&company_name=Sterling+Search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].initial['company_name'], "Sterling Search")

        # perform signup
        signup_data = {
            'company_name': 'Sterling Search',
            'admin_email': 'admin@sterling.com',
            'password': 'StrongPassword123!',
        }
        post_url = f"{signup_url}?template=executive"
        response = self.client.post(post_url, data=signup_data)

        # url should redirect to the new tenant's dashboard on their subdomain
        expected_subdomain = "sterling-search"
        expected_redirect = f"http://{expected_subdomain}.localhost:8000/dashboard/setup/"

        self.assertRedirects(
            response, 
            expected_redirect, 
            fetch_redirect_response=False
        )

        # make sure the tenant was created with the slug
        self.assertTrue(TenantClient.objects.filter(schema_name=expected_subdomain).exists())