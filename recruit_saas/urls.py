from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import RedirectView
from django.templatetags.static import static as static_tag
from customers.views import stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url=static_tag('marketing/images/favicons/favicon.ico'))),
    path('', include('marketing.urls')),
    path('customers/stripe-webhook/', stripe_webhook, name='stripe_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )