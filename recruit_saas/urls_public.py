from django.urls import include, path
from marketing import views

app_name = "public_marketing"

urlpatterns = [
    path('', include('marketing.urls')),
    path('customers/', include('customers.urls')),
]