from django.utils.text import slugify
from django_tenants.utils import schema_context
from django.core.management import call_command
from customers.models import Client, Domain, Plan
from django.contrib.auth.models import User

class TenantService:
    @staticmethod
    def create_onboarding_tenant(company_name, admin_email, password, template_id='executive'):
        tenant_slug = slugify(company_name)
        domain_name = f"{tenant_slug}.getpillarpost.com"
        schema_name = tenant_slug.replace('-', '_')

        if Domain.objects.filter(domain=domain_name).exists():
            return None, domain_name

        standard_plan, _ = Plan.objects.get_or_create(name="Standard")

        tenant = Client.objects.create(
            schema_name=schema_name,
            name=company_name,
            template_choice=template_id,
            plan=standard_plan,
            notification_email_1=admin_email,
            is_active=True
        )

        Domain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)

        # Move into the new tenant's schema
        with schema_context(tenant.schema_name):
            # 1. Run migrations to create the User table
            call_command('migrate', verbosity=0, interactive=False)
            
            # 2. Create the user explicitly
            new_user = User.objects.create_user(
                username=admin_email, # Use email as username for consistency
                email=admin_email,
                password=password
            )
            new_user.is_active = True
            new_user.save() # Explicitly save to ensure it hits the DB

        return tenant, domain_name