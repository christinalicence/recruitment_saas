from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.text import slugify
from django_tenants.utils import schema_context
from django.templatetags.static import static
from customers.models import Client, Domain, Plan
from .forms import TenantSignupForm, TenantLoginForm
from django.core.mail import send_mail
from django.conf import settings
from .services import TenantService

def company_about(request):
    """The main marketing about page for Pillar & Post (getpillarpost.com)"""
    return render(request, "marketing/about.html")


def landing_page(request):
    """The main home page for getpillarpost.com"""
    return render(request, "marketing/landing.html")


def tenant_signup(request):
    """Public signup - refactored to use TenantService while preserving all logic."""
    template_id = request.GET.get('template', 'executive')
    name_from_url = request.GET.get('company_name', '').strip()

    initial_data = {}
    if name_from_url:
        initial_data['company_name'] = name_from_url
        
    form = TenantSignupForm(request.POST or None, initial=initial_data)

    if request.method == "POST" and form.is_valid():
        company_name = form.cleaned_data["company_name"]
        admin_email = form.cleaned_data["admin_email"]
        password = form.cleaned_data["password"]

        tenant, domain_name = TenantService.create_onboarding_tenant(
            company_name=company_name,
            admin_email=admin_email,
            password=password,
            template_id=template_id
        )

        if not tenant:
            messages.error(request, f"The name '{company_name}' is already taken.")
            return render(request, "marketing/signup.html", {
                'form': form, 
                'template_id': template_id
            })

        portal_url = f"https://{domain_name}/login/"
        try:
            send_mail(
                subject="Welcome to PillarPost!",
                message=f"Hi {company_name}, your portal is ready at: {portal_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False, 
            )
        except Exception as e:
            print(f"EMAIL ERROR: {e}")
            messages.warning(
                request, 
                "Your portal is ready, but we had trouble sending the welcome email. Please note your login details below."
            )

        messages.success(request, f"Success! Your site is ready at {domain_name}")
        return redirect(f"https://{domain_name}/login/")

    return render(request, "marketing/signup.html", {'form': form, 'template_id': template_id})


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
    host = request.get_host().split(':')[0]
    parts = host.split('.')
    if len(parts) >= 2:
        base_domain = '.'.join(parts[-2:])
        return redirect(f"https://www.{base_domain}/")
    return redirect('/')

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
