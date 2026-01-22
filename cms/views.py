from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CompanyProfile
from .forms import CompanyProfileForm
from django.core.exceptions import PermissionDenied


@login_required
def dashboard_setup_editor(request):
    """
    Handles initial site personalization immediately after login.
    """
    # Automatically use the tenant name as the default display name if it's new
    profile, created = CompanyProfile.objects.get_or_create(
        id=1,  # We only ever want one profile per tenant
        defaults={'display_name': request.tenant.name}
    )
    if request.method == "POST":
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Once they've saved their basic info, send them to the main dashboard
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
def dashboard(request):
    """The main dashboard for the tenant."""
    # Ensure the user belongs to this tenant
    if hasattr(request.user, 'tenant') and request.user.tenant != request.tenant:
        raise PermissionDenied 
    # Get or create the profile so we have the branding colors
    profile, _ = CompanyProfile.objects.get_or_create(
        id=1, 
        defaults={'display_name': request.tenant.name}
    )
    return render(request, 'cms/dashboard.html', {'profile': profile})


@login_required
def job_list(request):
    """The list of jobs for the tenant."""
    # Placeholder implementation
    return render(request, 'cms/job_list.html')


# cms/views.py

def home(request):
    """
    The Public Homepage for a Tenant's site.
    This is what candidates see.
    """
    # Get the branding profile
    profile, _ = CompanyProfile.objects.get_or_create(
        id=1, 
        defaults={'display_name': request.tenant.name}
    )
    # Grab the latest jobs to show on the landing page
    from .models import Job
    latest_jobs = Job.objects.all().order_by('-id')[:3]

    return render(request, "cms/home.html", {
        "profile": profile,
        "latest_jobs": latest_jobs,
    })


def about(request):
    """The Public About Us page."""
    profile, _ = CompanyProfile.objects.get_or_create(
        id=1, 
        defaults={'display_name': request.tenant.name}
    )
    return render(request, "cms/about.html", {"profile": profile})