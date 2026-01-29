from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # The checkout hnd-off
    path('create-checkout/', views.create_checkout_session, name='create_checkout'),
    
    # The customer management portal
    path('portal/', views.customer_portal, name='customer_portal'),
    
    # The secret handshake for Stripe
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
]