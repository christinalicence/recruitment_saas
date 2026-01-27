from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import CompanyProfile
from .forms import CompanyProfileForm


def get_profile_defaults(request):
    """
    Centralized helper to provide consistent default branding 
    values across all views.
    """
    return {
        'display_name': request.tenant.name,
        'primary_color': '#2c3e50',
        'secondary_color': '#e74c3c',
        'background_color': '#ffffff'
    }


@login_required
def dashboard(request):
    """The main dashboard for the tenant."""
 
    profile, _ = CompanyProfile.objects.get_or_create(
        id=1, 
        defaults=get_profile_defaults(request)
    )
    return render(request, "cms/dashboard.html", {"profile": profile})


@login_required
def edit_site(request):
    """Handles site personalization (branding, colors, logo)."""
    profile, created = CompanyProfile.objects.get_or_create(
        id=1,
        defaults=get_profile_defaults(request)
    )

    if request.method == "POST":
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('cms:dashboard') 
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, "cms/edit_site.html", {
        "form": form,
        "profile": profile,
        "is_first_setup": created,
        "tenant": request.tenant
    })


@login_required
@xframe_options_exempt
def live_preview(request):
    """Renders home page content for the editor's iframe."""
    profile, _ = CompanyProfile.objects.get_or_create(
        id=1,
        defaults=get_profile_defaults(request)
    )
    return render(request, "cms/home.html", {
        "profile": profile,
        "is_preview": True
    })




def home(request):
    """The public-facing home page for the tenant (Agency site)."""
    profile, _ = CompanyProfile.objects.get_or_create(
        id=1,
        defaults=get_profile_defaults(request)
    )
    return render(request, "cms/home.html", {"profile": profile})

def about(request):
    """The public-facing 'About Us' page."""
    profile, _ = CompanyProfile.objects.get_or_create(
        id=1,
        defaults=get_profile_defaults(request)
    )
    return render(request, "cms/about.html", {"profile": profile})


@login_required
def job_list(request):
    """List of jobs for the tenant admin."""
    return render(request, "cms/job_list.html")