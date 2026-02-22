from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from .models import CompanyProfile, Job
from .forms import CompanyProfileForm, JobForm

from cloudinary.exceptions import BadRequest


def get_profile(request):
    """Reliably fetches the profile created by TenantService during onboarding."""
    return get_object_or_404(CompanyProfile, tenant_slug=request.tenant.schema_name)


def home(request):
    profile = get_profile(request)
    latest_jobs = Job.objects.all().order_by('-created_at')[:3]
    return render(request, "cms/home.html", {
        'profile': profile, 
        'latest_jobs': latest_jobs
    })


def about(request):
    profile = get_profile(request)
    return render(request, "cms/about.html", {'profile': profile})


@login_required
def dashboard(request):
    tenant = request.tenant
    if request.method == 'POST' and 'master_email' in request.POST:
        new_email = request.POST.get('master_email')
        tenant.master_email = new_email
        tenant.save()
        messages.success(request, f"Master email updated to {new_email}")
        return redirect('cms:dashboard')
    profile = get_profile(request)
    jobs = Job.objects.all() 
        
    return render(request, 'cms/dashboard.html', {
        'profile': profile,
        'jobs': jobs,
    })


@login_required
def edit_site(request):
    """
    Site Editor: Maintains all preview logic, prevents MultipleObjectsReturned,
    and catches Cloudinary 'File Too Large' errors.
    """
    profile = CompanyProfile.objects.filter(tenant_slug=request.tenant.schema_name).first()
    
    if not profile:
        profile = CompanyProfile.objects.create(
            tenant_slug=request.tenant.schema_name,
            **get_profile_defaults(request)
        )

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Site updated successfully!")
                return redirect('cms:edit_site')
            except BadRequest as e:
                messages.error(request, "Upload failed: Image is too large (Max 10MB). Please resize and try again.")
            except Exception as e:
                messages.error(request, "A server error occurred during the upload.")
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'cms/edit_site.html', {
        'form': form,
        'profile': profile,
    })


@xframe_options_exempt
@login_required
def live_preview(request):
    profile = get_profile(request)
    for field in ['template_choice', 'display_name', 'primary_color', 'secondary_color']:
        val = request.GET.get(field)
        if val:
            setattr(profile, field, val)
    
    return render(request, 'cms/home.html', {
        'profile': profile,
        'latest_jobs': latest_jobs,
        'is_preview': True
    })


def payment_success(request):
    """Just renders the pretty success HTML"""
    return render(request, 'cms/payment_success.html')


def payment_cancel(request):
    """Just renders the pretty cancel HTML"""
    return render(request, 'cms/payment_cancel.html')


@login_required
def manage_jobs(request):
    """The private dashboard area where tenants see their list of jobs."""
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'cms/manage_jobs.html', {'jobs': jobs})


@login_required
def add_job(request):
    """The form to create a new job."""
    job_count = Job.objects.count()
    if job_count >= 6:
        messages.warning(request, "Job limit reached. Delete a post to add a new one.")
        return redirect('cms:manage_jobs')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.save()
            messages.success(request, "Job vacancy posted successfully!")
            return redirect('cms:manage_jobs')
    else:
        form = JobForm()
    return render(request, 'cms/job_form.html', {'form': form})


@login_required
def edit_job(request, pk):
    """The form to edit an existing job."""
    job = get_object_or_404(Job, pk=pk)
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
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job vacancy removed.")
        return redirect('cms:manage_jobs')
    return render(request, 'cms/job_confirm_delete.html', {'job': job})


# --- PUBLIC FACING VIEWS ---

def public_job_list(request):
    """The public page where candidates browse all jobs."""
    profile = CompanyProfile.objects.filter(tenant_slug=request.tenant.schema_name).first()
    if not profile:
        profile = CompanyProfile.objects.create(
            tenant_slug=request.tenant.schema_name,
            **get_profile_defaults(request)
        )
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, "cms/job_list.html", {
        'profile': profile,
        'jobs': jobs
    })


def public_job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    profile = CompanyProfile.objects.filter(tenant_slug=request.tenant.schema_name).first()
    if not profile:
        profile = CompanyProfile.objects.create(
            tenant_slug=request.tenant.schema_name,
            **get_profile_defaults(request)
        )
    return render(request, "cms/public_job_detail.html", {
        'job': job,
        'profile': profile
    })


def apply_to_job(request, pk):
    """Handles the application email trigger with safety checks."""
    job = get_object_or_404(Job, pk=pk)
    profile = CompanyProfile.objects.filter(tenant_slug=request.tenant.schema_name).first()

    if request.method == 'POST':
        candidate_name = request.POST.get('full_name', 'Not provided')
        candidate_email = request.POST.get('email')
        candidate_phone = request.POST.get('phone', 'Not provided')
        cv_file = request.FILES.get('cv')

        recipients = []
        if job.custom_recipient_1: 
            recipients.append(job.custom_recipient_1)
        if job.custom_recipient_2: 
            recipients.append(job.custom_recipient_2)

        if not recipients and request.tenant.master_email:
            recipients.append(request.tenant.master_email)
        
        recipients = list(set(recipients))

        if not recipients:
            messages.error(request, "Application failed: No recruiter email is configured for this site.")
            return redirect('cms:public_job_detail', pk=pk)

        email_body = (
            f"New Application for {job.title}\n\n"
            f"Name: {candidate_name}\n"
            f"Email: {candidate_email or 'Not provided'}\n"
            f"Phone: {candidate_phone}\n\n"
            f"The candidate's CV is attached."
        )

        from django.core.mail import EmailMessage
        email_msg = EmailMessage(
            subject=f"New Application: {job.title} - {candidate_name}",
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            reply_to=[candidate_email] if candidate_email else None
        )

        if cv_file:
            if cv_file.size > 5 * 1024 * 1024:
                messages.error(request, "File too large. Please upload a CV smaller than 5MB.")
                return redirect('cms:public_job_detail', pk=pk)
            
            email_msg.attach(cv_file.name, cv_file.read(), cv_file.content_type)

        try:
            email_msg.send(fail_silently=False)
            messages.success(request, "Your application has been sent successfully!")
            return redirect('cms:application_success')
        except Exception as e:
            messages.error(request, "Technical glitch...")
            return redirect('cms:public_job_detail', pk=pk)
    return render(request, "cms/public_job_detail.html", {'job': job, 'profile': profile})


def application_success(request):
    profile = CompanyProfile.objects.filter(tenant_slug=request.tenant.schema_name).first()
    return render(request, 'cms/application_success.html', {'profile': profile})