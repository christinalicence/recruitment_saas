from django_tenants.middleware.main import TenantMainMiddleware
from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.urls import set_urlconf, reverse
from django.shortcuts import redirect


class CustomTenantMiddleware(TenantMainMiddleware):
    """Custom Tenant Middleware that ensures the correct URLconf is used based on the tenant."""
    def get_tenant(self, domain_model, hostname):
        hostname_no_port = hostname.split(':')[0]
        try:
            # Try to get the tenant
            return domain_model.objects.select_related('tenant').get(
                domain=hostname_no_port
            ).tenant
        except (domain_model.DoesNotExist, Exception):
            # If the table doesn't exist OR the domain isn't found, 
            # force return the public schema so migrations can run.
            return domain_model.objects.get(schema_name='public')

    def process_request(self, request):
        # Let the parent find the tenant and set the schema
        super().process_request(request)  
        # Safety check: Swap URLconf only if a tenant exists and isn't public
        if hasattr(request, 'tenant') and request.tenant and request.tenant.schema_name != 'public':
            request.urlconf = settings.TENANT_URLCONF
        else:
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF         
        # Actually tell Django to use this specific URLconf for this thread
        set_urlconf(request.urlconf)

    def process_response(self, request, response):
        # Ensure the 'Host' header is included in the Vary header for caching purposes
        patch_vary_headers(response, ('Host',))
        # For local dev 
        if settings.DEBUG and hasattr(request, 'tenant'):
            tenant_name = getattr(request.tenant, 'name', 'Public')
        return response


class SubscriptionGuardMiddleware:
    """Blocks access to inactive tenants except for billing/auth paths.""" 
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If it's the public schema or no tenant attached, let it through
        if not hasattr(request, 'tenant') or request.tenant.schema_name == 'public':
            return self.get_response(request)

        # Paths that are ALWAYS allowed (Login, Logout, and Billing)
        # We use a mix of reverse and hardcoded paths to ensure Stripe can always reach you
        allowed_paths = [
            reverse('customers:create_checkout'),
            reverse('customers:payment_success'),
            reverse('customers:payment_cancel'),
            reverse('customers:customer_portal'),
            '/login/', 
            '/logout/',
            '/customers/stripe-webhook/',
        ]

        # If the request is for an allowed path, continue without checking subscription status
        if any(request.path.startswith(path) for path in allowed_paths):
            return self.get_response(request)

        # Guard: If the tenant is inactive AND their trial has ended, force a redirect to checkout
        if not request.tenant.is_active and not request.tenant.is_on_trial:
            return redirect(reverse('customers:create_checkout'))

        return self.get_response(request)

    def process_request(self, request):
        # This method is used for debug
        if hasattr(request, 'tenant') and request.tenant and request.tenant.schema_name != 'public':
            pass
