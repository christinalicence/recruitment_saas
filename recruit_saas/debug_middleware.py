# recruit_saas/debug_middleware.py
from django_tenants.middleware.main import TenantMainMiddleware
from django.conf import settings  # Import settings

class CustomTenantMiddleware(TenantMainMiddleware):
    def get_tenant(self, domain_model, hostname):
        if 'localhost:' in hostname or '127.0.0.1:' in hostname:
            try:
                return domain_model.objects.select_related('tenant').get(domain=hostname).tenant
            except domain_model.DoesNotExist:
                pass
        return super().get_tenant(domain_model, hostname)

    def process_request(self, request):
        # Let the middleware find the tenant first
        super().process_request(request)
        
        # If a tenant is found, force Django to use the Tenant URLConf
        if request.tenant and request.tenant.schema_name != 'public':
            # This line solves the "Using the URLconf defined in recruit_saas.urls" problem
            request.urlconf = settings.TENANT_URLCONF