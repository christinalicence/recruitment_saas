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

A recruiter wants to be able to upload their jobs frequently because they work in a fast turn around market
- easy upload, template save later feature

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

### Colour Pallette

### Font Choices

### Wireframes

## Technical Design 

## Technologies used, and why

### Django Tenants

To allow companies to use their own subdomains. Eventually, if the site goes live they should be able to transfer these to bespoke domains.

It is also secure because it holds data in different schemas, meaning that leaks between different clients are less likely. Recruitment companies are very data concious because they need to be able to show they are GDPR compliant legally.

There are quite a lot of 'quirks' in the coding, things that help this system work. These are marked with notes in the code to stop accidental deletions in the future.

### Stripe

Selected because they handle all of payment, including sensitive data. It handles the subscriptions automatically. 

### Cloudfayre

The domain www.getpillarpost.com was purchased through Couldfayre because they provide good valur for domains. They are also use a domain licensing system that makes the subdomains quite simple and immediately able to use. Heroku does have this option, but at a far more expensive tier.

I needed to buy a domain for this project becuase deploying via a heroku domain wouldn't support the subdomains.

### Cloudinary

Cloudinary is used to store all pictures, both on the marketing site and ones that clients upload.
Selected because their resizing is user firendly, although there are size limits written in to this project for images to stop storage getting too filled up and keep things running smoothly.

### Neon for Postgres DB        

This is set up on the free tier, Django Tenants doesn't work with SQL Lite, so I needed to set up a compatible database.

### Brevo for Email Provider

Chosen because they have a good free tier (300 emails per day) and integrates well with heroku. It is used to send emails on sign up including the user's unique subdomain and emails related to payments. This has been combined with Zoho to run the inbox for hello@getpillarpost.com using a free tier.

### Celery? 

This allows different tasks to happen at the same time instead of waiting for server responses before continuing, speeding up the signup process.


Everything else is listed in my requirements.txt


## User Journeys

User Flow (not signed up)
- Landing Page
- Choose a template
- Preview (to draw them in)
- Sign Up (enter info to generate site, the form is in the style of the chosen template)
- Sign in (not ideal for UX, but transfers to subdomain)
- Dashboard

User Flow (signed up, going to their unique domain)
- Login
- Dashboard


## Features

### Email Portal Finder
This feature is on the landing page of the marketing site. If someone is already a user it allows them to be redirected to the correct subdomain for them to log in to their site. The clients will also be emailed this subdomian when they sign up

### Client's Dashboard

This is on each client's unquie subdomain. It allows them to manage their websites, jobs and subscriptions. The client's don't have seperate admin access created for them on sign up, everything is managed from here.

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

#### Job Editor
This is a key feature and the selling point for the site. It is simple to use, and allows the user to enter up to 6 jobs on the standard payment tier.

This part of the site allows the users to upload their current job adverts.

#### Live site viewer
This opens the client's live site on the P&P subdomain in a new tab, so they don't lose their place on the dashboard.

### Email Send features 
Emails are sent when people signup, which includes there unique url for login. Emails are also sent when subscriptions are set up or payments fail.

### A note on file setup.

Making a multi tenant app means that the file setup is a bit different from standard Django. There are 3 base.html files - 1 standard one for the marketing site, 1 dashboard one for when a tenant is signed and 1 tenant one for the sites they design. The CSS files mirror this set up and they are stored in the appropriate Django Apps. There are 3 apps - marketing (for the marketing site), CMS which handles everything for the clients when they are logged in and the customers app, which handles payment and management info. This is for the owner of P&P to use.

## Data Design

A key point in the ethos of the site is to retain as little data as possible.

Things we need are customer data - the data about who they are, and the data about the sites they have designed.


## Persistant Bugs and Challenged

### 404s caused by multitenancy




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


## Credits, Articles and Blogs

https://testdriven.io/blog/django-multi-tenant/
https://django-tenants.readthedocs.io/en/latest/install.html 
https://github.com/django-tenants/django-tenants/issues/28 
https://pypi.org/project/Django-Subdomain-Middleware/
https://lincolnloop.com/blog/user-generated-themes-django-css/
https://www.youtube.com/watch?v=_wefsc8X5VQ


## Photo credits

unsplash.com
'executive': 'Photo by <a href="https://unsplash.com/@alesiaskaz?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Alesia Kazantceva</a> on <a href="https://unsplash.com/photos/turned-off-laptop-computer-on-top-of-brown-wooden-table-VWcPlbHglYc?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
      
'startup': 'Photo by <a href="https://unsplash.com/@suryadhityas?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Suryadhityas</a> on <a href="https://unsplash.com/photos/a-room-filled-with-lots-of-desks-and-computers-NrDZJ9oWV_Y?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
      
'boutique': Image by <a href="https://pixabay.com/users/pexels-2286921/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=2181960">Pexels</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=2181960">Pixabay</a>


About us preview Image by <a href="https://pixabay.com/users/markusspiske-670330/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=581131">Markus Spiske</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=581131">Pixabay</a>

hero image Photo by <a href="https://unsplash.com/@cecilecos?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Cécile</a> on <a href="https://unsplash.com/photos/a-black-and-white-photo-of-a-wall-VgyM77QmzHo?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
      
About us P&P Photo by <a href="https://unsplash.com/@albrb?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Alejandro Barba</a> on <a href="https://unsplash.com/photos/grayscale-photo-of-concrete-building-L6lqXDt_WuI?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>

default about us Photo by <a href="https://unsplash.com/@essentialprints?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">James Healy</a> on <a href="https://unsplash.com/photos/aim-high-fly-higher-photo-frame-WZ-YnvCCLug?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
      


## Notes on Development

I tried to approach this project with a 'real world' mindset, so I have tried to write the documentation and notes in the code in such a way that other developers could use it to work on the project. This is a more complex tech stack than I have used before, with more 'moving parts' - pressing the wrong button or deleting the wron bit of code can cause lots of problems! Therefore notes have had to be better.

Using a multidomain site bought challenges I hadn't necessarily anticipated, such as having to buy a domain because Heroku doesn't support this type of set up. 

I also changed my thinking on aesthetics quite seriously from the beginning of development to the end, this was to make the tenant themes more tangibly different when you viewed them. I feel that this is something experience will help with, being able to picture the design concept better when it is actually developed.