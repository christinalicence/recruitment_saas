from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.text import slugify
from django_tenants.utils import schema_context
from django.templatetags.static import static
from customers.models import Client, Domain, Plan
from .forms import TenantSignupForm, TenantLoginForm

def tenant_signup(request):
    template_id = request.GET.get('template', 'executive')
    form = TenantSignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        company_name = form.cleaned_data["company_name"]
        admin_email = form.cleaned_data["admin_email"]
        password = form.cleaned_data["password"]
        
        tenant_slug = slugify(company_name)
        domain_name = f"{tenant_slug}.getpillarpost.com"
        schema_name = tenant_slug.replace('-', '_')

        if Domain.objects.filter(domain=domain_name).exists():
            messages.error(request, "That name is taken.")
            return render(request, "marketing/tenant_signup.html", {'form': form})

        # Safety: Ensure the 'Standard' plan exists in the DB
        standard_plan, _ = Plan.objects.get_or_create(name="Standard")

        tenant = Client.objects.create(
            schema_name=schema_name,
            name=company_name,
            template_choice=template_id,
            plan=standard_plan,
            notification_email_1=admin_email,
            is_active=True 
        )

        Domain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)

        with schema_context(tenant.schema_name):
            User.objects.create_user( # Standard client user
                username=admin_email,
                email=admin_email,
                password=password
            )

        return redirect(f"https://{domain_name}/login/")

    return render(request, "marketing/tenant_signup.html", {'form': form})

def tenant_login(request):
    form = TenantLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('cms:dashboard')
        messages.error(request, "Invalid email or password.")
    return render(request, "marketing/tenant_login.html", {'form': form})

def tenant_logout(request):
    logout(request)
    return redirect('public_marketing:landing')

def template_select(request):
    templates = [
        {'id': 'executive', 'name': 'The Executive', 'description': 'Clean, sharp, and corporate.'},
        {'id': 'startup', 'name': 'The Startup', 'description': 'Bold colors and modern typography.'},
        {'id': 'boutique', 'name': 'The Boutique', 'description': 'Elegant and focused on content.'},
    ]
    return render(request, "marketing/template_select.html", {'templates': templates})

def template_preview(request, template_id):
    name = request.GET.get('company_name', 'Your Company')
    stock_images = {
        'executive': 'marketing/images/default_executive.jpg',
        'boutique': 'marketing/images/default_boutique.jpg',
        'startup': 'marketing/images/default_startup.jpg',
    }
    dummy_jobs = [
        {'title': 'Senior Strategy Consultant', 'location': 'London', 'salary': '£85k+', 'summary': 'Strategy lead...'},
        {'title': 'Lead Frontend Engineer', 'location': 'Remote', 'salary': '€70k+', 'summary': 'React build...'},
    ]
    image_filename = stock_images.get(template_id, stock_images['executive'])
    return render(request, "marketing/preview_main.html", {
        'template_id': template_id,
        'company_name': name,
        'hero_image': static(image_filename),
        'jobs': dummy_jobs
    })