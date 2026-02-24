from cms.models import CompanyProfile


# Context processor to make tenant-specific profile data available in all templates.
def tenant_profile(request):
    profile = None
    if hasattr(request, 'tenant') and request.tenant.schema_name != 'public':
        profile = CompanyProfile.objects.filter(tenant_slug=request.tenant.schema_name).first()
    return {
        'profile': profile,
        'tenant': request.tenant if hasattr(request, 'tenant') else None
    }
