from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.text import slugify
from django_tenants.utils import schema_context
from customers.models import Client, Domain, Plan
from .forms import TenantSignupForm

def tenant_signup(request):
    """Public signup - creates tenant and admin user."""
    # Get template from URL (passed from the preview page)
    template_id = request.GET.get('template', 'executive')
    
    # Pre-fill company name if they typed it on the previous page
    initial_data = {'company_name': request.GET.get('company_name', '')}
    form = TenantSignupForm(request.POST or None, initial=initial_data)

    if request.method == "POST" and form.is_valid():
        company_name = form.cleaned_data["company_name"]
        admin_email = form.cleaned_data["admin_email"]
        password = form.cleaned_data["password"]
        
        # 1. Generate URLs and Schema names
        tenant_slug = slugify(company_name) # "Acme Corp" -> "acme-corp"
        domain_name = f"{tenant_slug}.getpillarpost.com"
        schema_name = tenant_slug.replace('-', '_') # "acme_corp" (DBs hate dashes)

        # 2. Check for duplicates BEFORE creating anything
        if Domain.objects.filter(domain=domain_name).exists():
            messages.error(request, f"The name '{company_name}' is already taken. Please try another.")
            return render(request, "marketing/tenant_signup.html", {'form': form})

        # 3. Get the Plan (Make sure this exists in your Heroku DB!)
        standard_plan = Plan.objects.filter(name="Standard").first()

        # 4. Create the Tenant
        tenant = Client.objects.create(
            schema_name=schema_name,
            name=company_name,
            template_choice=template_id,
            plan=standard_plan,
            notification_email_1=admin_email,
            is_active=True # Active for testing; change to False if implementing trial later
        )

        # 5. Create the Domain link
        Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=True
        )

        # 6. Create the Admin User inside the new tenant's schema
        with schema_context(tenant.schema_name):
            # We use create_superuser so they have full access to their dashboard
            User.objects.create_superuser(
                username=admin_email,
                email=admin_email,
                password=password
            )

        messages.success(request, f"Success! Your site is ready.")
        # Redirect directly to their new login page
        return redirect(f"https://{domain_name}/login/")

    return render(request, "marketing/tenant_signup.html", {'form': form})


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


def template_preview(request, template_id):
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
    hero_url = static(image_filename)

    return render(request, "marketing/preview_main.html", {
        'template_id': template_id,
        'company_name': name,
        'hero_image': hero_url,
        'jobs': dummy_jobs
    })


def about_page(request):
    return render(request, "marketing/about.html")