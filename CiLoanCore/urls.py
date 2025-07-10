from django.urls import path
from .views import *

urlpatterns = [
    path('send-whatsapp/',send_whatsapp_message),
    path('send_email/',send_email)
]

