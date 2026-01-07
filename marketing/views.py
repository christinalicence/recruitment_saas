from django.shortcuts import render, redirect
from .forms import TenantSignupForm
from customers.models import Client, Domain
from django_tenants.utils import schema_context
from django.contrib.auth.models import User
from datetime import date, timedelta

def tenant_signup(request):
    if request.method == "POST":
        form = TenantSignupForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data["company_name"]
            subdomain = form.cleaned_data["subdomain"]
            admin_email = form.cleaned_data["admin_email"]

            # Create tenant
            TRIAL_DAYS = 14
            tenant = Client(
                schema_name=subdomain,
                name=company_name,
                paid_until=date.today() + timedelta(days=TRIAL_DAYS),
                on_trial=True,
            )
            tenant.save()

            # Create default domain for tenant
            Domain.objects.create(
                domain=f"{subdomain}.localhost",
                tenant=tenant,
                is_primary=True
            )

            # Create admin user for tenant
            with schema_context(tenant.schema_name):
                User.objects.create_superuser(
                    username="admin",
                    email=admin_email,
                    password="password123"
                )

            # Redirect to the tenant's admin
            return redirect(f"http://{subdomain}.localhost:8000/admin/")
    else:
        form = TenantSignupForm()

    return render(request, "marketing/signup.html", {"form": form})
