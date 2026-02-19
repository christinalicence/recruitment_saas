from django.urls import path
from . import views
from customers import views as customer_views

app_name = 'cms'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Dashboard & Site Editing
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit/', views.edit_site, name='edit_site'),
    path('dashboard/update-email/', views.dashboard, name='update_master_email'),
    
    # JOBS MANAGEMENT (Tenant Console)
    path('dashboard/jobs/', views.manage_jobs, name='manage_jobs'),
    path('dashboard/jobs/add/', views.add_job, name='add_job'),
    
    # Public Job Listings
    path('jobs/', views.public_job_list, name='job_list'), 
    path('jobs/<int:pk>/', views.public_job_detail, name='public_job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_to_job, name='apply_to_job'),

    # Live Preview for Tenants
    path('preview/', views.live_preview, name='live_preview'),
    path('dashboard/jobs/edit/<int:pk>/', views.edit_job, name='edit_job'),
    path('dashboard/jobs/delete/<int:pk>/', views.delete_job, name='delete_job'),
]   