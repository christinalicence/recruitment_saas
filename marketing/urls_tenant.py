from django.urls import path
from .views import tenant_dashboard, tenant_login, tenant_logout

urlpatterns = [
    path("", tenant_dashboard, name="tenant_dashboard"),
    path("login/", tenant_login, name="tenant_login"),
    path("logout/", tenant_logout, name="tenant_logout"),
]
