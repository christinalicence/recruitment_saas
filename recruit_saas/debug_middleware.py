from django_tenants.middleware.main import TenantMainMiddleware
from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.urls import set_urlconf, reverse
from django.shortcuts import redirect


class CustomTenantMiddleware(TenantMainMiddleware):
    def get_tenant(self, domain_model, hostname):
        # Strip port for database lookup
        hostname_no_port = hostname.split(':')[0]
        
        try:
            return domain_model.objects.select_related('tenant').get(
                domain=hostname_no_port
            ).tenant
        except domain_model.DoesNotExist:
            return super().get_tenant(domain_model, hostname)

    def process_request(self, request):
        # 1. Let the parent find the tenant and set the schema
        super().process_request(request)
        
        # 2. FORCE the URLconf swap
        # If we aren't in public, use the Tenant URLs
        if request.tenant and request.tenant.schema_name != 'public':
            request.urlconf = settings.TENANT_URLCONF
        else:
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
            
        # 3. Actually tell Django to use this specific URLconf for this thread
        set_urlconf(request.urlconf)

    def process_response(self, request, response):
        patch_vary_headers(response, ('Host',))
        if settings.DEBUG and hasattr(request, 'tenant'):
            tenant_name = getattr(request.tenant, 'name', 'Public')
            schema_name = getattr(request.tenant, 'schema_name', 'public')
            # Added URLConf to the log so you can see it working
            print(f"DEBUG: Host={request.get_host()} | Tenant={tenant_name} | URLConf={getattr(request, 'urlconf', 'Default')}")
        
        return response
    

class SubscriptionGuardMiddleware:
    """Middleware to block access to inactive tenants except for billing paths."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Ignore the public marketing site
        if not request.tenant or request.tenant.schema_name == 'public':
            return self.get_response(request)

        # 2. Paths that are ALWAYS allowed (Login, Logout, and Billing)
        # We use reverse() to ensure we match the dynamic tenant URL structure
        allowed_paths = [
            reverse('customers:create_checkout'),
            reverse('customers:stripe_webhook'),
            reverse('customers:payment_success'),
            reverse('customers:payment_cancel'),
            reverse('customers:customer_portal'),
            '/login/', 
            '/logout/',
        ]

        # Check if the current path matches any of our allowed paths
        if any(request.path.startswith(path) for path in allowed_paths):
            return self.get_response(request)

        # 3. If not active AND trial has expired, redirect to checkout
        if not request.tenant.is_active and not request.tenant.is_on_trial:
            return redirect(reverse('customers:create_checkout'))

        return self.get_response(request)