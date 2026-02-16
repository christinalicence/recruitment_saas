from django.utils.text import slugify
from django_tenants.utils import schema_context
from django.contrib.auth.models import User
from customers.models import Client, Domain, Plan

class TenantService:
    @staticmethod
    def create_onboarding_tenant(company_name, admin_email, password, template_id='executive'):
        """
        Industry standard service for atomic tenant provisioning.
        """
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

        with schema_context(tenant.schema_name):
            User.objects.create_user(
                username=admin_email,
                email=admin_email,
                password=password
            )
        
        return tenant, domain_name