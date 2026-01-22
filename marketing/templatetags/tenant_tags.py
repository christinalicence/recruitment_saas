from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def public_url(context, view_name):
    """Generate a URL to the public domain from a tenant subdomain"""
    request = context['request']
    
    # If we're already on public, just use the normal URL
    if request.tenant.schema_name == 'public':
        from django.urls import reverse
        return reverse(f'public_marketing:{view_name}')
    
    # If we're on a tenant, construct the public URL
    host = request.get_host()
    
    # Remove subdomain to get base domain
    parts = host.split('.')
    if len(parts) > 2:
        # Has subdomain, remove it
        base_domain = '.'.join(parts[1:])
    else:
        # No subdomain (e.g., "localhost:8000")
        base_domain = host
    
    protocol = 'https' if request.is_secure() else 'http'
    
    # Map view names to paths
    paths = {
        'landing': '/',
        'about': '/about/',
        'template_select': '/choose-template/',
    }
    
    path = paths.get(view_name, '/')
    return f"{protocol}://{base_domain}{path}"