"""
URL configuration for ci_loan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('LoginAuth.urls')),
    path('permissions/',include('LoginAuth.rbac_urls')),
    path('approval/',include('LoginAuth.am_urls')),
    path('master/',include('Masters.urls')),
    # path('schrduler/',include('Masters.schrduler_urls')),
    path('profile/',include('CompanyProfile.urls')),
    path('user/',include('UserManagement.urls')),
    path('LoanInquiry/',include('InquiryLoanProcess.urls')),
    path('DisSetSys/',include('DisSetSystem.urls')),
    path('InquiryAction/',include('InquiryAction.urls')),
    path('AuditTrail/',include('AuditTrail.urls')),
    path('CustomSettings/',include('CustomSettings.urls')),
    path('Auction/',include('Auction.urls')),
    path('KycVerification/',include('KycVerification.urls')),
    path('FieldMapping/',include('FieldMapping.urls')),
    path('CiLoanCore/',include('CiLoanCore.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)