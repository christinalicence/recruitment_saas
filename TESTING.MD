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
