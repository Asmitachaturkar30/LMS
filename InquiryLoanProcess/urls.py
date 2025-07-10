from django.urls import path
from .views import *


urlpatterns = [
    #--------- FULL KYC Apis --------------------
    path('createKYC/', create_full_kyc),
    path('updateKYC/<int:kyc_id>/', update_full_kyc),
    path('viewAllKyc/', viewAllKyc),

    #---------------------- Approval apis -----------------

    path('createApproval/', createApproval),
    path('updateApproval/<int:pk>/', updateApproval),
    path('deleteApproval/<int:pk>/',deleteApproval),
    path('getApprovalById/<int:pk>/', getApprovalById),
    path('viewAllApprovel/', viewAllApprovals),

    #------------------ Foreclosure apis -------
    path('createForeclosure/', createForeclosure),
    path('updateForeclosure/<int:pk>/', updateForeclosure),
    path('deleteForeclosure/<int:pk>/',deleteForeclosure),
    path('getForeclosureById/<int:pk>/', getForeclosureById),
    path('viewAllForeclosures/', viewAllForeclosures),

    #------------------ EMI apis -------
    
    path('createEMI/', createEMI),
    path('updateEMI/<int:pk>/', updateEMI),
    path('deleteEMI/<int:pk>/',deleteEMI),
    path('getEmiById/<int:pk>/', getEmiById),
    path('viewAllEMI/', viewAllEMI),

    #------------------ Penalty apis -------
    
    path('createPenalty/', createPenalty),
    path('updatePenalty/<int:pk>/', updatePenalty),
    path('deletePenalty/<int:pk>/',deletePenalty),
    path('getPenaltyById/<int:pk>/', getPenaltyById),
    path('viewAllPenalty/', viewAllPenalty),


    #------------------ DisbursementInfo apis -------
    
    path('createDisbursementInfo/', createDisbursementInfo),
    path('updateDisbursementInfo/<int:pk>/', updateDisbursementInfo),
    path('getDisbursementInfoById/<int:pk>/', getDisbursementInfoById),
    path('viewAllDisbursementInfo/',viewAllDisbursementInfo),
    path('deleteDisbursementInfo/<int:pk>/',deleteDisbursementInfo),


    #------------------ Inquiry apis -------
    
    path('createInquiry/', createInquiry),
    path('updateInquiry/<int:pk>/', updateInquiry),
    path('getInquiryById/<int:pk>/', getInquiryById),
    path('getAllInquiries/',getAllInquiries),
    path('deleteInquiry/<int:pk>/',deleteInquiry),


    #------------------ LoanApplication apis -------
    
    path('createLoanApplication/', createLoanApplication),
    path('updateLoanApplication/<int:pk>/', updateLoanApplication),
    path('getLoanApplicationById/<int:pk>/', getLoanApplicationById),
    path('getAllLoanApplications/',getAllLoanApplications),
    path('deleteLoanApplication/<int:pk>/',deleteLoanApplication),
]
