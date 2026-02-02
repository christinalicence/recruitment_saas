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

@login_required
def edit_site(request):
    """Handles site design updates, supporting image uploads and resizing."""
    profile, created = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )

    if request.method == 'POST':
        # Pass request.FILES for image uploads
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                form.save() # This triggers the resizing save() in models.py
                messages.success(request, "Your site has been updated successfully!")
                return redirect('cms:edit_site')
            except Exception as e:
                messages.error(request, f"Error processing images: {str(e)}")
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'cms/edit_site.html', {'form': form, 'profile': profile})

@xframe_options_exempt
def live_preview(request):
    """Powers the real-time preview iframe in the dashboard."""
    profile = CompanyProfile.objects.filter(display_name=request.tenant.name).first()
    
    # Grab current form choices from GET params for instant preview feedback
    template_choice = request.GET.get('template_choice', getattr(profile, 'template_choice', 'executive'))
    
    # Calculate image path: Uploaded URL vs Local Fallback URL
    hero_url = f"{settings.MEDIA_URL}hero/default_{template_choice}.jpg"
    if profile and profile.hero_image:
        try:
            hero_url = profile.hero_image.url
        except ValueError:
            pass

    preview_data = {
        'display_name': request.GET.get('display_name', profile.display_name if profile else "Your Company"),
        'primary_color': request.GET.get('primary_color', profile.primary_color if profile else "#1e3a8a"),
        'secondary_color': request.GET.get('secondary_color', profile.secondary_color if profile else "#64748b"),
        'background_color': request.GET.get('background_color', profile.background_color if profile else "#ffffff"),
        'template_choice': template_choice,
        'hero_title': request.GET.get('hero_title', profile.hero_title if profile else "Great Careers Await"),
        'hero_text': request.GET.get('hero_text', profile.hero_text if profile else ""),
        'get_hero_image': hero_url,  # Key for the template
    }

    return render(request, "cms/home.html", {
        'profile': preview_data,
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