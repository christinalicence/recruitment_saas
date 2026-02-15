from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from customers.models import Client, Plan, Domain
from django_tenants.utils import schema_context, get_public_schema_name
from . import TenantTestCase

class StripeBillingTests(TenantTestCase):
    def setUp(self):
        super().setUp()
        with schema_context(get_public_schema_name()):
            # Create a plan for testing
            self.plan = Plan.objects.create(
                name="Standard", 
                stripe_price_id="price_123"
            )
            # Create the tenant and assign the plan
            self.tenant = Client.objects.create(
                schema_name="test-tenant", 
                name="Test Corp", 
                plan=self.plan
            )
            # Create a domain so the view can build the redirect URL
            Domain.objects.create(
                domain="test-tenant.localhost", 
                tenant=self.tenant, 
                is_primary=True
            )
            self.user = User.objects.create_user(
                username="jill", 
                email="jill@test.com"
            )

    @patch('stripe.checkout.Session.create')
    @patch('stripe.Customer.create')
    def test_checkout_session_redirection(self, mock_customer, mock_session):
        """Verify the view creates a Stripe session and redirects correctly."""
        # Setup fake Stripe responses
        mock_customer.return_value.id = "cus_abc123"
        mock_session.return_value.url = "https://checkout.stripe.com/test_pay"

        self.client.force_login(self.user)
        
        # We need to ensure the request is associated with the tenant
        # Usually handled by middleware, but in tests, we target the domain
        response = self.client.get(
            reverse('customers:create_checkout'), 
            HTTP_HOST='test-tenant.localhost:8000'
        )

        # Check for 303 Redirect
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.url, "https://checkout.stripe.com/test_pay")
        
        # Verify success_url used the correct domain
        _, kwargs = mock_session.call_args
        self.assertIn("test-tenant.localhost", kwargs['success_url'])
        self.assertIn("/billing/success/", kwargs['success_url'])