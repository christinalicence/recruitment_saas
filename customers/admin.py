from django.contrib import admin
from django_tenants.utils import schema_context
from .models import Client, Domain, Plan
from cms.models import Job 

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "get_domain", "plan", "job_count", "trial_ends", "is_active", "schema_name")
    search_fields = ("name", "schema_name")

    def job_count(self, obj):
        """Hops into the tenant schema to count how many jobs they have posted."""
        if obj.schema_name == 'public':
            return "N/A"
        with schema_context(obj.schema_name):
            return Job.objects.count()
    job_count.short_description = "Jobs Posted"

    def get_domain(self, obj):
        """Retrieves the primary domain associated with the tenant."""
        domain_obj = obj.domains.filter(is_primary=True).first()
        return domain_obj.domain if domain_obj else "No Domain"
    get_domain.short_description = "Domain"