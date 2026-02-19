from django.db import connection 
from django.utils.text import slugify
from django_tenants.utils import schema_context
from django.core.management import call_command
from customers.models import Client, Domain, Plan
from django.contrib.auth import get_user_model

class TenantService:
    @staticmethod
    def create_onboarding_tenant(company_name, admin_email, password, template_id='executive'):
        tenant_slug = slugify(company_name)
        domain_name = f"{tenant_slug}.getpillarpost.com"
        schema_name = tenant_slug.replace('-', '_')

        print(f"\n[DEBUG] Starting onboarding for: {company_name}")
        print(f"[DEBUG] Target Schema: {schema_name} | Target Domain: {domain_name}")

        if Domain.objects.filter(domain=domain_name).exists():
            print(f"[DEBUG] Domain {domain_name} already exists. Aborting.")
            return None, domain_name

        tenant = None
        try:
            # 1. Create Tenant and Domain records in Public
            connection.set_schema_to_public() 
            print("[DEBUG] Current Schema: PUBLIC. Creating Client and Domain records...")
            
            standard_plan, _ = Plan.objects.get_or_create(name="Standard")
            tenant = Client.objects.create(
                schema_name=schema_name,
                name=company_name,
                template_choice=template_id,
                plan=standard_plan,
                notification_email_1=admin_email,
                is_active=False

            )
            Domain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)
            print(f"[DEBUG] Base records created for tenant ID: {tenant.id}")

            # 2. Run Migrations
            with schema_context(tenant.schema_name):
                print(f"[DEBUG] Switched to context: {tenant.schema_name}. Running migrations...")
                call_command('migrate', verbosity=0, interactive=False)
                print(f"[DEBUG] Migrations completed for {tenant.schema_name}")
            
            # 3. Reset Connection
            print("[DEBUG] Closing database connection to refresh table metadata...")
            connection.close() 

            # 4. Create the User
            with schema_context(tenant.schema_name):
                print(f"[DEBUG] Re-entering context: {tenant.schema_name} to create user.")
                User = get_user_model()
                
                # Check if user already exists in this schema
                if not User.objects.filter(email=admin_email).exists():
                    user = User.objects.create_user(
                        username=admin_email,
                        email=admin_email,
                        password=password,
                        is_active=True
                    )
                    print(f"[DEBUG] SUCCESS: User {user.email} created in schema {tenant.schema_name}")
                else:
                    print(f"[DEBUG] User {admin_email} already existed in this schema.")

            return tenant, domain_name

        except Exception as e:
            print(f"[DEBUG] ERROR encountered: {str(e)}")
            connection.set_schema_to_public()
            if tenant:
                print(f"[DEBUG] Cleaning up failed tenant: {schema_name}")
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
                tenant.delete()
            return None, None