# cms/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    """The main dashboard for the tenant."""
    return render(request, 'cms/dashboard.html')


@login_required
def job_list(request):
    """The list of jobs for the tenant."""
    # Placeholder implementation
    return render(request, 'cms/job_list.html')