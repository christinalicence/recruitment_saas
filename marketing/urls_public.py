from django.urls import path
from marketing import views

app_name = "marketing"

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("choose-template/", views.template_select, name="template_select"),
    path("signup/", views.tenant_signup, name="tenant_signup"),
]