from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django_tenants.utils import schema_context
from customers.models import Client as TenantClient, Domain
from cms.models import CompanyProfile
from customers.tests import TenantCleanupTestCase


class DashboardSecurityTest(TenantCleanupTestCase):
    """
    Tests to ensure users cannot access other tenants' dashboards.
    """
    
    def setUp(self):
        """Create two separate tenants with their own users."""
        # Create Tenant A
        with schema_context('public'):
            self.tenant_a = TenantClient.objects.create(
                schema_name='tenant_a_test',
                name='Tenant A'
            )
            Domain.objects.create(
                domain='a.localhost',
                tenant=self.tenant_a,
                is_primary=True
            )
            
            # Create Tenant B
            self.tenant_b = TenantClient.objects.create(
                schema_name='tenant_b_test',
                name='Tenant B'
            )
            Domain.objects.create(
                domain='b.localhost',
                tenant=self.tenant_b,
                is_primary=True
            )
        
        # Create user for Tenant A
        with schema_context('tenant_a_test'):
            CompanyProfile.objects.get_or_create(
                id=1,
                defaults={'display_name': 'Tenant A Corp'}
            )
            self.user_a = User.objects.create_user(
                username='user@a.com',
                email='user@a.com',
                password='password123'
            )
        
        # Create user for Tenant B
        with schema_context('tenant_b_test'):
            CompanyProfile.objects.get_or_create(
                id=1,
                defaults={'display_name': 'Tenant B Corp'}
            )
            self.user_b = User.objects.create_user(
                username='user@b.com',
                email='user@b.com',
                password='password123'
            )

    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_cross_tenant_access_is_forbidden(self):
        """
        Ensures a user cannot jump from one tenant domain to another.
        """
        # Manually authenticate the user by setting session
        # This is necessary because test client login() doesn't work well with tenant schemas
        session = self.client.session
        
        # Login User A by directly setting the session (workaround for tenant schema)
        with schema_context('tenant_a_test'):
            from django.contrib.auth import authenticate
            user = authenticate(username='user@a.com', password='password123')
            self.assertIsNotNone(user, "User A authentication failed")
            
            # Manually log in the user
            self.client.force_login(user)

        dashboard_url = reverse('cms:dashboard')
        
        # Step 2: Legitimate Access to Tenant A
        res_ok = self.client.get(dashboard_url, HTTP_HOST='a.localhost')
        self.assertEqual(res_ok.status_code, 200, "User A should access their own dashboard")

        # Step 3: Malicious Cross-Tenant Access - User A tries to access Tenant B
        response = self.client.get(dashboard_url, HTTP_HOST='b.localhost')
        # Should either redirect to login or return 403
        self.assertIn(response.status_code, [302, 403, 404], 
                     "SECURITY CRITICAL: User A was able to access Tenant B's dashboard!")

    @override_settings(ROOT_URLCONF='recruit_saas.urls_tenant')
    def test_authenticated_user_can_only_access_own_tenant(self):
        """
        Additional test: verify each user can only see their own tenant's data.
        """
        # Login as User A using force_login
        with schema_context('tenant_a_test'):
            user_a = User.objects.get(username='user@a.com')
            self.client.force_login(user_a)
        
        # Access Tenant A dashboard
        response = self.client.get(reverse('cms:dashboard'), HTTP_HOST='a.localhost')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tenant A')
        
        # Try to access Tenant B dashboard (should fail)
        response = self.client.get(reverse('cms:dashboard'), HTTP_HOST='b.localhost')
        self.assertNotEqual(response.status_code, 200, "Cross-tenant access should be blocked")