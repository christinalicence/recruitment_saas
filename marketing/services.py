import os
from django.db import connection 
from django.utils.text import slugify
from django_tenants.utils import schema_context
from customers.models import Client, Domain, Plan
from django.contrib.auth import get_user_model


class TenantService:
    @staticmethod
    def create_onboarding_tenant(company_name, admin_email, password, template_id='executive'):
        tenant_slug = slugify(company_name)
        domain_name = f"{tenant_slug}.getpillarpost.com"
        schema_name = tenant_slug.replace('-', '_')

        tenant = None
        try:
            # stripe bits
            connection.set_schema_to_public() 
            stripe_id = os.getenv('price_id_standard')
            standard_plan, created = Plan.objects.get_or_create(
                name="Standard",
                defaults={'stripe_price_id': stripe_id}
            )
            if not created and not standard_plan.stripe_price_id:
                standard_plan.stripe_price_id = stripe_id
                standard_plan.save()
            
            # --- subscription and tenant creation ---
            tenant = Client.objects.create(
                schema_name=schema_name,
                name=company_name,
                template_choice=template_id,
                plan=standard_plan,
                notification_email_1=admin_email,
                is_active=False 
            )

            # make domain in public schema
            Domain.objects.create(
                domain=domain_name,
                tenant=tenant,
                is_primary=True
            )

            # set to sctive now
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
            if tenant:
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
                tenant.delete()
            print(f"Error in onboarding: {e}")
            return None, None