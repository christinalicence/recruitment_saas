
from django.urls import path
from marketing import views

app_name = "marketing"

urlpatterns = [
    path("login/", views.tenant_login, name="tenant_login"),
    path("dashboard/", views.tenant_dashboard, name="tenant_dashboard"),
    path("logout/", views.tenant_logout, name="tenant_logout"),
]