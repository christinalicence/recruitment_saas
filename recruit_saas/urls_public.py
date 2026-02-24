from django.contrib import admin
from django.urls import include, path
from marketing import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customers/', include('customers.urls')),
    path('choose-template/', views.template_select, name='template_select'),
    path('preview/<str:template_id>/', views.template_preview, name='template_preview'),
    path('signup/', views.tenant_signup, name='tenant_signup'),
    path('find-portal/', views.portal_finder, name='portal_finder'),
    path('about/', views.company_about, name='about'),
    # Root page - must be last
    path('', views.landing_page, name='landing'),
]

app_name = 'public_marketing'
