from django.contrib import admin
from .models import Client, Domain, Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "max_jobs")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "plan", "trial_ends", "is_active", "schema_name")
    search_fields = ("name", "schema_name")

 
@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")