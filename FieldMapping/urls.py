from django.urls import path
from .views import * 

urlpatterns=[
    path('getFieldMappings/',getFieldMappings),
    path('updateFieldLabel/',updateFieldLabel),
    # path('deleteFieldLabel/',deleteFieldLabel),
]