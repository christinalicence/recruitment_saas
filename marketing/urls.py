from django.urls import path
from . import views

app_name = 'public_marketing'

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("find-portal/", views.portal_finder, name="portal_finder"),
    path("choose-template/", views.template_select, name="template_select"),
    path("preview/<str:template_id>/", views.template_preview, name="template_preview"),
    path("signup/", views.tenant_signup, name="tenant_signup"),
    path("about/", views.company_about, name="about")
]