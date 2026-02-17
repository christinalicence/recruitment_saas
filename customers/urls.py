from django.urls import path
from . import views
from cms import views as cms_views

app_name = 'customers'

urlpatterns = [
    path('upgrade/', views.create_checkout_session, name='create_checkout'),
    path('portal/', views.customer_portal, name='customer_portal'),
    path('success/', cms_views.payment_success, name='payment_success'),
    path('cancel/', cms_views.payment_cancel, name='payment_cancel'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
]
