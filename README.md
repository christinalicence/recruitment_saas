# recruitment_saas

Django tenants - keeps data seperate, tidy. Must use PostgreSQL, set up using Neon. Built using subdomains on tenants because it keeps cookies and data completely seperate, rather than folders which is an option. 

Using 1 shared db, but seperate schema's per client. This is GDPR compliant

User is created on signup with 14 day trial
        (need to improve password for new users)

Each tenant has a dashboard and no access to django admin to keep things secure and prevent them causing issues.

Crispy forms, using Bootstrap 5, used for ease.

User Flow (not signed up)
- Landing Page
- Choose a template
- Preview (to draw them in)
- Sign Up (enter info to generate site, the form is in the style of the chosen template)
- See site
- Dashboard

User Flow (signed up)
- Landing Page
- Dashboard

Persistant Bug
Getting a 404 error when trying to hit a subdomain, because django's middleware didn't use the correct url file (it kept hitting the one at the root rather than the one in the marketing app). Solved locally through adapting some bespoke middleware code. This is likely to need more attention during deployment.

Another subdomain issue is getting 403 errors when trying to get to the dashboard/properly looged on. This has been solved in local dev with the settings look like 

# --- COOKIES & CSRF ---
# We comment these out for localhost development to avoid 403 errors.
# SESSION_COOKIE_DOMAIN = ".localhost"
# CSRF_COOKIE_DOMAIN = ".localhost"

# Ensure Django trusts the subdomain origins
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://*.localhost:8000",
]

# Security settings for local development
CSRF_COOKIE_HTTPONLY = False  # Allows Django's CSRF middleware to see it
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# middleware settings for cookies
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = 

But these do need changing when deployed to heroku.

Migrations

Need to be applied to tenant or public egs of commands
python3 manage.py makemigrations cms
python3 manage.py migrate_schemas --tenants
python3 manage.py migrate_schemas --shared

Dynamic CSS
- context processor acceses the settings in different html files, 
and dynamic branding js file needed to get this working with different browsers
marketing/templatetags - to help navbar links when inside tenants


Credits 

https://testdriven.io/blog/django-multi-tenant/
https://django-tenants.readthedocs.io/en/latest/install.html 
https://github.com/django-tenants/django-tenants/issues/28 
https://pypi.org/project/Django-Subdomain-Middleware/
https://lincolnloop.com/blog/user-generated-themes-django-css/
https://www.youtube.com/watch?v=_wefsc8X5VQ
