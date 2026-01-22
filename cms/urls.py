from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'), # <--- Add this line
    path('dashboard/', views.dashboard, name='dashboard'),
    path('setup/', views.dashboard_setup_editor, name='setup'), 
    path('jobs/', views.job_list, name='job_list'),
]