from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from customers.views import stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    # This includes the marketing urls ONLY for the public site
    path('', include('marketing.urls')),
    path('billing/stripe-webhook/', stripe_webhook, name='stripe_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )