from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django_tenants.utils import schema_context
from customers.models import Client as TenantClient, Domain
from cms.models import CompanyProfile
from customers.tests import TenantTestCase


class PreviewFrameTest(TenantTestCase):
    """
    Tests for the live preview functionality in the site editor.
    """
    
    def setUp(self):
        """Create a test tenant with a user and profile."""
        with schema_context('public'):
            self.tenant = TenantClient.objects.create(
                schema_name='testcorp',
                name='Test Corp'
            )
            Domain.objects.create(
                domain='testcorp.localhost',
                tenant=self.tenant,
                is_primary=True
            )
        
        # Create user and profile in tenant schema
        with schema_context('testcorp'):
            with schema_context('testcorp'):
            # Match display_name to self.tenant.name ('Test Corp')
                CompanyProfile.objects.create(
                    display_name='Test Corp', 
                    hero_title='Test Corp Branding'
                )

    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_preview_frame_access(self):
        with schema_context('testcorp'):
            user = User.objects.get(username='admin@test.com')
            self.client.force_login(user)

        url = reverse('cms:live_preview')
        response = self.client.get(url, HTTP_HOST='testcorp.localhost')
        
        self.assertEqual(response.status_code, 200)
        # Now this will pass because the hero_title is what's rendered
        self.assertContains(response, "Test Corp Branding")

    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_preview_frame_requires_login(self):
        """Test that unauthenticated users cannot access the preview."""
        url = reverse('cms:live_preview')
        response = self.client.get(url, HTTP_HOST='testcorp.localhost')
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)