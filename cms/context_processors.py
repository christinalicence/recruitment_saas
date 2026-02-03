from cms.models import CompanyProfile


def tenant_profile(request):
    profile = None
    if hasattr(request, 'tenant') and request.tenant.schema_name != 'public':
        # Search for the profile belonging to this specific tenant slug
        profile = CompanyProfile.objects.filter(tenant_slug=request.tenant.schema_name).first()
        
    return {
        'profile': profile,
        'tenant': request.tenant if hasattr(request, 'tenant') else None
    }
