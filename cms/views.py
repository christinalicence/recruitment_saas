import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.conf import settings

from .models import CompanyProfile, Job
from .forms import CompanyProfileForm

def get_profile_defaults(request):
    """
    Centralized helper to provide professional recruitment content 
    and set initial defaults for new tenants.
    """
    return {
        'display_name': request.tenant.name,
        'primary_color': '#1e3a8a',  
        'secondary_color': '#64748b', 
        'background_color': '#ffffff',
        'hero_title': "Connecting Exceptional Talent with World-Class Teams",
        'hero_text': (
            "We specialize in finding the perfect match between high-growth companies "
            "and industry-leading professionals."
        ),
        'about_title': "Expertise. Integrity. Results.",
        'about_content': "With over a decade of experience in specialized recruitment...",
        'jobs_header_text': "Explore our current openings.",
    }

# --- PUBLIC VIEWS ---

def home(request):
    """The main public landing page for the tenant site."""
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    latest_jobs = Job.objects.all().order_by('-id')[:3]
    return render(request, "cms/home.html", {
        "profile": profile,
        "latest_jobs": latest_jobs
    })

def about(request):
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    return render(request, "cms/about.html", {"profile": profile})

def job_list(request):
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    jobs = Job.objects.all()
    return render(request, "cms/job_list.html", {"profile": profile, "jobs": jobs})

def job_detail(request, job_id):
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    job = get_object_or_404(Job, id=job_id)
    return render(request, "cms/job_detail.html", {"profile": profile, "job": job})


# --- DASHBOARD / EDITOR VIEWS ---

@login_required
def dashboard(request):
    """The internal management area for the company."""
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    return render(request, 'cms/dashboard.html', {'profile': profile})

# --- DASHBOARD / EDITOR VIEWS ---


@login_required
def edit_site(request):
    profile, created = CompanyProfile.objects.get_or_create(...)

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Success! Your changes are now live.") # Success message
            return redirect('cms:edit_site')
        else:
            # This captures the "silent" failure and makes it a message
            messages.error(request, "Wait! We couldn't save. Please check the form for errors.")
            print(form.errors) # Still good for debugging!
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'cms/edit_site.html', {
        'form': form,
        'profile': profile,
    })

@login_required
@xframe_options_exempt
def live_preview(request):
    profile, _ = CompanyProfile.objects.get_or_create(
        tenant_slug=request.tenant.schema_name,
        defaults={
            'tenant_slug': request.tenant.schema_name,
            'display_name': request.tenant.name,
            **get_profile_defaults(request)
        }
    )
    
    # Override the profile object attributes with GET params for the preview
    # This keeps it as an object so .url methods still work!
    profile.template_choice = request.GET.get('template_choice', profile.template_choice)
    profile.display_name = request.GET.get('display_name', profile.display_name)
    profile.primary_color = request.GET.get('primary_color', profile.primary_color)
    profile.secondary_color = request.GET.get('secondary_color', profile.secondary_color)
    profile.background_color = request.GET.get('background_color', profile.background_color)
    profile.hero_title = request.GET.get('hero_title', profile.hero_title)
    profile.hero_text = request.GET.get('hero_text', profile.hero_text)

    return render(request, "cms/home.html", {
        'profile': profile, # Now passing the updated object
        'latest_jobs': Job.objects.all()[:3]
    })

# --- STRIPE INTEGRATION FOR CMS ---#


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request):
    """Initiates the Stripe Checkout process."""
    client = request.tenant 
    
    # 1. Ensure the customer exists in Stripe
    if not client.stripe_customer_id:
        customer = stripe.Customer.create(
            email=request.user.email,
            name=client.name,
            metadata={'tenant_id': client.id}
        )
        client.stripe_customer_id = customer.id
        client.save()

    # 2. Get the specific tenant domain (e.g., 'python.localhost')
    domain = client.domains.first().domain 
    
    # 3. Create the ONE session with your new pretty URLs
    session = stripe.checkout.Session.create(
        customer=client.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{'price': client.plan.stripe_price_id, 'quantity': 1}],
        mode='subscription',
        # Note: Added the 'cms' prefix to match your urls.py namespace
        success_url=f"http://{domain}:8000/billing/success/",
        cancel_url=f"http://{domain}:8000/billing/cancel/",
        metadata={'tenant_id': client.id}
    )
    
    return redirect(session.url, code=303)

def customer_portal(request):
    """Redirects active subscribers to manage their own billing."""
    session = stripe.billing_portal.Session.create(
        customer=request.tenant.stripe_customer_id,
        return_url=f"{settings.SITE_URL}/dashboard/",
    )
    return redirect(session.url, code=303)


def payment_success(request):
    """Render the success page after a successful Stripe payment."""
    return render(request, 'cms/payment_success.html')

def payment_cancel(request):
    """Render the cancel page if a user exits Stripe Checkout."""
    return render(request, 'cms/payment_cancel.html')