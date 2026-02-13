from xmlrpc import client
import stripe
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import redirect
from urllib3 import request
from .models import Client
from django.core.mail import send_mail


def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    client = request.tenant
    
    if not client.stripe_customer_id:
        customer = stripe.Customer.create(
            email=request.user.email,
            name=client.name,
            metadata={'tenant_id': client.id}
        )
        client.stripe_customer_id = customer.id
        client.save()

    # Determine protocol based on environment, keep local development on http
    protocol = "https" if not settings.DEBUG else "http"
    current_host = request.get_host() 
    
    session = stripe.checkout.Session.create(
        customer=client.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{'price': client.plan.stripe_price_id, 'quantity': 1}],
        mode='subscription',
        success_url=f"{protocol}://{current_host}/customers/success/",
        cancel_url=f"{protocol}://{current_host}/customers/cancel/",
        metadata={'tenant_id': client.id}
    )
    
    return redirect(session.url, code=303)


def customer_portal(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    client = request.tenant 
    if not client.stripe_customer_id:
        customer = stripe.Customer.create(
            email=request.user.email,
            name=client.name,
            metadata={'tenant_id': client.id}
        )
        client.stripe_customer_id = customer.id
        client.save()

    return_url = f"https://{request.get_host()}/dashboard/"
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=client.stripe_customer_id,
            return_url=return_url,
        )
        return redirect(session.url, code=303)
    except stripe.error.StripeError as e:
        return redirect('customers:create_checkout')


@csrf_exempt
def stripe_webhook(request):
    """Handle incoming Stripe webhooks to update tenant subscription status."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return HttpResponse(status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        tenant_id = session.get('metadata', {}).get('tenant_id')
        
        if tenant_id:
            client = Client.objects.get(id=tenant_id)
            client.is_active = True
            client.save()

            domain = client.domains.filter(is_primary=True).first()
            portal_url = f"https://{domain.domain}/login/" if domain else "https://getpillarpost.com"

            try:
                send_mail(
                    subject="Subscription Active!",
                    message=f"Hi {client.name},\n\nYour Standard Plan is now active! You can access your portal here: {portal_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.notification_email_1],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Stripe Success Email Failed: {e}")

    elif event['type'] == 'invoice.payment_failed':
        session = event['data']['object']
        customer_id = session.get('customer')
        
        if customer_id:
            try:
                client = Client.objects.get(stripe_customer_id=customer_id)
                client.is_active = False 
                client.save()
                
                try:
                    send_mail(
                        subject="Action Required: Payment Failed",
                        message=f"Hi {client.name}, we were unable to process your payment. Please log in to update your billing.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.notification_email_1],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Stripe Failure Email Failed: {e}")
            except Client.DoesNotExist:
                pass
    return HttpResponse(status=200)