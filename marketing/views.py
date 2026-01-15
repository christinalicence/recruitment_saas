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
    template_id = request.GET.get('template', 'executive')
    initial_data = {'company_name': request.GET.get('company_name', '')}
    form = TenantSignupForm(request.POST or None, initial=initial_data)

    if request.method == "POST" and form.is_valid():
        # 1. Create Tenant (Model handles slugification)
        tenant = Client.objects.create(
            name=form.cleaned_data["company_name"],
            template_choice=template_id,
            on_trial=True,
            paid_until=date.today() + timedelta(days=14)
        )
        
        # 2. Create Domain
        Domain.objects.create(
            domain=f"{tenant.schema_name}.localhost",
            tenant=tenant,
            is_primary=True
        )

        # 3. Create Admin User in the new schema
        with schema_context(tenant.schema_name):
            User.objects.create_superuser(
                username=form.cleaned_data["admin_email"],
                email=form.cleaned_data["admin_email"],
                password=form.cleaned_data["password"]
            )

        # 4.Absolute URL with Port Handling
        subdomain = tenant.schema_name
        # Splitting host and port to handle local development vs production
        host_parts = request.get_host().split(':')
        host = host_parts[0]
        port = host_parts[1] if len(host_parts) > 1 else None

        if port:
            # Local development environment (e.g., http://slug.localhost:8000)
            redirect_url = f"http://{subdomain}.{host}:{port}/dashboard/setup/"
        else:
            # Production environment (e.g., https://slug.pillarandpost.com)
            redirect_url = f"https://{subdomain}.{host}/dashboard/setup/"

        return redirect(redirect_url)

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


def template_select(request):
    templates = [
        {'id': 'executive', 'name': 'The Executive', 'description': 'Clean, sharp, and corporate.'},
        {'id': 'startup', 'name': 'The Startup', 'description': 'Bold colors and modern typography.'},
        {'id': 'boutique', 'name': 'The Boutique', 'description': 'Elegant and focused on content.'},
    ]
    return render(request, "marketing/template_select.html", {'templates': templates})


def template_preview(request, template_id):
    name = request.GET.get('company_name') or "Your Company"
    context = {
        'template_id': template_id,
        'company_name': name,
        'jobs': [
            {
                'title': 'Senior Software Engineer', 
                'salary': '£80,000', 
                'location': 'London',
                'summary': 'Join a high-growth fintech team building scalable microservices.' # Added text
            },
            {
                'title': 'Talent Acquisition Manager', 
                'salary': '£55,000', 
                'location': 'Manchester',
                'summary': 'Lead the end-to-end recruitment lifecycle for our creative agency.' # Added text
            },
        ]
    }
    return render(request, "marketing/previews/preview_main.html", context)
