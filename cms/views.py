from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .models import CompanyProfile
from .forms import CompanyProfileForm

def check_tenant_permission(request):
    """
    Helper to ensure the authenticated user actually exists in the 
    current tenant's schema. This prevents cross-tenant access.
    """
    try:
        User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        raise PermissionDenied("You do not have permission to access this tenant.")

@login_required
def dashboard(request):
    """The main dashboard for the tenant."""
    check_tenant_permission(request)
    
    profile, _ = CompanyProfile.objects.get_or_create(
        id=1, 
        defaults={'display_name': request.tenant.name}
    )
    return render(request, "cms/dashboard.html", {"profile": profile})

@login_required
def edit_site(request):
    """Handles site personalization (branding, colors, logo)."""
    check_tenant_permission(request)
    
    profile, created = CompanyProfile.objects.get_or_create(
        id=1,
        defaults={'display_name': request.tenant.name}
    )

    if request.method == "POST":
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Redirect to absolute path for stability across URLconfs
            return redirect('/dashboard/') 
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
    check_tenant_permission(request)
    profile, _ = CompanyProfile.objects.get_or_create(id=1)
    return render(request, "cms/home.html", {"profile": profile})


def home(request):
    """
    The public-facing home page for the tenant (Agency site).
    """
    profile, _ = CompanyProfile.objects.get_or_create(
        id=1,
        defaults={'display_name': request.tenant.name}
    )
    return render(request, "cms/home.html", {"profile": profile})


def about(request):
    """The public-facing 'About Us' page."""
    profile, _ = CompanyProfile.objects.get_or_create(id=1)
    return render(request, "cms/about.html", {"profile": profile})


@login_required
def job_list(request):
    """List of jobs for the tenant admin."""
    check_tenant_permission(request)
    return render(request, "cms/job_list.html")