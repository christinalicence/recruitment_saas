# Pillar and Post

## Concept of Website

This site is built for people launching their recruitment businesses who want a low cost, but still professional looking site. Although there are many companies out there that allow people to build their own sites eg Wix, Squarespace etc I found that none of them were designed for recruiters. They want to be able to post job adverts that are easily updateable, but this was a difficult task in all the sites I tested. Recruitment companies are often launched by people working on their own and they build on a few industry relationships to grow. This is talked about in this https://www.recruiter.co.uk/depth/2025/07/flying-solo "there were 31,247 recruitment enterprises in the UK at the start of 2024, with micro businesses (those with fewer than 10 employees) accounting for 78.6% of the workforce"

Pillar and Post is here to provide for those people, who often don't want to spend much money, but want something credible to share with their clients and candidates.

The site allows them to sign up, then they can choose from 3 templates to build their recruitment sites on. Each template has 3 pages, Home, About Us and Jobs. They can change colours, text and pictures on the templates.

Data and keeping data safe is really important to recruitment businesses because they are subject to GDPR audits. The site is deisgned to save as little data as possible. The candidates data is not saved when they apply to a job, just shared to 2 different email address the client adds. Payments are handled by Stripe, so no data is saved their either.

### User Stories

A recruiter wants to set up a site to build a business working with city banks. 
 - different templates

A recruiter wants to be able to include their brand colours
 - colour picker

A recruiter wants to be able to include their own fonts
 - font changer (not built yet)

A recruiter wants to be able to change their jobs while on the go
- easy jobs upload, mobile friendly

A recruiter wants to be able to build trust by including photos of themselves
- About and hero image options

A recruiter is budget concious and wants to be able to test options without paying immediately
- 14 day free trial

A recruiter wants to be able to use their own domain address

A recruiter needs to be able to list their data and privacy policies
 - this is for a future release

A recruiter wants to update 20 jobs
 - a premium tier, for future release

## Aesthetic Design

The nature of this site means that there tangibly different design aesthetics involved, one for the marketing site for Pillar and Post and 3 different ones for the 3 different tenant themes.

The marketing site is designed to be trustworthy, conservative and give the idea of a solid foundations. I've used understated colours and fonts and included photos of buildings, going for the pillar and post theme.

## Technical Design 

## Technologies used, and why

### Django Tenants

To allow companies to use their own subdomains. Eventually, if the site goes live they should be able to transfer these to bespoke domains.

It is also secure because it holds data in different schemas, meaning that leaks between different clients are less likely. Recruitment companies are very data concious because they need to be able to show they are GDPR compliant legally.

### Stripe

Selected because they handle all of payment, including sensitive data.

### Cloudfayre

The domain www.getpillarpost.com was purchased through Couldfayre because they provide good valur for domains. They are also use a domain licensing system that makes the subdomains quite simple and immediately able to use. Heroku does have this option, but at a far more expensive tier.

I needed to buy a domain for this project becuase deploying via a heroku domain wouldn't support the subdomains.

### Cloudinary

Cloudinary is used to store all pictures, both on the marketing site and ones that clients upload.
Selected because their resizing is user firendly, although there are size limits written in to this project for images to stop storage getting too filled up and keep things running smoothly.

### Neon for Postgres DB        

This is set up on the free tier, Django Tenants doesn't work with SQL Lite, so I needed to set up a compatible database.

### Email Provider


Everything else is listed in my requirements.txt


## User Flows

## Features

### Email Portal Finder
This feature is on the landing page of the marketing site. If someone is already a user it allows them to be redirected to the correct subdomain for them to log in to their site. The clients will also be emailed this subdomian when they sign up

### Billings and Payments

### Site Editor

#### Template Changer
There is a choice of 3 templates, with distinctly different looks.

#### Colour Picker, with contrast checker
This is written using a javascript function and a ratio

#### Image Uploaders
There are 2 image uploaders, for the hero image on the home page and the about us image on the about page.

#### Text inputters 
There are various text inputters, which adjust the live site when you press save

#### Job updater
This is a key feature and the selling point for the site. It is simple to use, and allows the user to enter up to 6 jobs on the standard payment tier.

#### Live site viewer
This opens the client's live site on the P&P subdomain in a new tab, so they don't lose their place on the dashboard.

## Data Design

A key point in the ethos of the site is to retain as little data as possible.

Things we need are customer data - the data about who they are, and the data about the sites they have designed.





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

Seperate base.html and css files for the marketing site, the dashboard/editor and the tenant sites. This keeps the files cleaner and stops them trying to link to other subdomains in the navbar causing 403 issues.

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


Photo credits

unsplash.com
'executive': 'Photo by <a href="https://unsplash.com/@alesiaskaz?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Alesia Kazantceva</a> on <a href="https://unsplash.com/photos/turned-off-laptop-computer-on-top-of-brown-wooden-table-VWcPlbHglYc?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
      
'startup': 'Photo by <a href="https://unsplash.com/@suryadhityas?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Suryadhityas</a> on <a href="https://unsplash.com/photos/a-room-filled-with-lots-of-desks-and-computers-NrDZJ9oWV_Y?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
      
'boutique': Image by <a href="https://pixabay.com/users/pexels-2286921/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=2181960">Pexels</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=2181960">Pixabay</a>


About us preview Image by <a href="https://pixabay.com/users/markusspiske-670330/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=581131">Markus Spiske</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=581131">Pixabay</a>

hero image Photo by <a href="https://unsplash.com/@cecilecos?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Cécile</a> on <a href="https://unsplash.com/photos/a-black-and-white-photo-of-a-wall-VgyM77QmzHo?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
      
About us P&P Photo by <a href="https://unsplash.com/@albrb?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Alejandro Barba</a> on <a href="https://unsplash.com/photos/grayscale-photo-of-concrete-building-L6lqXDt_WuI?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>

default about us Photo by <a href="https://unsplash.com/@essentialprints?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">James Healy</a> on <a href="https://unsplash.com/photos/aim-high-fly-higher-photo-frame-WZ-YnvCCLug?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
      