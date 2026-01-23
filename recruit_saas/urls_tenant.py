from django.urls import path, include
from marketing import views
from django.contrib import admin
from marketing.views import tenant_logout

urlpatterns = [
    path("login/", views.tenant_login, name="tenant_login"),
    path('logout/', tenant_logout, name='tenant_logout'), # Now the tenant knows what 'tenant_logout' is!
    path('', include(('cms.urls', 'cms'), namespace='cms')),
    path('admin/', admin.site.urls),
]