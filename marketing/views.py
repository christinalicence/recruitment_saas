from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django_tenants.utils import schema_context
from customers.models import Client, Domain
from .forms import TenantSignupForm, TenantLoginForm


def tenant_signup(request):
    """Public signup - creates tenant and shows success page."""
    template_id = request.GET.get('template', 'executive')
    initial_data = {'company_name': request.GET.get('company_name', '')}
    form = TenantSignupForm(request.POST or None, initial=initial_data)

    if request.method == "POST" and form.is_valid():
        company_name = form.cleaned_data["company_name"]
        admin_email = form.cleaned_data["admin_email"]
        password = form.cleaned_data["password"]
        
        # 1. Create Tenant
        tenant, created = Client.objects.get_or_create(
            name=company_name,
            defaults={'template_choice': template_id, 'on_trial': True}
        )
        
        # 2. Create Domain
        host_full = request.get_host()
        base_domain = host_full.split(':')[0]
        if base_domain in ["127.0.0.1", "localhost"]:
            base_domain = "localhost"
            
        full_domain = f"{tenant.schema_name}.{base_domain}"
        Domain.objects.get_or_create(
            domain=full_domain,
            defaults={'tenant': tenant, 'is_primary': True}
        )
        
        # 3. Create user AND profile inside the Tenant Schema
        with schema_context(tenant.schema_name):
            tenant_user, t_created = User.objects.get_or_create(
                username=admin_email,
                defaults={
                    'email': admin_email, 
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            tenant_user.set_password(password)
            tenant_user.save()
            
            # Create CompanyProfile
            from cms.models import CompanyProfile
            CompanyProfile.objects.get_or_create(
                id=1,
                defaults={
                    'display_name': company_name,
                    'primary_color': '#2c3e50',
                    'secondary_color': '#e74c3c',
                    'background_color': '#ffffff'
                }
            )
        
        # 4. Show success page instead of redirecting
        port = f":{host_full.split(':')[1]}" if ":" in host_full else ""
        login_url = f"http://{full_domain}{port}/login/"
        
        return render(request, "marketing/signup_success.html", {
            "login_url": login_url,
            "company_name": company_name,
            "email": admin_email
        })

    return render(request, "marketing/signup.html", {"form": form})


def portal_finder(request):
    """Help users find their portal by email address."""
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, "Please enter your email address")
            return render(request, "marketing/portal_finder.html")
        
        # Search for tenants where this user exists
        found_tenants = []
        
        for tenant in Client.objects.exclude(schema_name='public'):
            with schema_context(tenant.schema_name):
                if User.objects.filter(email=email).exists():
                    domain = tenant.domains.first()
                    if domain:
                        host_full = request.get_host()
                        port = f":{host_full.split(':')[1]}" if ":" in host_full else ""
                        login_url = f"http://{domain.domain}{port}/login/"
                        
                        found_tenants.append({
                            'name': tenant.name,
                            'login_url': login_url
                        })
        
        if found_tenants:
            return render(request, "marketing/portal_finder.html", {
                'found_tenants': found_tenants,
                'email': email
            })
        else:
            messages.error(request, f"No portals found for {email}. Please check your email or sign up.")
            return render(request, "marketing/portal_finder.html")
    
    return render(request, "marketing/portal_finder.html")


def tenant_login(request):
    form = TenantLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request, 
            username=form.cleaned_data['email'], 
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            return redirect('cms:dashboard') 
        else:
            messages.error(request, "Invalid email or password")
    return render(request, "marketing/login.html", {"form": form})

def tenant_logout(request):
    logout(request)
    messages.success(request, "You've been logged out.")
    return redirect('tenant_login')


def landing_page(request):
    return render(request, "marketing/landing.html")


def template_select(request):
    templates = [
        {'id': 'executive', 'name': 'The Executive', 'description': 'Clean, sharp, and corporate.'},
        {'id': 'startup', 'name': 'The Startup', 'description': 'Bold colors and modern typography.'},
        {'id': 'boutique', 'name': 'The Boutique', 'description': 'Elegant and focused on content.'},
    ]
    return render(request, "marketing/template_select.html", {'templates': templates})


# marketing/views.py

def template_preview(request, template_id):
    name = request.GET.get('company_name', 'Your Company')
    
    stock_images = {
        'executive': 'hero/default_executive.jpg',
        'boutique': 'hero/default_boutique.jpg',
        'startup': 'hero/default_startup.jpg',
    }

    dummy_jobs = [
        {'title': 'Senior Strategy Consultant', 'location': 'London, UK', 'salary': '£85k - £110k', 'summary': 'Leading a team of analysts...'},
        {'title': 'Lead Frontend Engineer', 'location': 'Remote', 'salary': '€70k - €95k', 'summary': 'Building scalable React components...'},
        {'title': 'Creative Account Manager', 'location': 'New York', 'salary': '$90k - $120k', 'summary': 'Bridging the gap between design and clients...'}
    ]

    return render(request, "marketing/preview_main.html", {
        'template_id': template_id,
        'company_name': name,
        'hero_image': f"/media/{stock_images.get(template_id, stock_images['executive'])}",
        'jobs': dummy_jobs
    })


def about_page(request):
    return render(request, "marketing/about.html")