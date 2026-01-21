from django_tenants.middleware.main import TenantMainMiddleware
from django.conf import settings
from django.db import connection

class CustomTenantMiddleware(TenantMainMiddleware):
    def get_tenant(self, domain_model, hostname):
        # Strip port if it exists
        hostname_no_port = hostname.split(':')[0]
        try:
            return domain_model.objects.select_related('tenant').get(domain=hostname_no_port).tenant
        except domain_model.DoesNotExist:
            return super().get_tenant(domain_model, hostname)

    def process_request(self, request):
        # 1. Let the base logic find the tenant
        super().process_request(request)
        # 2. DEBUG PRINT: Check if a tenant was actually found
        print(f"DEBUG MIDDLEWARE: Host={request.get_host()} | Tenant={request.tenant}")
        # 3. FORCE URLCONF SWITCH
        # If we found a tenant and it's NOT the public schema, force the tenant URLs
        if request.tenant and request.tenant.schema_name != 'public':
            request.urlconf = settings.TENANT_URLCONF
            # This ensures subsequent code (and templates) know which URLConf to use
            connection.set_tenant(request.tenant)
            