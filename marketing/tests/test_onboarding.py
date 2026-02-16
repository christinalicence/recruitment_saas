from django.test import Client as TestClient, TestCase
from django.conf import settings
from django.urls import clear_url_caches, set_urlconf
from django.template import engines
from customers.models import Client as TenantClient, Domain
from django_tenants.utils import schema_context, get_public_schema_name
from django_tenants.utils import schema_context


class MarketingPagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        with schema_context(get_public_schema_name()):
            cls.public_tenant, _ = TenantClient.objects.get_or_create(
                schema_name='public', 
                defaults={'name': 'Public'}
            )
            
            domain_exists = Domain.objects.filter(domain='testserver').first()
            if not domain_exists:
                Domain.objects.create(
                    domain='testserver',
                    tenant=cls.public_tenant,
                    is_primary=True
                )
            else:
                if domain_exists.tenant != cls.public_tenant:
                    domain_exists.tenant = cls.public_tenant
                    domain_exists.save()

    def setUp(self):
        django_engine = engines['django']
        django_engine.engine.libraries['tenant_tags'] = 'marketing.templatetags.tenant_tags'

        clear_url_caches()
        set_urlconf(settings.PUBLIC_SCHEMA_URLCONF)
        self.client = TestClient()

    def test_pages_load(self):
        """Verify marketing pages return 200 and contain expected branding."""
        # Test Landing Page
        response = self.client.get('/', HTTP_HOST="testserver")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pillar & Post") # Check branding

        # Test Template Selection
        response = self.client.get('/choose-template/', HTTP_HOST="testserver")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Executive") # Check data from view

    def test_tenant_signup_creates_client(self):
        """Verify that the signup form triggers tenant creation via TenantService."""
        signup_url = '/signup/'
        data = {
            'company_name': 'Green Recruitment',
            'admin_email': 'admin@green.com',
            'password': 'SecurePassword123!',
        }
        
        response = self.client.post(signup_url, data, HTTP_HOST="testserver")
        
        from customers.models import Client
        self.assertTrue(Client.objects.filter(name='Green Recruitment').exists())

def test_tenant_domain_mapping(self):
    """Verify the Domain record is correctly linked to the new Client."""
    signup_url = '/signup/'
    data = {
        'company_name': 'Green Recruitment',
        'admin_email': 'admin@green.com',
        'password': 'SecurePassword123!',
    }
    
    self.client.post(signup_url, data, HTTP_HOST="testserver")
    
    with schema_context('public'):
        tenant = TenantClient.objects.get(name='Green Recruitment')
        domain = Domain.objects.get(tenant=tenant)
        
        self.assertEqual(domain.domain, "green-recruitment.getpillarpost.com")
        self.assertTrue(domain.is_primary)

    def test_tenant_signup_redirects_to_subdomain(self):
        """Verify signup redirects to the new tenant subdomain."""
        data = {
            'company_name': 'Blue Agency',
            'admin_email': 'contact@blue.com',
            'password': 'SecurePassword123!',
        }
        response = self.client.post('/signup/', data, HTTP_HOST="testserver")
        
        # Check for the expected redirect URL (slugified name + base domain)
        expected_url = "https://blue-agency.getpillarpost.com/login/"
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def tearDown(self):
        set_urlconf(None)
        clear_url_caches()