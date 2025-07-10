from django.urls import path
from .views import *

urlpatterns = [
    path('verify_aadhaar/',verify_aadhaar),
    path('verify_pan/',verify_pan),
    path('verifyDrivingLicense/',verifyDrivingLicense),
    path('verifyVoterId/',verify_voter_id),
    path('verifyBank/',verify_bank),
    path('verifyElectricityBill/',verify_electricity_bill),
    path('verifyITR_V/',verify_itr_v),
    path('verifyITRCompliance/',verify_itr_compliance),
    path('creditReportCibil/',credit_report_cibil),
    path('CreditReportCibilPdf/',fetch_credit_report_cibil_pdf),
    path('digilocker_initialize/',digilocker_initialize),
    path('digilocker_list_documents/<str:client_id>/',digilocker_list_documents),
    path('digilocker_download_document/<str:client_id>/<str:file_id>/', digilocker_download_document,),
]