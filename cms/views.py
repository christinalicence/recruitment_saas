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
    """Reliably fetches the profile created during onboarding."""
    return get_object_or_404(CompanyProfile, tenant_slug=request.tenant.schema_name)


def home(request):
    profile = get_profile(request)
    # Get first 3 jobs for the home page feature section
    latest_jobs = Job.objects.all()[:3]
    return render(request, 'cms/index.html', {
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
        tenant.master_email = request.POST.get('master_email')
        tenant.save()
        messages.success(request, "Master email updated.")
        return redirect('cms:dashboard')

    profile = get_profile(request)
    jobs = Job.objects.all()
    return render(request, 'cms/dashboard.html', {'profile': profile, 'jobs': jobs})


@login_required
def edit_site(request):
    profile = get_profile(request)
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Site updated successfully!")
                return redirect('cms:edit_site')
            except BadRequest:
                messages.error(request, "Upload failed: Image is too large (Max 10MB). Please resize and try again.")
            except Exception:
                messages.error(request, "A server error occurred during the upload.")
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'cms/edit_site.html', {'form': form, 'profile': profile})

@login_required
@xframe_options_exempt
def live_preview(request):
    profile = get_profile(request)
    # Temporary overrides for preview
    profile.template_choice = request.GET.get('template_choice', profile.template_choice)
    profile.display_name = request.GET.get('display_name', profile.display_name)
    profile.primary_color = request.GET.get('primary_color', profile.primary_color)
    profile.secondary_color = request.GET.get('secondary_color', profile.secondary_color)
    profile.background_color = request.GET.get('background_color', profile.background_color)
    profile.hero_title = request.GET.get('hero_title', profile.hero_title)
    profile.hero_text = request.GET.get('hero_text', profile.hero_text)

    return render(request, "cms/home.html", {
        'profile': profile,
        'latest_jobs': Job.objects.all()[:3]
    })

def public_job_list(request):
    profile = get_profile(request)
    jobs = Job.objects.all()
    return render(request, "cms/public_job_list.html", {'jobs': jobs, 'profile': profile})

def public_job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    profile = get_profile(request)
    
    if request.method == "POST":
        candidate_name = request.POST.get('full_name')
        candidate_email = request.POST.get('email')
        candidate_phone = request.POST.get('phone')
        cv_file = request.FILES.get('cv')

        # Determine recipients
        recipients = [request.tenant.master_email]
        if job.custom_recipient_1:
            recipients.append(job.custom_recipient_1)
        if job.custom_recipient_2:
            recipients.append(job.custom_recipient_2)

        email_body = (
            f"New application for {job.title}\n\n"
            f"Name: {candidate_name}\n"
            f"Email: {candidate_email or 'Not provided'}\n"
            f"Phone: {candidate_phone}\n\n"
            f"The candidate's CV is attached."
        )

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
        except Exception:
            messages.error(request, "Technical glitch. Please try again or contact us directly.")
            return redirect('cms:public_job_detail', pk=pk)

    return render(request, "cms/public_job_detail.html", {'job': job, 'profile': profile})


def application_success(request):
    profile = get_profile(request)
    return render(request, "cms/application_success.html", {'profile': profile})


def payment_success(request):
    """The view for the post-Stripe redirection."""
    profile = get_profile(request)
    return render(request, 'cms/payment_success.html', {'profile': profile})