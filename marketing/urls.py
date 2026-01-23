from django.urls import path
from . import views

app_name = 'public_marketing'

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("login/", views.tenant_login, name="tenant_login"),
    path("logout/", views.tenant_logout, name="tenant_logout"),
    path("choose-template/", views.template_select, name="template_select"),
    path("preview/<str:template_id>/", views.template_preview, name="template_preview"),
    path("signup/", views.tenant_signup, name="tenant_signup"),
    path('about/', views.about_page, name='about'),
]