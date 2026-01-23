from cms.models import CompanyProfile


def tenant_profile(request):
    """Make the tenant's profile available in all templates."""
    profile = None
    # Only fetch profile for tenant-specific requests (not public schema)
    if hasattr(request, 'tenant') and request.tenant.schema_name != 'public':
        # Fetch the first profile available in this tenant's isolated schema
        profile = CompanyProfile.objects.first()
    return {'profile': profile}
