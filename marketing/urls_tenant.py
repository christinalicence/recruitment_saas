from django.urls import path, include
from marketing import views

urlpatterns = [
    path("login/", views.tenant_login, name="tenant_login"),
    path("logout/", views.tenant_logout, name="tenant_logout"),
    path('dashboard/setup/', views.dashboard_setup, name='dashboard_setup'),
    path('dashboard/', include('cms.urls')),
]