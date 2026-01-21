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
        company_name = form.cleaned_data["company_name"]
        admin_email = form.cleaned_data["admin_email"]
        password = form.cleaned_data["password"]
        
        # make tenant
        tenant, created = Client.objects.get_or_create(
            name=company_name,
            defaults={'template_choice': template_id, 'on_trial': True}
        )
        
        # make domain
        host_full = request.get_host()  # e.g. "localhost:8000"
        base_domain_no_port = host_full.split(':')[0]
        
        # Store domain WITHOUT port (for production)
        full_domain_no_port = f"{tenant.schema_name}.{base_domain_no_port}"
        Domain.objects.get_or_create(
            domain=full_domain_no_port,
            defaults={'tenant': tenant, 'is_primary': True}
        )
        
        # ALSO store domain WITH port (for local development)
        if ':' in host_full:
            full_domain_with_port = f"{tenant.schema_name}.{host_full}"
            Domain.objects.get_or_create(
                domain=full_domain_with_port,
                defaults={'tenant': tenant, 'is_primary': False}
            )
        
        # create superuser in tenant schema
        with schema_context(tenant.schema_name):
            if not User.objects.filter(username=admin_email).exists():
                User.objects.create_superuser(
                    username=admin_email,
                    email=admin_email,
                    password=password
                )
        
        # redirect to tenant subdomain login
        is_local = "localhost" in host_full or "127.0.0.1" in host_full
        protocol = "http" if is_local else "https"
        redirect_url = f"{protocol}://{tenant.schema_name}.{host_full}/login/"
        
        return redirect(redirect_url)

    return render(request, "marketing/signup.html", {"form": form, "template_id": template_id})


def tenant_login(request):
    form = TenantLoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user:
            login(request, user)
            return redirect("cms:setup") 
        else:
            # error message for invalid login
            messages.error(request, "Invalid email or password. Please try again.")

    return render(request, "marketing/login.html", {"form": form})


def tenant_logout(request):
    logout(request)
    return redirect("tenant_login")


def landing_page(request):
    # CURRENTLY FOR DEBUGGING PURPOSES ONLY
    print(f"DEBUG: Host is {request.get_host()}")
    print(f"DEBUG: Tenant is {getattr(request, 'tenant', 'No Tenant Found')}")
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
                'summary': 'Join a high-growth fintech team building scalable microservices.' 
            },
            {
                'title': 'Talent Acquisition Manager', 
                'salary': '£55,000', 
                'location': 'Manchester',
                'summary': 'Lead the end-to-end recruitment lifecycle for our creative agency.' 
            },
        ]
    }
    return render(request, "marketing/previews/preview_main.html", context)