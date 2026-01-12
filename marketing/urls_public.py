from django.urls import path
from marketing import views

app_name = "marketing"

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("signup/", views.tenant_signup, name="tenant_signup"),
]