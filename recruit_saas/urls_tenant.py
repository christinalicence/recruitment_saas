from django.urls import path, include
from django.contrib import admin
from marketing import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.tenant_login, name='tenant_login'),
    path('logout/', views.tenant_logout, name='tenant_logout'),
    
    # We need to provide 'landing' so base.html logo doesn't crash
    path('', include('cms.urls')),
    path('dashboard/', include('cms.urls'), name='landing'), 

    # Dummy routes to keep shared navbar happy
    path('choose-template/', views.template_select, name='template_select'),
    path('about/', views.about_page, name='about'),
    path('find-portal/', views.portal_finder, name='portal_finder'),

    path('billing/', include('customers.urls', namespace='customers')),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)