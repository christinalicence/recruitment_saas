from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage

from .models import CompanyProfile, Job
from .forms import CompanyProfileForm, JobForm
from cloudinary.exceptions import BadRequest

def get_tenant_profile(request):
    """
    Helper function to fetch the tenant's company profile.
    """
    return get_object_or_404(CompanyProfile, tenant_slug=request.tenant.schema_name)

def home(request):
    profile = get_tenant_profile(request)
    return render(request, 'cms/index.html', {'profile': profile})

def about(request):
    profile = get_tenant_profile(request)
    return render(request, "cms/about.html", {'profile': profile})

@login_required
def dashboard(request):
    tenant = request.tenant
    if request.method == 'POST' and 'master_email' in request.POST:
        tenant.master_email = request.POST.get('master_email')
        tenant.save()
        messages.success(request, "Master email updated.")
        return redirect('cms:dashboard')

    profile = get_tenant_profile(request)
    jobs = Job.objects.all()
    return render(request, 'cms/dashboard.html', {'profile': profile, 'jobs': jobs})

@login_required
def edit_site(request):
    profile = get_tenant_profile(request)
    
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Site updated successfully!")
                return redirect('cms:edit_site')
            except BadRequest:
                # Essential Cloudinary size warning
                messages.error(request, "Upload failed: Image is too large (Max 10MB). Please resize and try again.")
            except Exception:
                # Essential general safety warning
                messages.error(request, "A server error occurred during the upload.")
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'cms/edit_site.html', {'form': form, 'profile': profile})

@login_required
@xframe_options_exempt
def live_preview(request):
    """
    Shows real-time changes without saving to DB.
    """
    profile = get_tenant_profile(request)

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
