from django.test import Client, override_settings
from django.urls import reverse
from customers.models import Client as TenantClient
from customers.tests import TenantCleanupTestCase


@override_settings(ROOT_URLCONF="recruit_saas.urls")
class OnboardingFlowTest(TenantCleanupTestCase):
    """Tests the complete user journey from template selection to signup"""

    def setUp(self):
        self.client = Client()

    def test_onboarding_to_signup_flow(self):
        """Tests the journey from selection to preview to signup"""
        url = reverse("public_marketing:template_select")
        response = self.client.get(url, HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        preview_url = reverse(
            "public_marketing:template_preview",
            kwargs={"template_id": "executive"},
        )

        print(f"DEBUG: Preview URL is: {preview_url}")

        response = self.client.get(
            f"{preview_url}?company_name=Sterling+Search",
            HTTP_HOST="localhost",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sterling Search")
        signup_url = reverse("public_marketing:tenant_signup")
        response = self.client.get(
            f"{signup_url}?template=executive&company_name=Sterling+Search",
            HTTP_HOST="localhost",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].initial["company_name"],
            "Sterling Search",
        )
        signup_data = {
            "company_name": "Sterling Search",
            "admin_email": "admin@sterling.com",
            "password": "StrongPassword123!",
        }

        post_url = f"{signup_url}?template=executive"
        response = self.client.post(
            post_url,
            data=signup_data,
            HTTP_HOST="localhost",
        )
        # DEBUG: If this fails, see what errors the form has
        if response.status_code == 200:
            print(f"Form Errors: {response.context['form'].errors}")

        expected_subdomain = "sterling-search"
        # Match the local dev port
        expected_redirect = f"http://{expected_subdomain}.localhost:8000/login/"
        
        self.assertRedirects(
            response,
            expected_redirect,
            fetch_redirect_response=False,
        )
