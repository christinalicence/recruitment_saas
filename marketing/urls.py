from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.tenant_signup, name="tenant_signup"),
]