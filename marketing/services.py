import os
from django.db import connection, transaction
from django.utils.text import slugify
from django_tenants.utils import schema_context
from customers.models import Client, Domain, Plan
from django.contrib.auth import get_user_model

class TenantService:
    @staticmethod
    def create_onboarding_tenant(company_name, admin_email, password, template_id='executive'):
        # Normalize email immediately to prevent search failures
        admin_email = admin_email.lower().strip() 
        tenant_slug = slugify(company_name)
        domain_name = f"{tenant_slug}.getpillarpost.com"
        schema_name = tenant_slug.replace('-', '_')

        tenant = None
        try:
            connection.set_schema_to_public() 
            stripe_id = os.getenv('price_id_standard')
            standard_plan, created = Plan.objects.get_or_create(
                name="Standard",
                defaults={'stripe_price_id': stripe_id}
            )
            
            # Use atomic to prevent ghost tenants if the user creation fails
            with transaction.atomic(using='default'):
                tenant = Client.objects.create(
                    schema_name=schema_name,
                    name=company_name,
                    template_choice=template_id,
                    plan=standard_plan,
                    notification_email_1=admin_email, # Source for Portal Finder
                    master_email=admin_email,
                    is_active=False 
                )

                Domain.objects.create(
                    domain=domain_name,
                    tenant=tenant,
                    is_primary=True
                )

                with schema_context(tenant.schema_name):
                    User = get_user_model()
                    if not User.objects.filter(email=admin_email).exists():
                        User.objects.create_user(
                            username=admin_email, # Standardizing username as email
                            email=admin_email,
                            password=password,
                            is_active=True
                        )

            return tenant, domain_name

        except Exception as e:
            connection.set_schema_to_public()
            with connection.cursor() as cursor:
                cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
            print(f"Cleanup successful after error: {e}")
            return None, None