from django.shortcuts import render, redirect
from datetime import date, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django_tenants.utils import schema_context
from customers.models import Client, Domain
from .forms import TenantSignupForm, TenantLoginForm


def tenant_signup(request):
    form = TenantSignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        company_name = form.cleaned_data["company_name"]
        subdomain = form.cleaned_data["subdomain"]
        admin_email = form.cleaned_data["admin_email"]

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
                user = User.objects.create(
                    username=admin_email,   # use email as username
                    email=admin_email,
                    is_staff=True,
                    is_superuser=False,
                    password=make_password(form.cleaned_data["password"]),
                )

            return redirect(f"http://{subdomain}.localhost:8000/login/")

    return render(request, "marketing/signup.html", {"form": form})


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
            return redirect("tenant_dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "marketing/login.html", {"form": form})


@login_required
def tenant_dashboard(request):
    tenant = request.tenant

    return render(
        request,
        "marketing/dashboard.html",
        {"tenant_name": request.tenant.name},
    )


def tenant_logout(request):
    logout(request)
    return redirect("tenant_login")
