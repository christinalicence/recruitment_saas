import stripe
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import redirect
from .models import Client
from django.core.mail import send_mail


def create_checkout_session(request):
    """Initiates the Stripe Checkout process."""
    client = request.tenant
    
    if not client.stripe_customer_id:
        customer = stripe.Customer.create(
            email=request.user.email,
            name=client.name,
            metadata={'tenant_id': client.id}
        )
        client.stripe_customer_id = customer.id
        client.save()

    domain = client.domains.first().domain
    
    session = stripe.checkout.Session.create(
        customer=client.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{'price': client.plan.stripe_price_id, 'quantity': 1}],
        mode='subscription',
        success_url=f"http://{domain}:8000/billing/success/",
        cancel_url=f"http://{domain}:8000/billing/cancel/",
        metadata={'tenant_id': client.id}
    )
    return redirect(session.url, code=303)

def customer_portal(request):
    """Sends the user to Stripe's Billing Portal to manage cards/cancellation."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if not request.tenant.stripe_customer_id:
        return redirect('customers:create_checkout')
    session = stripe.billing_portal.Session.create(
        customer=request.tenant.stripe_customer_id,
        return_url=f"http://{request.get_host()}/dashboard/",
    )
    return redirect(session.url, code=303)

@csrf_exempt
def stripe_webhook(request):
    """Server-to-server communication from Stripe to confirm payment."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return HttpResponse(status=400)

    # The 'Handshake': Stripe confirms the checkout was completed successfully
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        tenant_id = session.get('metadata', {}).get('tenant_id')
        
        if tenant_id:
            client = Client.objects.get(id=tenant_id)
            client.is_active = True # Activate the tenant
            client.save()

            send_mail(
                subject="Subscription Active!",
                message=f"Hi {client.name}, your Standard Plan is now active.",
                from_email="billing@recruit-saas.com",
                recipient_list=[client.notification_email_1], # Uses the email from signup
                fail_silently=False,
    )

    return HttpResponse(status=200)
