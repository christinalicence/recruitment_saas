from django_tenants.middleware.main import TenantMainMiddleware
from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.urls import set_urlconf

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