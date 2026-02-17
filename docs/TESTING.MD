# Testing

## Testing Objectives Against User Stories

## Manual Testing

### Code Validators

#### HTML Validator

#### CSS VAlidator

#### Javascript Linter

#### Python Standards

### Features Testing

### Responsiveness

### Accessibility

#### Lighthouse

#### Wave

### User Testing

The first round of user testing found a few bugs. 

- If you had an error during sign up it would fail silently

- If you visited a tenant's live page and tried to open a job advert to see the detail you got a 404 error.

It also uncovered a frustration with the sign up process because you entered your details to create your account, but the login page that followed (while being integral to how the site works because it routes to the subdomain) was annoying because you had to reenter all your details.

## Automated Testing

### Django Testing

I have tried to be as thorough as possible with automated testing, mainly to future proof the site. I ran in to lots of issues with the domain routing which meant that tests were harder to write, but through persistance I am happy with the coverage.

### Jest Testing

## Test Driven Development

I found this far more challenging with the subdomain environment and found that I was rewriting my tests often through the development process, but I do find this a valuable tool in terms of understanding my code and seeing potential future issues with it. 

A bug that I encountered when testing was persistent database issues - the tests couldn't run because the databases already existed, Django tries to clean the database automatically before each test run if this happens, but I kept being told there was an active user on the database and deleting it was impossible. This turned out to be an issue with having my Neon Postgres DB pooled, which means that it keeps connections open. When I changed it to unpooled this issue was fixed.
 

For cleaning up db
from customers.models import Client
# Delete all clients except the one named 'public'
Client.objects.exclude(schema_name='public').delete()

# List the clients in the db
for tenant in Client.objects.all():
    print(f"Name: {tenant.name} | Schema: {tenant.schema_name}")

python manage.py flush - deletes everyone inc superuser
python3 manage.py createsuperuser

# Import from the 'customers' app (or wherever your Tenant model lives)
from customers.models import Client, Domain

# 1. Create the public tenant
# Note: Ensure the model name is 'Client' or 'Tenant' based on your code
tenant = Client(schema_name='public', name='Public Tenant')
tenant.save()

# 2. Add the domain so Django knows how to route to it
# If you are developing locally, use 'localhost'
domain = Domain(domain='localhost', tenant=tenant, is_primary=True)
domain.save()


There are issues with testing locally and when deployed caused by the movements bewteen subdomains. The tests written for local dev are often not compatbile


The testing ethos is to do as much as possible with automated tests. This is to guarantee data security, which is vital for the site, and to future proof it.

I tried to use test driven development, but came across some herdals with this. The biggest one is the multi tenant environment. I found myself writing tests that I knew would break when I deployed. I was hesitent to do too much of the development work on the deployed site because I was experimenting a lot with different css combinations and I didn't want my github repo to be too cluttered.

# Automated Testing

# Manual Testing

# User Testing