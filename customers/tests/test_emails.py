import json
from unittest.mock import patch
from django.test import RequestFactory
from django.utils.crypto import get_random_string
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import schema_context, get_public_schema_name
from customers.models import Client, Domain, Plan
from customers.views import stripe_webhook


class EmailNotificationTests(TenantTestCase):
    """
    Tests that the platform sends the correct emails at key lifecycle events.
    """

    @classmethod
    def setup_tenant(cls, tenant):
        tenant.schema_name = 'email_test_tenant'
        tenant.name = 'Email Test Corp'
        return tenant

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = f'{get_random_string(8)}.testserver.com'
        return domain

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from django_tenants.utils import get_public_schema_name
        with schema_context(get_public_schema_name()):
            cls.public_tenant, _ = Client.objects.get_or_create(
                schema_name='public',
                defaults={'name': 'Public'}
            )
            cls.public_domain, _ = Domain.objects.get_or_create(
                domain='testserver',
                defaults={
                    'tenant': cls.public_tenant,
                    'is_primary': True,
                }
            )
            if cls.public_domain.tenant != cls.public_tenant:
                cls.public_domain.tenant = cls.public_tenant
                cls.public_domain.save()

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        with schema_context(get_public_schema_name()):
            self.plan, _ = Plan.objects.get_or_create(
                name="Standard",
                defaults={'stripe_price_id': 'price_123'}
            )
            self.tenant.plan = self.plan
            self.tenant.stripe_customer_id = 'cus_email_test_123'
            self.tenant.notification_email_1 = 'owner@emailtest.com'
            self.tenant.is_active = False
            self.tenant.save()

    # signup welcome email

    @patch('marketing.views.send_mail')
    @patch('marketing.views.TenantService.create_onboarding_tenant')
    def test_signup_sends_welcome_email(self, mock_create, mock_send_mail):
        """
        After successful signup, a welcome email must be sent to
        the admin email containing the portal URL.
        """
        mock_create.return_value = (
            self.tenant,
            'email-test-corp.getpillarpost.com'
        )

        from django.test import Client as TestClient
        from django.conf import settings
        from django.urls import set_urlconf, clear_url_caches

        clear_url_caches()
        set_urlconf(settings.PUBLIC_SCHEMA_URLCONF)

        client = TestClient()
        client.post(
            '/signup/',
            {
                'company_name': 'Email Test Corp',
                'admin_email': 'owner@emailtest.com',
                'password': 'SecurePassword123!',
            },
            HTTP_HOST='testserver',
        )
        set_urlconf(None)
        clear_url_caches()

        self.assertTrue(mock_send_mail.called,
                        "send_mail should be called after successful signup.")

        call_args = mock_send_mail.call_args
        positional = call_args[0] if call_args[0] else []
        kwargs = call_args[1] if call_args[1] else {}

        subject = positional[0] if positional else kwargs.get('subject', '')
        self.assertIn('Welcome', subject,
                      f"Welcome email subject should contain 'Welcome', got: {subject}")

        message = positional[1] if len(positional) > 1 else kwargs.get('message', '')
        self.assertIn('email-test-corp.getpillarpost.com', message,
                      "Welcome email body should contain the tenant's portal URL.")

        recipient_list = positional[3] if len(positional) > 3 else kwargs.get('recipient_list', [])
        self.assertIn('owner@emailtest.com', recipient_list,
                      "Welcome email must be sent to the admin email address.")

    # Payment Success Email

    @patch('customers.views.send_mail')
    @patch('stripe.Webhook.construct_event')
    def test_payment_success_sends_confirmation_email(self, mock_webhook, mock_send_mail):
        """
        When a payment succeeds, a confirmation email must be sent to
        the tenant's notification email containing the portal URL.
        """
        payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer': 'cus_email_test_123',
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
        stripe_webhook(request)

        self.assertTrue(mock_send_mail.called,
                        "send_mail should be called after a successful payment.")

        call_kwargs = mock_send_mail.call_args
        positional = call_kwargs[0] if call_kwargs[0] else []
        kwargs = call_kwargs[1] if call_kwargs[1] else {}

        subject = positional[0] if positional else kwargs.get('subject', '')
        self.assertIn('Active', subject,
                      f"Success email subject should confirm activation, got: {subject}")

        recipient_list = positional[3] if len(positional) > 3 else kwargs.get('recipient_list', [])
        self.assertIn('owner@emailtest.com', recipient_list,
                      "Success email must be sent to notification_email_1.")

    # Payment Failure Email

    @patch('customers.views.send_mail')
    @patch('stripe.Webhook.construct_event')
    def test_payment_failure_sends_alert_email(self, mock_webhook, mock_send_mail):
        """
        When a payment fails, an alert email must be sent to the
        tenant's notification email so they can update their billing details.
        """
        with schema_context(get_public_schema_name()):
            self.tenant.is_active = True
            self.tenant.save()

        payload = {
            'type': 'invoice.payment_failed',
            'data': {
                'object': {
                    'customer': 'cus_email_test_123',
                }
            }
        }
        mock_webhook.return_value = payload

        request = self.factory.post(
            '/customers/stripe-webhook/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        stripe_webhook(request)

        self.assertTrue(mock_send_mail.called,
                        "send_mail should be called after a payment failure.")

        call_kwargs = mock_send_mail.call_args
        positional = call_kwargs[0] if call_kwargs[0] else []
        kwargs = call_kwargs[1] if call_kwargs[1] else {}

        subject = positional[0] if positional else kwargs.get('subject', '')
        self.assertIn('Payment', subject,
                      f"Failure email subject should reference payment, got: {subject}")

        recipient_list = positional[3] if len(positional) > 3 else kwargs.get('recipient_list', [])
        self.assertIn('owner@emailtest.com', recipient_list,
                      "Failure email must be sent to notification_email_1.")
