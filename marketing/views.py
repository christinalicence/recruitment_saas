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
    # Catching pre-fill data from the Preview/Selection page
    template_id = request.GET.get('template', 'professional')
    initial_data = {
        'company_name': request.GET.get('company_name', ''),
    }
    form = TenantSignupForm(request.POST or None, initial=initial_data)
    if request.method == "POST" and form.is_valid():
        company_name = form.cleaned_data["company_name"]
        admin_email = form.cleaned_data["admin_email"]
        password = form.cleaned_data["password"]
        
        # Create the tenant first - the model now generates schema_name
        tenant = Client.objects.create(
            name=company_name,
            template_choice=template_id, 
            paid_until=date.today() + timedelta(days=14),
            on_trial=True,
        )
        
        # Now retrieve the auto-generated slug to create the domain
        subdomain = tenant.schema_name
        
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
