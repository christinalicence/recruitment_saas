from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit/', views.edit_site, name='edit_site'),
    path('dashboard/jobs/', views.job_list, name='job_list'),
    path('preview/', views.live_preview, name='live_preview'),
]