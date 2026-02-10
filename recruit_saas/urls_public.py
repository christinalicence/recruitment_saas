from django.urls import include, path
from marketing import views

app_name = "public_marketing"

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("choose-template/", views.template_select, name="template_select"),
    path("preview/<str:template_id>/", views.template_preview, name="template_preview"),
    path("signup/", views.tenant_signup, name="tenant_signup"),
    path('customers/', include('customers.urls')),
    path("about/", views.company_about, name="about")
]