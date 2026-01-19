# recruitment_saas

Django tenants - keeps data seperate, tidy. Must use PostgreSQL, set up using Neon. Built using subdomains on tenants because it keeps cookies and data completely seperate, rather than folders which is an option. 

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
Getting a 404 error when trying to hit a subdomain, because django's middleware didn't use the correct url file (it kept hitting the one at the root rather than the one in the marketing app)