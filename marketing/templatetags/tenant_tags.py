from django import template
from django.urls import reverse, NoReverseMatch
from django.conf import settings

register = template.Library()

@register.simple_tag(takes_context=True)
def public_url(context, view_name):
    request = context.get('request')
    if not request:
        return ''

    base_view_name = view_name.split(':')[-1]
    
    if hasattr(request, 'tenant') and request.tenant.schema_name == 'public':
        try:
            return reverse(f'public_marketing:{base_view_name}')
        except NoReverseMatch:
            try:
                return reverse(base_view_name)
            except NoReverseMatch:
                return f"/{base_view_name}/"

    paths = {
        'landing': '/',
        'about': '/about/',
        'template_select': '/choose-template/',
        'tenant_signup': '/signup/',
        'portal_finder': '/find-portal/',
        'template_preview': '/preview/',
    }
    
    path = paths.get(base_view_name, '/')
    
    host = request.get_host().split(':')[0] 
    parts = host.split('.')

    if len(parts) >= 2:
        base_domain = '.'.join(parts[-2:])
    else:
        base_domain = host

    protocol = 'https' if not settings.DEBUG or request.is_secure() else 'http'
    
    return f"{protocol}://{base_domain}{path}"