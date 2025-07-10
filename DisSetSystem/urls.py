from django.urls import path
from .views import *

urlpatterns = [ 
    #------------------ Disbursment apis -------
    
    path('createDisbursment/', createDisbursment),
    path('updateDisbursment/<int:disbursement_id>/', updateDisbursment),
    path('getDisbursmentById/<int:disbursement_id>/', getDisbursmentById),
    path('getAllDisbursment/',getAllDisbursment),
    path('deleteDisbursment/<int:disbursement_id>/',deleteDisbursment),

    #------------------ RepaymentSchedule apis -------
    
    path('createRepaymentSchedule/', createRepaymentSchedule),
    path('updateRepaymentSchedule/<int:pk>/', updateRepaymentSchedule),
    path('getRepaymentScheduleById/<int:pk>/', getRepaymentScheduleById),
    path('getAllRepaymentSchedules/',getAllRepaymentSchedules),
    path('deleteRepaymentSchedule/<int:pk>/',deleteRepaymentSchedule),


    #------------------ PaymentCollection apis -------
    
    path('createPaymentCollection/', createPaymentCollection),
    path('updatePaymentCollection/<int:pk>/', updatePaymentCollection),
    path('getPaymentCollectionById/<int:pk>/', getPaymentCollectionById),
    path('getAllPaymentCollections/',getAllPaymentCollections),
    path('deletePaymentCollection/<int:pk>/',deletePaymentCollection),

    #------------------ LoanClosure apis -------
    
    path('createLoanClosure/', createLoanClosure),
    path('updateLoanClosure/<int:pk>/', updateLoanClosure),
    path('getLoanClosureById/<int:pk>/', getLoanClosureById),
    path('getAllLoanClosures/',getAllLoanClosures),
    path('deleteLoanClosure/<int:pk>/',deleteLoanClosure),

    #------------------ LoanForeclosures apis -------
    
    path('createLoanForeclosure/', createLoanForeclosure),
    path('updateLoanForeclosure/<int:pk>/', updateLoanForeclosure),
    path('getLoanForeclosureById/<int:pk>/', getLoanForeclosureById),
    path('getAllLoanForeclosures/',getAllLoanForeclosures),
    path('deleteLoanForeclosure/<int:pk>/',deleteLoanForeclosure),


    #------------------ LoanRenewal apis -------
    
    path('createLoanRenewal/', createLoanRenewal),
    path('updateLoanRenewal/<int:pk>/', updateLoanRenewal),
    path('getLoanRenewalById/<int:pk>/', getLoanRenewalById),
    path('getAllLoanRenewals/',getAllLoanRenewals),
    path('deleteLoanRenewal/<int:pk>/',deleteLoanRenewal),

    #------------------ AutoSquareOff apis -------
    
    path('createAutoSquareOff/', createAutoSquareOff),
    path('updateAutoSquareOff/<int:pk>/', updateAutoSquareOff),
    path('getAutoSquareOffById/<int:pk>/', getAutoSquareOffById),
    path('getAllAutoSquareOffs/',getAllAutoSquareOffs),
    path('deleteAutoSquareOff/<int:pk>/',deleteAutoSquareOff),

 
    #------------------ EMICollectionAdjustment  apis -------
    
    path('createEMICollection/', create_emi_collection),
    path('updateEMICollection/<int:pk>/', update_emi_collection),
    path('getEMICollectionById/<int:pk>/', get_emi_collection_by_id),
    path('getAllEMICollection/',get_all_emi_collections),
    path('DeleteEMICollection/<int:pk>/',delete_emi_collection),
]
