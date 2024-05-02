from django.urls import path
from .views import USSDSession, ussd_endpoint, process_input

urlpatterns = [
    path('', ussd_endpoint, name = 'endpoint')
]