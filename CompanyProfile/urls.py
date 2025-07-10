from django.urls import path
from .views import *    

urlpatterns = [
    #--------------------Profile api urls -----------------------
    path('createCompanyprofile/', create_company_profile, name='create_company_profile'),
    path('updateCompanyProfile/<int:pk>/', update_company_profile, name='update_company_profile'),
    path('getCompanyProfileById/<int:pk>/', getCompanyProfileById),
    path('getCompanyProfile/',getCompanyProfile),
]