from django_tenants.middleware.main import TenantMainMiddleware
from django.conf import settings

class CustomTenantMiddleware(TenantMainMiddleware):
    """
    Custom tenant middleware that handles hostname with ports
    and provides debug information about tenant resolution.
    """
    
    def get_tenant(self, domain_model, hostname):
        """
        Override to strip port from hostname before lookup.
        This ensures 'localhost:8000' matches 'localhost' in the database.
        """
        # Strip port if it exists
        hostname_no_port = hostname.split(':')[0]
        
        try:
            return domain_model.objects.select_related('tenant').get(
                domain=hostname_no_port
            ).tenant
        except domain_model.DoesNotExist:
            # Fallback to parent class logic
            return super().get_tenant(domain_model, hostname)

    def process_request(self, request):
        """
        Process the request and add debug logging.
        """
        # Let the parent class handle tenant detection and schema switching
        response = super().process_request(request)
        
        # Debug logging (only in DEBUG mode)
        if settings.DEBUG:
            tenant_name = getattr(request.tenant, 'name', 'Unknown')
            schema_name = getattr(request.tenant, 'schema_name', 'Unknown')
            print(f"DEBUG MIDDLEWARE: Host={request.get_host()} | Tenant={tenant_name} | Schema={schema_name}")
        
        return response