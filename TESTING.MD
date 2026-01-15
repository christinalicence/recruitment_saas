Django Tenants means slightly different commands 
# First time only - creates the test DB
python manage.py test --keepdb

# Every subsequent run - reuses the DB, super fast
python manage.py test --keepdb

# If things get weird and you need a fresh DB
python manage.py test --keepdb --noinput

# For testing with django-tenants, create a separate test database configuration
if "test" in sys.argv:
    # Parse your existing DB_URL but use a different database name for tests
    test_db_config = dj_database_url.parse(
        os.environ["DB_URL"],
        conn_max_age=600,
        ssl_require=True,
    )
    # Change just the database name to a test database
    test_db_config["NAME"] = "test_recruit_saas"
    test_db_config["ENGINE"] = "django_tenants.postgresql_backend"
    DATABASES = {
        "default": {
            **test_db_config,
            "TEST": {
                "NAME": "test_recruit_saas",
            }
        }
    }
    # Force close connections to avoid stalling
    DATABASES["default"]["CONN_MAX_AGE"] = 0

tests are quite slow because a whole test db and schemas are created

Automated tests -
 - Onboarding - tests that a client is created during sign in (vital for app to function for new clients)
 - Isolation - very important for gdpr and security. Means one tenant can never accidentally access another tenant's info.

Test Files are structured so that they are all in the app they are testing. Some code (for creating, deleting and editing test databases) is stored in a seperate file (customers/tests/__init__.py) and called when needed. This is to make it easier to isolate the correct tests.

To run the site locally with the subdomains they need to be added using these commands (on mac)
sudo nano /etc/hosts
127.0.0.1 sterling-search.localhost (testing one)
127.0.0.1 test-co.localhost