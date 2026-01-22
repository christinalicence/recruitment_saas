from cms.models import CompanyProfile


def tenant_profile(request):
    """Make the tenant's profile available in all templates."""
    profile = None
    
    # Only fetch profile for tenant-specific requests (not public schema)
    if hasattr(request, 'tenant') and request.tenant.schema_name != 'public':
        try:
            profile = CompanyProfile.objects.get(id=1)
        except CompanyProfile.DoesNotExist:
            # Profile doesn't exist yet (e.g., fresh signup)
            profile = None
    
    return {'profile': profile}
