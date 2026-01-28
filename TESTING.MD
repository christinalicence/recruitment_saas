Django Tenants means slightly different commands 
# First time only - creates the test DB
python manage.py test --keepdb

# Every subsequent run - reuses the DB, super fast
python manage.py test --keepdb

# If things get weird and you need a fresh DB
python manage.py test --keepdb --noinput


tests are quite slow because a whole test db and schemas are created

Automated tests -
 - Onboarding - tests that a client is created during sign in (vital for app to function for new clients)
 - Isolation - very important for gdpr and security. Means one tenant can never accidentally access another tenant's info.

Test Files are structured so that they are all in the app they are testing. Some code (for creating, deleting and editing test databases) is stored in a seperate file (customers/tests/__init__.py) and called when needed. This is to make it easier to isolate the correct tests.

To test locally you need to specify the port so that django can create the subdomains for new tenants. The correct command is 
python3 manage.py runserver localhost:8000

Main Landing Page	http://localhost:8000
Tenant Login Page	http://test-company.localhost:8000/dashboard/

These are test links when run locally.

For cleaning up db
from customers.models import Client
# Delete all clients except the one named 'public'
Client.objects.exclude(schema_name='public').delete()

# List the clients in the db
for tenant in Client.objects.all():
    print(f"Name: {tenant.name} | Schema: {tenant.schema_name}")

python manage.py flush - deletes everyone inc superuser