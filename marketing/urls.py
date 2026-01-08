from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.tenant_login, name="tenant_login"),
    path("logout/", views.tenant_logout, name="tenant_logout"),
    path("", views.tenant_dashboard, name="tenant_dashboard"),
    path("signup/", views.tenant_signup, name="tenant_signup"),
]
