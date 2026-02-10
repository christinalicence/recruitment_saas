from django.urls import path, include
from django.contrib import admin
from marketing import views as marketing_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Auth handled by Marketing views (shared logic)
    path('login/', marketing_views.tenant_login, name='tenant_login'),
    path('logout/', marketing_views.tenant_logout, name='tenant_logout'),
    
    # CMS handles the core tenant site (Home, About, Jobs, Dashboard)
    path('', include('cms.urls')),

    # Billing & Admin
    path('billing/', include('customers.urls', namespace='customers')),
    path('admin/', admin.site.urls),

    # Marketing support routes needed on subdomains
    path('choose-template/', marketing_views.template_select, name='template_select'),
    path('find-portal/', marketing_views.portal_finder, name='portal_finder'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)