import os
from django.db import connection, transaction
from django.utils.text import slugify
from django_tenants.utils import schema_context
from customers.models import Client, Domain, Plan
from django.contrib.auth import get_user_model

class TenantService:
    @staticmethod
    def create_onboarding_tenant(company_name, admin_email, password, template_id='executive'):
        admin_email = admin_email.lower().strip() 
        tenant_slug = slugify(company_name)
        domain_name = f"{tenant_slug}.getpillarpost.com"
        schema_name = tenant_slug.replace('-', '_')

        try:
            connection.set_schema_to_public() 
            
            # Re-checking Stripe logic: pulls from env as before
            stripe_id = os.getenv('price_id_standard')
            standard_plan, _ = Plan.objects.get_or_create(
                name="Standard",
                defaults={'stripe_price_id': stripe_id}
            )
            
            # STEP A: Create records in Public. 
            # We keep this atomic to ensure Client + Domain exist together
            with transaction.atomic(using='default'):
                tenant = Client.objects.create(
                    schema_name=schema_name,
                    name=company_name,
                    template_choice=template_id,
                    plan=standard_plan,
                    notification_email_1=admin_email,
                    master_email=admin_email,
                    is_active=False 
                )

                Domain.objects.create(
                    domain=domain_name,
                    tenant=tenant,
                    is_primary=True
                )

            # STEP B: Manual Schema Creation.
            # This is OUTSIDE the atomic block to prevent the "Pending Trigger" lock.
            # This requires 'auto_create_schema = False' in models.py.
            tenant.create_schema(check_if_exists=True, verbosity=1)

            # STEP C: Create User in the new schema
            with schema_context(tenant.schema_name):
                User = get_user_model()
                if not User.objects.filter(email=admin_email).exists():
                    User.objects.create_user(
                        username=admin_email,
                        email=admin_email,
                        password=password,
                        is_active=True
                    )

            return tenant, domain_name

        except Exception as e:
            connection.set_schema_to_public()
            # If the schema was created but User creation failed, we nuke it
            with connection.cursor() as cursor:
                cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
            print(f"Cleanup successful after error: {e}")
            return None, None