# marketing/views.py
from django.shortcuts import render, redirect
from datetime import date, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django_tenants.utils import schema_context
from customers.models import Client, Domain
from .forms import TenantSignupForm, TenantLoginForm


def tenant_signup(request):
    form = TenantSignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        subdomain = form.cleaned_data["subdomain"]
        company_name = form.cleaned_data["company_name"]
        admin_email = form.cleaned_data["admin_email"]
        password = form.cleaned_data["password"]

        if Client.objects.filter(schema_name=subdomain).exists():
            form.add_error("subdomain", "This subdomain is already taken")
        else:
            tenant = Client.objects.create(
                schema_name=subdomain,
                name=company_name,
                paid_until=date.today() + timedelta(days=14),
                on_trial=True,
            )

            Domain.objects.create(
                domain=f"{subdomain}.localhost",
                tenant=tenant,
                is_primary=True,
            )

            with schema_context(tenant.schema_name):
                User.objects.create_user(
                    username=admin_email,
                    email=admin_email,
                    password=password
                )

            current_host = request.get_host()
            if ":" in current_host:
                port = current_host.split(":")[-1]
                redirect_url = f"http://{subdomain}.localhost:{port}/login/"
            else:
                redirect_url = f"http://{subdomain}.localhost/login/"

            return redirect(redirect_url)

    return render(request, "marketing/signup.html", {"form": form})


@login_required
def tenant_dashboard(request):
    return render(
        request, 
        "marketing/dashboard.html",
        {"tenant_name": request.tenant.name}
    )


def tenant_login(request):
    form = TenantLoginForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user:
            login(request, user)
            return redirect("marketing:tenant_dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "marketing/login.html", {"form": form})


def tenant_logout(request):
    logout(request)
    return redirect("marketing:tenant_login")


def landing_page(request):
    """Renders the Pillar & Post public landing page."""
    return render(request, "marketing/landing.html")