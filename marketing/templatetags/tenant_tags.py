from django import template
from django.urls import reverse, set_urlconf, get_urlconf
from django.conf import settings

register = template.Library()\


# Custom template tag to generate URLs using the public schema's URL configuration.


@register.simple_tag
def public_url(view_name, *args, **kwargs):
    current_urlconf = get_urlconf()
    try:
        set_urlconf(settings.PUBLIC_SCHEMA_URLCONF)
        return reverse(view_name, args=args, kwargs=kwargs)
    finally:
        set_urlconf(current_urlconf)

