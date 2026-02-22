import json
from unittest.mock import patch
from django.test import RequestFactory
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import schema_context, get_public_schema_name
from customers.views import stripe_webhook
from customers.models import Client

class StripeWebhookTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.schema_name = 'webhook_test_tenant'
        tenant.name = "Webhook Corp"
        return tenant

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = 'testserver' 
        return domain

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        with schema_context(get_public_schema_name()):
            self.tenant.stripe_customer_id = "cus_webhook_123"
            self.tenant.is_active = False
            self.tenant.save()

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_success_activates_client(self, mock_webhook):
        payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_webhook_123",
                    "metadata": {"tenant_id": str(self.tenant.id)}
                }
            }
        }

        request = self.factory.post(
            '/customers/stripe-webhook/', 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        mock_webhook.return_value = payload
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
            "type": "invoice.payment_failed",
            "data": {"object": {"customer": "cus_webhook_123"}}
        }

        request = self.factory.post(
            '/customers/stripe-webhook/', 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        
        mock_webhook.return_value = payload

        response = stripe_webhook(request)
        
        self.assertEqual(response.status_code, 200)
        
        with schema_context(get_public_schema_name()):
            self.tenant.refresh_from_db()
            self.assertFalse(self.tenant.is_active)