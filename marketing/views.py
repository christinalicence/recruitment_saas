from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.text import slugify
from django_tenants.utils import schema_context
from django.templatetags.static import static
from customers.models import Client, Domain, Plan
from .forms import TenantSignupForm, TenantLoginForm

def company_about(request):
    """The main marketing about page for Pillar & Post (getpillarpost.com)"""
    return render(request, "marketing/about.html")

def landing_page(request):
    """The main home page for getpillarpost.com"""

    return render(request, "marketing/landing.html")

def tenant_signup(request):
    """Public signup - creates tenant and standard client user."""
    template_id = request.GET.get('template', 'executive')
    name_from_url = request.GET.get('company_name', '')
    form = TenantSignupForm(request.POST or None,)
    
    if name_from_url:
        form.fields['company_name'].widget.attrs.update({
            'placeholder': name_from_url
        })

    if request.method == "POST" and form.is_valid():
        company_name = form.cleaned_data["company_name"]
        admin_email = form.cleaned_data["admin_email"]
        password = form.cleaned_data["password"]
        
        # 1. Production Naming Logic
        tenant_slug = slugify(company_name)
        domain_name = f"{tenant_slug}.getpillarpost.com"
        schema_name = tenant_slug.replace('-', '_')

        # 2. Prevent Crashes
        if Domain.objects.filter(domain=domain_name).exists():
            messages.error(request, f"The name '{company_name}' is already taken.")
            return render(request, "marketing/signup.html", {'form': form})

        # 3. Get/Create Plan (Prevents crash if Plan table is empty)
        standard_plan, _ = Plan.objects.get_or_create(name="Standard")

        # 4. Create Tenant (Kept notification_email_1 and template_choice)
        tenant = Client.objects.create(
            schema_name=schema_name,
            name=company_name,
            template_choice=template_id,
            plan=standard_plan,
            notification_email_1=admin_email,
            is_active=True # Set to True so you can log in immediately
        )

        # 5. Create Domain
        Domain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)

        # 6. Create User in the new schema (Standard User)
        with schema_context(tenant.schema_name):
            User.objects.create_user(
                username=admin_email,
                email=admin_email,
                password=password
            )

        messages.success(request, f"Success! Your site is ready at {domain_name}")
        return redirect(f"https://{domain_name}/login/")

    return render(request, "marketing/signup.html", {'form': form})

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
    return render(request, "marketing/login.html", {'form': form})

def tenant_logout(request):
    logout(request)
    # Redirect to the main public landing page
    return redirect('public_marketing:landing')

def template_select(request):
    templates = [
        {'id': 'executive', 'name': 'The Executive', 'description': 'Clean, sharp, and corporate.'},
        {'id': 'startup', 'name': 'The Startup', 'description': 'Bold colors and modern typography.'},
        {'id': 'boutique', 'name': 'The Boutique', 'description': 'Elegant and focused on content.'},
    ]
    return render(request, "marketing/template_select.html", {'templates': templates})

def template_preview(request, template_id):
    """Logic kept exactly as originally provided"""
    name = request.GET.get('company_name', 'Your Company')
    stock_images = {
        'executive': 'marketing/images/default_executive.jpg',
        'boutique': 'marketing/images/default_boutique.jpg',
        'startup': 'marketing/images/default_startup.jpg',
    }
    dummy_jobs = [
        {'title': 'Senior Strategy Consultant', 'location': 'London, UK', 'salary': '£85k - £110k', 'summary': 'Leading a team of analysts...'},
        {'title': 'Lead Frontend Engineer', 'location': 'Remote', 'salary': '€70k - €95k', 'summary': 'Building scalable React components...'},
        {'title': 'Creative Account Manager', 'location': 'New York', 'salary': '$90k - $120k', 'summary': 'Bridging the gap between design and clients...'}
    ]
    image_filename = stock_images.get(template_id, stock_images['executive'])
    
    return render(request, "marketing/preview_main.html", {
        'template_id': template_id,
        'company_name': name,
        'hero_image': static(image_filename),
        'jobs': dummy_jobs
    })


def portal_finder(request):
    """Allows users to find their tenant portal by admin email."""
    found_tenants = []
    email = None

    if request.method == "POST":
        email = request.POST.get('email')
        if email:
            tenants = Client.objects.filter(notification_email_1__iexact=email)
            for tenant in tenants:
                domain = tenant.domains.filter(is_primary=True).first()
                if domain:
                    found_tenants.append({
                        'name': tenant.name,
                        'login_url': f"https://{domain.domain}/login/"
                    })
            
            if not found_tenants:
                messages.error(request, "No portals found for that email address.")

    return render(request, "marketing/portal_finder.html", {
        'found_tenants': found_tenants,
        'email': email
    })
