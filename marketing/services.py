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
            # 1. Setup in Public Schema
            connection.set_schema_to_public() 
            stripe_id = os.getenv('price_id_standard')
            standard_plan, _ = Plan.objects.get_or_create(
                name="Standard",
                defaults={'stripe_price_id': stripe_id}
            )
            
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

            tenant.create_schema(check_if_exists=True, verbosity=1)
            
            with schema_context(tenant.schema_name):
                User = get_user_model()
                if not User.objects.filter(email=admin_email).exists():
                    User.objects.create_user(
                        username=admin_email,
                        email=admin_email,
                        password=password,
                        is_active=True
                    )
                
                # Branding Configurations (Restored)
                configs = {
                    'executive': {
                        'primary': '#0f172a',
                        'bg': '#ffffff',
                    },
                    'startup': {
                        'primary': '#4a5d5e',   
                        'bg': '#f0f4f4',         
                    },
                    'boutique': {
                        'primary': '#3f6212',
                        'bg': '#fafaf9',
                    }
                }
                vibe = configs.get(template_id, configs['executive'])

                from cms.models import CompanyProfile
                CompanyProfile.objects.update_or_create(
                    tenant_slug=schema_name,
                    defaults={
                        'display_name': company_name,
                        'primary_color': vibe['primary'],
                        'secondary_color': vibe['primary'],
                        'background_color': vibe['bg'],
                        
                        'hero_title': "Connecting Exceptional Talent with World-Class Teams",
                        'hero_text': (
                            "We specialize in finding the perfect match between industry leaders "
                            "and top-tier professionals."
                        ),
                        
                        'homepage_body_text': (
                            "Whether you're a business looking for your next key hire or a professional ready for a new challenge, "
                            "we're here to make the right introduction. Our consultants bring deep sector knowledge and a "
                            "personal approach to every search, ensuring that we don't just fill roles, but build lasting "
                            "professional partnerships. By combining rigorous candidate screening with an intuitive understanding "
                            "of company culture, we help organizations scale with confidence while guiding talented individuals "
                            "toward the career-defining opportunities they deserve.\n\n"
                            "We believe that recruitment is about more than just matching a CV to a job description; "
                            "it is about recognizing potential and fostering growth. In today’s competitive landscape, "
                            "finding the right fit requires a partner who listens as much as they search. From the initial "
                            "consultation to the final placement, we remain committed to transparency, integrity, and the "
                            "long-term success of both our clients and our candidates."
                        ),
                        
                        'about_title': "Expertise. Integrity. Results.",
                        'about_content': "With over a decade of experience in specialized recruitment...",
                        'jobs_header_text': "Current Vacancies",
                    }
                )

            return tenant, domain_name

        except Exception as e:
            connection.set_schema_to_public()
            with connection.cursor() as cursor:
                cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
            print(f"Cleanup successful after error: {e}")
            return None, None