from django.urls import path, include
from django.urls import path, include
from marketing import views
from django.contrib import admin

urlpatterns = [
    # Wrap these in the 'public_marketing' namespace to match the public urls.py
    path('', include(([
        path("login/", views.tenant_login, name="tenant_login"),
        path('logout/', views.tenant_logout, name='tenant_logout'),
    ], 'public_marketing'))),
    
    path('', include(('cms.urls', 'cms'), namespace='cms')),
    path('admin/', admin.site.urls),
]