from django_tenants.middleware.main import TenantMainMiddleware
from django.conf import settings
from django.utils.cache import patch_vary_headers

class CustomTenantMiddleware(TenantMainMiddleware):
    """
    Custom middleware to handle tenant switching, hostname port-stripping,
    and CSRF/Cookie fixes for subdomains.
    """
    
    def get_tenant(self, domain_model, hostname):
        """
        Strip the port (e.g., :8000) from the hostname before the database lookup
        so that 'vf.localhost:8000' matches 'vf.localhost' in the records.
        """
        hostname_no_port = hostname.split(':')[0]
        
        try:
            return domain_model.objects.select_related('tenant').get(
                domain=hostname_no_port
            ).tenant
        except domain_model.DoesNotExist:
            # Fallback to the default django-tenants behavior
            return super().get_tenant(domain_model, hostname)

    def process_response(self, request, response):
        """
        1. Fixes CSRF issues by telling the browser the response varies by Host.
        2. Provides clean debug logging in the console.
        """
        # CSRF FIX: Vital for switching between localhost and subdomains
        patch_vary_headers(response, ('Host',))

        # DEBUG LOGGING: Shows you exactly which schema is active for every request
        if settings.DEBUG and hasattr(request, 'tenant'):
            tenant_name = getattr(request.tenant, 'name', 'Public')
            schema_name = getattr(request.tenant, 'schema_name', 'public')
            print(f"DEBUG: Host={request.get_host()} | Tenant={tenant_name} | Schema={schema_name}")
        
        return response