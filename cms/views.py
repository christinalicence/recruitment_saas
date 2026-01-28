from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import CompanyProfile, Job
from .forms import CompanyProfileForm


def get_profile_defaults(request):
    """
    Centralized helper to provide professional recruitment content 
    and stock imagery as defaults.
    """
    return {
        'display_name': request.tenant.name,
        'primary_color': '#1e3a8a',  # Professional Navy
        'secondary_color': '#64748b', # Slate Grey
        'background_color': '#ffffff',
        'hero_title': "Connecting Exceptional Talent with World-Class Teams",
        'hero_text': (
            "We specialize in finding the perfect match between high-growth companies "
            "and industry-leading professionals. Our mission is to build the future "
            "of work, one placement at a time."
        ),
        # Default Stock Photos
        'hero_image': "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=1200&q=80",
        'team_photo': "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80",
        
        'about_title': "Expertise. Integrity. Results.",
        'about_content': (
            "With over a decade of experience in executive search and technical "
            "staffing, we have helped hundreds of companies scale their operations. "
            "Our methodology combines data-driven insights with a human-first approach "
            "to ensure long-term cultural and professional alignment."
        ),
        'jobs_header_text': "Explore our current career opportunities. Your next milestone starts here."
    }

@login_required
def dashboard(request):
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name, # Use name instead of ID
        defaults=get_profile_defaults(request)
    )
    return render(request, "cms/dashboard.html", {"profile": profile})

@login_required
def edit_site(request):
    """Handles site personalization (branding, colors, logo)."""
    profile, created = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
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

def home(request):
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    return render(request, "cms/home.html", {"profile": profile})


@login_required
@xframe_options_exempt
def live_preview(request):
    """
    Renders the home page with real-time updates for colors and text.
    """
    profile = CompanyProfile.objects.first() 
    
    # We include secondary_color here to fix the update issue
    preview_data = {
        'display_name': request.GET.get('display_name', profile.display_name if profile else "New Agency"),
        'hero_title': request.GET.get('hero_title', profile.hero_title if profile else "Great Careers Await"),
        'hero_text': request.GET.get('hero_text', profile.hero_text if profile else ""),
        'primary_color': request.GET.get('primary_color', profile.primary_color if profile else "#1e3a8a"),
        'secondary_color': request.GET.get('secondary_color', profile.secondary_color if profile else "#64748b"),
        'background_color': request.GET.get('background_color', profile.background_color if profile else "#ffffff"),
        'template_choice': request.GET.get('template_choice', getattr(profile, 'template_choice', 'executive')),
        # Fallback for images in preview if not uploaded
        'hero_image': profile.hero_image if profile and profile.hero_image else None,
    }

    return render(request, "cms/home.html", {
        'profile': preview_data,
        'latest_jobs': Job.objects.all()[:3]
    })


def about(request):
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    return render(request, "cms/about.html", {"profile": profile})

@login_required
def job_list(request):
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    jobs = Job.objects.all()
    return render(request, "cms/job_list.html", {
        "profile": profile,
        "jobs": jobs
    })


def job_detail(request, job_id):
    profile, _ = CompanyProfile.objects.get_or_create(
        display_name=request.tenant.name,
        defaults=get_profile_defaults(request)
    )
    job = Job.objects.get(id=job_id)
    return render(request, "cms/job_detail.html", {
        "profile": profile,
        "job": job
    })