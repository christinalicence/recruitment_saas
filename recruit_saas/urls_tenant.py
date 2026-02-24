from django.urls import path, include
from django.contrib import admin
from marketing import views as marketing_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', marketing_views.tenant_login, name='tenant_login'),
    path('logout/', marketing_views.tenant_logout, name='tenant_logout'),
    path('', include('cms.urls')),
    path('about/', marketing_views.company_about, name='about'),
    path('choose-template/', marketing_views.template_select, name='template_select'),
    path('find-portal/', marketing_views.portal_finder, name='portal_finder'),
    path('billing/', include('customers.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
