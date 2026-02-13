from django.test import Client, override_settings, TransactionTestCase
from django.urls import reverse
from customers.models import Client as TenantClient, Domain
from django_tenants.utils import get_public_schema_name, schema_context
from django.contrib.auth.models import User

@override_settings(ROOT_URLCONF="recruit_saas.urls_public")
class OnboardingFlowTest(TransactionTestCase):
    """
    Test the public marketing onboarding flow.
    Uses TransactionTestCase to avoid TenantTestCase complications.
    """
    
    def setUp(self):
        self.client = Client()
        
        # Ensure public tenant and localhost domain exist
        public_schema = get_public_schema_name()
        with schema_context(public_schema):
            # Clean up any existing localhost domain
            Domain.objects.filter(domain="localhost").delete()
            
            # Get or create public tenant
            public_tenant, created = TenantClient.objects.get_or_create(
                schema_name=public_schema,
                defaults={'name': 'Public', 'is_active': True}
            )
            
            # Create localhost domain
            Domain.objects.create(
                domain="localhost",
                tenant=public_tenant,
                is_primary=True
            )

    def test_template_select_page_loads(self):
        """Test that the template selection page loads successfully"""
        url = reverse("public_marketing:template_select")
        response = self.client.get(url, HTTP_HOST="localhost")
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "template")

    def test_signup_creates_tenant(self):
        """Test that signup creates a new tenant and redirects correctly"""
        signup_url = reverse("public_marketing:tenant_signup")
        signup_data = {
            "company_name": "Test Company",
            "admin_email": "admin@testcompany.com",
            "password": "TestPassword123!",
        }

        # Perform the signup POST
        response = self.client.post(
            f"{signup_url}?template=executive",
            data=signup_data,
            HTTP_HOST="localhost",
        )

        # Verify redirect to new tenant portal
        expected_domain = "test-company.getpillarpost.com"
        expected_redirect = f"https://{expected_domain}/login/"
        
        self.assertRedirects(
            response,
            expected_redirect,
            fetch_redirect_response=False,
        )

        # Verify tenant was created in public schema
        with schema_context(get_public_schema_name()):
            self.assertTrue(
                TenantClient.objects.filter(schema_name="test_company").exists()
            )
            tenant = TenantClient.objects.get(schema_name="test_company")
            self.assertTrue(tenant.is_active)
            self.assertEqual(tenant.template_choice, "executive")
            
            # Verify domain was created
            domain = Domain.objects.get(domain=expected_domain)
            self.assertEqual(domain.tenant, tenant)
            self.assertTrue(domain.is_primary)

        # Verify user was created in tenant schema
        with schema_context("test_company"):
            self.assertTrue(
                User.objects.filter(email="admin@testcompany.com").exists()
            )

    def tearDown(self):
        """Clean up test data"""
        public_schema = get_public_schema_name()
        
        # Clean up any test tenants created
        with schema_context(public_schema):
            # Delete test tenant (this will cascade delete the domain)
            test_tenants = TenantClient.objects.filter(
                schema_name__in=["test_company", "sterling_search"]
            )
            for tenant in test_tenants:
                try:
                    # Drop schema first
                    from django.db import connection
                    cursor = connection.cursor()
                    cursor.execute(f'DROP SCHEMA IF EXISTS "{tenant.schema_name}" CASCADE')
                    # Then delete the tenant record
                    tenant.delete()
                except Exception as e:
                    print(f"Warning during cleanup: {e}")