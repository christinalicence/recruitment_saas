from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def public_url(context, view_name):
    """Generate a URL to the public domain from a tenant subdomain"""
    request = context['request']
    
    # Strip the namespace if it exists to look up the path in our dictionary
    # This handles both 'about' and 'public_marketing:about'
    base_view_name = view_name.split(':')[-1]
    
    # Ensure we have the full namespaced name for the reverse() function
    full_view_name = f'public_marketing:{base_view_name}'
    
    # If we're already on public, just use the normal URL reverse
    if request.tenant.schema_name == 'public':
        return reverse(full_view_name)
    
    # If we're on a tenant, construct the public URL manually
    host = request.get_host()
    
    # Logic to extract the base domain
    parts = host.split('.')
    if len(parts) > 2:
        base_domain = '.'.join(parts[1:])
    else:
        base_domain = host
    
    protocol = 'https' if request.is_secure() else 'http'
    
    # Map the base view names to their URL paths
    paths = {
        'landing': '/',
        'about': '/about/',
        'template_select': '/choose-template/',
        'tenant_signup': '/signup/',
    }
    
    path = paths.get(base_view_name, '/')
    return f"{protocol}://{base_domain}{path}"