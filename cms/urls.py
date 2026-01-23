from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('', views.home, name='home'),     
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit-site/', views.edit_site, name='edit_site'), 
    path('jobs/', views.job_list, name='job_list'),
    path('about/', views.about, name='about'),
    path('live-preview/', views.live_preview, name='live_preview'),
]