from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CompanyProfile
from .forms import CompanyProfileForm


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
    return render(request, 'cms/dashboard.html')


@login_required
def job_list(request):
    """The list of jobs for the tenant."""
    # Placeholder implementation
    return render(request, 'cms/job_list.html')