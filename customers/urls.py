from django.urls import path
from . import views
from cms import views as cms_views

app_name = 'customers'

urlpatterns = [
    # The checkout hnd-off
    path('create-checkout/', views.create_checkout_session, name='create_checkout'),
    
    # The customer management portal
    path('portal/', views.customer_portal, name='customer_portal'),
    path('success/', cms_views.payment_success, name='payment_success'),
    path('cancel/', cms_views.payment_cancel, name='payment_cancel'),
]
