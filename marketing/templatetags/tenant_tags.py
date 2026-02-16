from django import template
from django.urls import reverse, NoReverseMatch
from django.conf import settings

register = template.Library()

@register.simple_tag(takes_context=True)
def public_url(context, view_name):
    request = context.get('request')
    if not request:
        return ''

    # 1. Clean the view name (handles 'about' or 'public_marketing:about')
    base_view_name = view_name.split(':')[-1]
    
    # 2. Try the "Normal" way first (if we are currently on the public site)
    if hasattr(request, 'tenant') and request.tenant.schema_name == 'public':
        try:
            # Try without the namespace first
            return reverse(base_view_name)
        except NoReverseMatch:
            try:
                return reverse(f'public_marketing:{base_view_name}')
            except NoReverseMatch:
                return f"/{base_view_name}/"

    # 3. The "Resilient" Fallback (If we're on a tenant or resolver fails)
    paths = {
        'landing': '/',
        'about': '/about/',
        'template_select': '/choose-template/',
        'tenant_signup': '/signup/',
        'portal_finder': '/find-portal/',
        'template_preview': '/preview/',
    }
    
    path = paths.get(base_view_name, '/')
    
    # Logic to find the base domain (e.g., getpillarpost.com)
    host = request.get_host().split(':')[0] 
    parts = host.split('.')
    
    # If on agency.getpillarpost.com, parts[-2:] gives ['getpillarpost', 'com']
    if len(parts) >= 2:
        base_domain = '.'.join(parts[-2:])
    else:
        base_domain = host

    # Force HTTPS in production, follow request in local dev
    protocol = 'https' if not settings.DEBUG or request.is_secure() else 'http'
    
    return f"{protocol}://{base_domain}{path}"