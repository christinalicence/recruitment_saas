from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # This includes the marketing urls ONLY for the public site
    path('', include('marketing.urls')), 
]