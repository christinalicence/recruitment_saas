
from django.contrib import admin
from django.urls import path, include
from marketing import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('marketing.urls', 'marketing'), namespace='public_marketing')),
]
