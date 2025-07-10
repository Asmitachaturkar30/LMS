# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('createCustomSetting/', createCustomSetting),
    path('updateCustomSetting/<int:pk>/', updateCustomSetting),
    path('deleteCustomSetting/<int:pk>/', deleteCustomSetting),
    path('getAllCustomSettings/', getAllCustomSettings),
    path('getCustomSettingById/<int:pk>/', getCustomSettingById),
    # path('updateCustomSettingPartial/<int:pk>/', updateCustomSettingPartial),

]
