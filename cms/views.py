import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from .models import CompanyProfile, Job
from .forms import CompanyProfileForm, JobForm

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
    return render(request, "cms/home.html", {
        "profile": profile,
    })

def about(request):
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    return render(request, "cms/about.html", {"profile": profile})

def job_list(request):
    """The public list of all jobs for this tenant."""
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    jobs = Job.objects.all()
    
    return render(request, "cms/job_list.html", {
        'profile': profile,
        'jobs': jobs
    })

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
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )

    jobs = Job.objects.all() 
    
    return render(request, 'cms/dashboard.html', {
        'profile': profile,
        'jobs': jobs, 
    })


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

from django.core.mail import send_mail

# --- TENANT CONSOLE VIEWS --- JOBS


@login_required
def manage_jobs(request):
    """The private dashboard area where tenants see their list of jobs."""
    jobs = Job.objects.filter(tenant=request.tenant).order_by('-created_at')
    return render(request, 'cms/manage_jobs.html', {'jobs': jobs})

@login_required
def add_job(request):
    """The form to create a new job."""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.tenant = request.tenant # Link the job to the current tenant
            job.save()
            messages.success(request, "Job vacancy posted successfully!")
            return redirect('cms:manage_jobs')
    else:
        form = JobForm()
    return render(request, 'cms/job_form.html', {'form': form})

@login_required
def edit_job(request, pk):
    """The form to edit an existing job."""
    job = get_object_or_404(Job, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job vacancy updated!")
            return redirect('cms:manage_jobs')
    else:
        form = JobForm(instance=job)
    return render(request, 'cms/job_form.html', {'form': form})

@login_required
def delete_job(request, pk):
    """Simple view to delete a job."""
    job = get_object_or_404(Job, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job vacancy removed.")
        return redirect('cms:manage_jobs')
    return render(request, 'cms/job_confirm_delete.html', {'job': job})


def public_job_list(request):
    """The public page where candidates browse all jobs for this tenant."""
    # This matches the name expected by your urls.py
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    jobs = Job.objects.filter(tenant=request.tenant).order_by('-created_at')
    return render(request, "cms/job_list.html", {
        'profile': profile,
        'jobs': jobs
    })

def job_detail(request, pk):
    """The public detail page for a single job."""
    job = get_object_or_404(Job, pk=pk)
    profile = CompanyProfile.objects.get(display_name=request.tenant.name)
    return render(request, "cms/job_detail.html", {
        'job': job,
        'profile': profile
    })


# --- PUBLIC CANDIDATE VIEWS ---

def apply_to_job(request, pk):
    """Triggers the direct email to the tenant."""
    job = get_object_or_404(Job, pk=pk)
    profile = CompanyProfile.objects.get(tenant=request.tenant)
    
    if request.method == 'POST':
        # Logic: Priority 1 = Job Custom Emails, Priority 2 = Company Master Email
        recipients = []
        if job.custom_recipient_1:
            recipients.append(job.custom_recipient_1)
            if job.custom_recipient_2:
                recipients.append(job.custom_recipient_2)
        elif profile.master_application_email:
            recipients.append(profile.master_application_email)

        if recipients:
            send_mail(
                subject=f"Application: {job.title} - {request.POST.get('full_name')}",
                message=f"New applicant for {job.title}.\n\nName: {request.POST.get('full_name')}\nEmail: {request.POST.get('email')}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
            )
            messages.success(request, "Application sent directly to the recruiter!")
        
        return redirect('cms:job_detail', pk=pk)