from django.test import Client, TransactionTestCase
from django.urls import reverse
from customers.models import Client as TenantClient, Domain
from django_tenants.utils import get_public_schema_name, schema_context
from django.contrib.auth.models import User

class OnboardingFlowTest(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.public_schema = get_public_schema_name()
        
        with schema_context(self.public_schema):
            # Setup a clean public tenant
            Domain.objects.filter(domain="localhost").delete()
            public_tenant, _ = TenantClient.objects.get_or_create(
                schema_name=self.public_schema,
                defaults={'name': 'Public', 'is_active': True}
            )
            Domain.objects.create(domain="localhost", tenant=public_tenant, is_primary=True)

    def test_onboarding_pages_ok(self):
        """Verify the main public pages load without crashing"""
        # Test hardcoded paths to match our new simplified template
        for path in ['/', '/choose-template/', '/signup/', '/about/']:
            response = self.client.get(path, HTTP_HOST="localhost")
            self.assertEqual(response.status_code, 200, f"Path {path} failed!")

    def test_signup_creates_tenant(self):
        """Test the full flow from signup to tenant creation"""
        signup_data = {
            "company_name": "New Agency",
            "admin_email": "hello@newagency.com",
            "password": "Password123!",
        }
        
        response = self.client.post(
            "/signup/?template=startup",
            data=signup_data,
            HTTP_HOST="localhost"
        )
        
        # Check for redirect to the new tenant's login
        self.assertIn("new-agency.getpillarpost.com/login/", response.url)

        # Confirm the tenant exists in the DB
        with schema_context(self.public_schema):
            self.assertTrue(TenantClient.objects.filter(schema_name="new_agency").exists())