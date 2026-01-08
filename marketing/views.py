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

            # Prevent duplicate tenants
            if Client.objects.filter(schema_name=subdomain).exists():
                form.add_error("subdomain", "This subdomain is already taken")
                return render(request, "marketing/signup.html", {"form": form})

            # Create tenant
            tenant = Client.objects.create(
                schema_name=subdomain,
                name=company_name,
                paid_until=date.today() + timedelta(days=14),
                on_trial=True,
            )

            # Create domain
            Domain.objects.create(
                domain=f"{subdomain}.localhost",
                tenant=tenant,
                is_primary=True,
            )

            # Create tenant admin user safely (not Django superuser)
            with schema_context(tenant.schema_name):
                if not User.objects.filter(username="admin").exists():
                    User.objects.create_user(
                        username="admin",
                        email=admin_email,
                        password="password123",  # dev only
                    )

            # Redirect to tenant landing page (dashboard)
            return redirect(f"http://{subdomain}.localhost:8000/")

    else:
        form = TenantSignupForm()

    return render(request, "marketing/signup.html", {"form": form})


def tenant_dashboard(request):
    """
    Simple dashboard for tenants
    """
    tenant = getattr(request, "tenant", None) 
    context = {
        "tenant_name": tenant.name if tenant else "Your Company"
    }
    return render(request, "marketing/dashboard.html", context)
