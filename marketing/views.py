from django.shortcuts import render, redirect
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
        
        # 1. Create the Tenant (Schema)
        tenant, created = Client.objects.get_or_create(
            name=company_name,
            defaults={'template_choice': template_id, 'on_trial': True}
        )
        
        # 2. Create the Domain
        host_full = request.get_host() 
        base_domain = host_full.split(':')[0]
        
        # Ensure subdomains work locally
        if base_domain == "127.0.0.1" or base_domain == "localhost":
            base_domain = "localhost"
            
        full_domain_no_port = f"{tenant.schema_name}.{base_domain}"
        
        Domain.objects.get_or_create(
            domain=full_domain_no_port,
            defaults={'tenant': tenant, 'is_primary': True}
        )
        
        # 3. Create the admin user in the new tenant's schema
        with schema_context(tenant.schema_name):
            if not User.objects.filter(email=admin_email).exists():
                User.objects.create_superuser(
                    username=admin_email,
                    email=admin_email,
                    password=password
                )
        
        # 4. Construct Redirect URL
        port = f":{host_full.split(':')[1]}" if ":" in host_full else ""
        
        if base_domain == "localhost":
            redirect_url = f"http://{tenant.schema_name}.localhost{port}/login/"
        else:
            redirect_url = f"https://{tenant.schema_name}.{base_domain}/login/"
            
        return redirect(redirect_url)

    return render(request, "marketing/signup.html", {"form": form})

def landing_page(request):
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
    return render(request, "marketing/preview_main.html", context)

def tenant_login(request):
    form = TenantLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('cms:dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "marketing/login.html", {"form": form})

def tenant_logout(request):
    logout(request)
    return redirect('public_marketing:landing')

def about_page(request):
    return render(request, "marketing/about.html")