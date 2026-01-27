from cms.models import CompanyProfile

def tenant_profile(request):
    """Make the tenant's profile available in all templates automatically."""
    profile = None
    # Ensure we are on a tenant site and not the main marketing site
    if hasattr(request, 'tenant') and request.tenant.schema_name != 'public':
        # Every tenant has exactly one profile (ID=1) created via views or signals
        profile = CompanyProfile.objects.filter(id=1).first()
        
    return {
        'profile': profile,
        'tenant': request.tenant if hasattr(request, 'tenant') else None
    }