from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage

from .models import CompanyProfile, Job
from .forms import CompanyProfileForm, JobForm
from cloudinary.exceptions import BadRequest

# --- HELPER ---
def get_profile(request):
    """Reliably fetches the profile created by TenantService during onboarding."""
    return get_object_or_404(CompanyProfile, tenant_slug=request.tenant.schema_name)

# --- PUBLIC TENANT VIEWS (The Live Site) ---

def home(request):
    profile = get_profile(request)
    latest_jobs = Job.objects.filter(tenant=request.tenant).order_by('-created_at')[:3]
    return render(request, 'cms/home.html', {
        'profile': profile,
        'latest_jobs': latest_jobs
    })

def about(request):
    profile = get_profile(request)
    return render(request, "cms/about.html", {'profile': profile})

def public_job_list(request):
    profile = get_profile(request)
    jobs = Job.objects.filter(tenant=request.tenant).order_by('-created_at')
    return render(request, "cms/job_list.html", {'profile': profile, 'jobs': jobs})

def public_job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, tenant=request.tenant)
    profile = get_profile(request)
    return render(request, "cms/public_job_detail.html", {'job': job, 'profile': profile})

# --- SITE EDITOR & PREVIEW (The "Wedit Site" Stuff) ---

@login_required
def edit_site(request):
    """
    The main Site Editor. Handles branding, content, and Cloudinary uploads.
    """
    profile = get_profile(request)
    
    if request.method == 'POST':
        # Files are passed for logos/hero images
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Site updated successfully!")
                return redirect('cms:edit_site')
            except BadRequest:
                messages.error(request, "Upload failed: Image is too large (Max 10MB).")
            except Exception:
                messages.error(request, "A server error occurred during the upload.")
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'cms/edit_site.html', {
        'form': form,
        'profile': profile,
    })

@login_required
@xframe_options_exempt
def live_preview(request):
    """
    Used by the iframe in the Site Editor to show real-time changes 
    before the user hits 'Save'.
    """
    profile = get_profile(request)
    
    # These parameters are sent via JS from the editor form to the iframe URL
    fields = [
        'template_choice', 'display_name', 'primary_color', 
        'secondary_color', 'hero_title', 'hero_text'
    ]
    for field in fields:
        val = request.GET.get(field)
        if val:
            setattr(profile, field, val)
    
    return render(request, "cms/home.html", {
        'profile': profile,
        'latest_jobs': Job.objects.filter(tenant=request.tenant)[:3]
    })

# --- PRIVATE DASHBOARD & JOBS ---

@login_required
def dashboard(request):
    tenant = request.tenant
    if request.method == 'POST' and 'master_email' in request.POST:
        tenant.master_email = request.POST.get('master_email')
        tenant.save()
        messages.success(request, "Master email updated.")
        return redirect('cms:dashboard')

    profile = get_profile(request)
    jobs = Job.objects.filter(tenant=tenant)
    return render(request, 'cms/dashboard.html', {'profile': profile, 'jobs': jobs})

@login_required
def manage_jobs(request):
    jobs = Job.objects.filter(tenant=request.tenant).order_by('-created_at')
    return render(request, 'cms/manage_jobs.html', {'jobs': jobs})

@login_required
def add_job(request):
    if Job.objects.filter(tenant=request.tenant).count() >= 6:
        messages.warning(request, "Limit reached. Delete a post to add a new one.")
        return redirect('cms:manage_jobs')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.tenant = request.tenant
            job.save()
            messages.success(request, "Job vacancy posted!")
            return redirect('cms:manage_jobs')
    else:
        form = JobForm()
    return render(request, 'cms/job_form.html', {'form': form})

@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated!")
            return redirect('cms:manage_jobs')
    else:
        form = JobForm(instance=job)
    return render(request, 'cms/job_form.html', {'form': form})

@login_required
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job removed.")
        return redirect('cms:manage_jobs')
    return render(request, 'cms/job_confirm_delete.html', {'job': job})

# --- APPLICATIONS & SUCCESS ---

def apply_to_job(request, pk):
    job = get_object_or_404(Job, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        candidate_name = request.POST.get('full_name', 'Not provided')
        candidate_email = request.POST.get('email')
        cv_file = request.FILES.get('cv')

        recipients = []
        if job.custom_recipient_1: recipients.append(job.custom_recipient_1)
        if job.custom_recipient_2: recipients.append(job.custom_recipient_2)
        if not recipients and request.tenant.master_email:
            recipients.append(request.tenant.master_email)
        
        recipients = list(set(recipients))
        if not recipients:
            messages.error(request, "No recruiter email configured.")
            return redirect('cms:public_job_detail', pk=pk)

        email_msg = EmailMessage(
            subject=f"New Application: {job.title} - {candidate_name}",
            body=f"New application for {job.title}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            reply_to=[candidate_email] if candidate_email else None
        )
        if cv_file:
            email_msg.attach(cv_file.name, cv_file.read(), cv_file.content_type)

        try:
            email_msg.send(fail_silently=False)
            return redirect('cms:application_success')
        except Exception:
            messages.error(request, "Email service error.")
    
    return redirect('cms:public_job_detail', pk=pk)

def application_success(request):
    return render(request, 'cms/application_success.html', {'profile': get_profile(request)})

def payment_success(request):
    return render(request, 'cms/payment_success.html', {'profile': get_profile(request)})

def payment_cancel(request):
    return render(request, 'cms/payment_cancel.html', {'profile': get_profile(request)})