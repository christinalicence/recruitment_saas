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
