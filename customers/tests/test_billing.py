import json
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.utils.crypto import get_random_string
from unittest.mock import patch
from customers.models import Client, Plan, Domain
from django_tenants.utils import schema_context, get_public_schema_name
from django_tenants.test.cases import TenantTestCase

class StripeBillingTests(TenantTestCase):
    @classmethod
    def setup_domain(cls, domain):
        domain.domain = f'{get_random_string(8)}.testserver.com'
        return domain

    def setUp(self):
        super().setUp()
        with schema_context(get_public_schema_name()):
            self.plan, _ = Plan.objects.get_or_create(
                name="Standard", 
                defaults={'stripe_price_id': "price_123"}
            )
            self.tenant.plan = self.plan
            self.tenant.stripe_customer_id = "cus_123"
            self.tenant.save()
            
            self.user = User.objects.create_user(
                username=f"user_{get_random_string(5)}", 
                email="jill@test.com"
            )

@patch('stripe.Webhook.construct_event')
@patch('stripe.checkout.Session.create')
@patch('stripe.Customer.create')
def test_checkout_session_redirection(self, mock_customer, mock_session, mock_webhook):
    # Setup mocks
    mock_webhook.return_value = {'type': 'dummy'}
    
    mock_customer.return_value.id = "cus_abc123"
    mock_session.return_value.url = "https://checkout.stripe.com/test_pay"

    user_logged_in.disconnect(dispatch_uid="update_last_login")
    self.client.force_login(self.user)
    
    # Use reverse to ensure the path is exactly what Django expects
    url = reverse('customers:create_checkout')
    response = self.client.get(url, HTTP_HOST=self.domain.domain)
    
    self.assertIn(response.status_code, [302, 303])
    self.assertEqual(response.url, "https://checkout.stripe.com/test_pay")

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_success_activates_client(self, mock_webhook):
        payload = {"id": "evt_test"}
        mock_webhook.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer': 'cus_123',
                    'metadata': {'tenant_id': str(self.tenant.id)}
                }
            }
        }

        response = self.client.post(
            '/customers/stripe-webhook/', 
            data=json.dumps(payload), 
            content_type="application/json",
            HTTP_HOST='testserver'
        )

        self.assertEqual(response.status_code, 200)
        with schema_context(get_public_schema_name()):
            self.tenant.refresh_from_db()
            self.assertTrue(self.tenant.is_active)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_failure_deactivates_client(self, mock_webhook):
        with schema_context(get_public_schema_name()):
            self.tenant.is_active = True
            self.tenant.save()

        payload = {"id": "evt_fail"}
        mock_webhook.return_value = {
            'type': 'invoice.payment_failed',
            'data': {'object': {'customer': 'cus_123'}}
        }

        response = self.client.post(
            '/customers/stripe-webhook/',
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_HOST='testserver'
        )

        self.assertEqual(response.status_code, 200)
        with schema_context(get_public_schema_name()):
            self.tenant.refresh_from_db()
            self.assertFalse(self.tenant.is_active)