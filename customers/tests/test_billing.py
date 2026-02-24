import json
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from unittest.mock import patch
from customers.models import Plan
from customers.views import create_checkout_session, stripe_webhook
from django_tenants.utils import schema_context, get_public_schema_name
from django_tenants.test.cases import TenantTestCase
from django.test import RequestFactory


class StripeBillingTests(TenantTestCase):
    @classmethod
    def setup_domain(cls, domain):
        domain.domain = f'{get_random_string(8)}.testserver.com'
        return domain

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
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

    @patch('stripe.checkout.Session.create')
    @patch('stripe.Customer.create')
    def test_checkout_session_redirection(self, mock_customer, mock_session):

        mock_customer.return_value.id = "cus_abc123"
        mock_session.return_value.url = "https://checkout.stripe.com/test_pay"

        request = self.factory.get('/')
        request.tenant = self.tenant
        request.user = self.user

        response = create_checkout_session(request)

        self.assertIn(response.status_code, [302, 303])
        self.assertEqual(response['Location'], "https://checkout.stripe.com/test_pay")

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_success_activates_client(self, mock_webhook):
        payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer': 'cus_123',
                    'metadata': {'tenant_id': str(self.tenant.id)}
                }
            }
        }
        mock_webhook.return_value = payload

        request = self.factory.post(
            '/customers/stripe-webhook/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        response = stripe_webhook(request)

        self.assertEqual(response.status_code, 200)
        with schema_context(get_public_schema_name()):
            self.tenant.refresh_from_db()
            self.assertTrue(self.tenant.is_active)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_failure_deactivates_client(self, mock_webhook):
        with schema_context(get_public_schema_name()):
            self.tenant.is_active = True
            self.tenant.save()

        payload = {
            'type': 'invoice.payment_failed',
            'data': {'object': {'customer': 'cus_123'}}
        }
        mock_webhook.return_value = payload

        request = self.factory.post(
            '/customers/stripe-webhook/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        response = stripe_webhook(request)

        self.assertEqual(response.status_code, 200)
        with schema_context(get_public_schema_name()):
            self.tenant.refresh_from_db()
            self.assertFalse(self.tenant.is_active)
