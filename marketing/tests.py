from django.test import Client, TransactionTestCase, override_settings
from django.urls import reverse
from django_tenants.utils import schema_context
from customers.models import Client as TenantClient, Domain
from cms.models import Job


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

@override_settings(ROOT_URLCONF='recruit_saas.urls') 
class OnboardingFlowTest(TenantCleanupTestCase):
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
        # signup post
        signup_data = {
            'company_name': 'Sterling Search',
            'subdomain': 'sterling',
            'admin_email': 'admin@sterling.com',
            'password': 'StrongPassword123!',
        }
        post_url = f"{signup_url}?template=professional"
        response = self.client.post(post_url, data=signup_data)
        # Verify redirect to the new subdomain login
        self.assertRedirects(response, "http://sterling.localhost/login/", fetch_redirect_response=False)
        self.assertTrue(TenantClient.objects.filter(schema_name='sterling').exists())

class SchemaIsolationTest(TenantCleanupTestCase):
    """Tests that one recruiter's data never leaks to another"""
    def test_firm_data_isolation(self):
        # create 2 firms
        firm_a = TenantClient.objects.create(schema_name='firm_a', name='Sterling Search')
        firm_b = TenantClient.objects.create(schema_name='firm_b', name='Global Talent')
        # post job in Firm A's schema
        with schema_context(firm_a.schema_name):
            job_a = Job.objects.create(
                title="Investment Banker",
                salary="£150k",
                location="City of London",
                summary="Exclusive high-stakes role.",
                description="Long description here..."
            )
            self.assertEqual(Job.objects.count(), 1)
            job_a_id = job_a.id
        # switch to Firm B's schema and verify no jobs exist
        with schema_context(firm_b.schema_name):
            # Verify total count is zero in this schema
            self.assertEqual(Job.objects.count(), 0)
            # Try seeing job in wrong schema
            with self.assertRaises(Job.DoesNotExist):
                Job.objects.get(id=job_a_id)
        # Switch back to Firm A and verify job exists
        with schema_context(firm_a.schema_name):
            self.assertEqual(Job.objects.count(), 1)
            self.assertEqual(Job.objects.first().title, "Investment Banker")
            