from django.urls import *
from .views import *

urlpatterns = [
    #--------------------Followup api urls -----------------------
    path('createFollowup/',createFollowup),
    path('updateFollowup/<int:pk>/',updateFollowup),
    path('deleteFollowup/<int:pk>/',deleteFollowup),
    path('getAllFollowups/',getAllFollowups),

    #--------------------Assign api urls -----------------------
    path('createAssign/',createAssign),
    path('updateAssign/<int:pk>/',updateAssign),
    path('getAllAssign/',getAllAssign),

    #--------------------InquiryNote api urls -----------------------
    path('createInquiryNote/',createInquiryNote),
    path('updateInquiryNote/<int:pk>/',updateInquiryNote),
    path('deleteInquiryNote/<int:pk>/', deleteInquiryNote),
    path('getAllInquiryNotes/', getAllInquiryNotes),

    #--------------------SpecialNote api urls -----------------------
    path('createSpecialNote/',createSpecialNote),
    path('updateSpecialNote/<int:pk>/',updateSpecialNote),
    path('deleteSpecialNote/<int:pk>/', deleteSpecialNote),
    path('getAllSpecialNotes/', getAllSpecialNotes),

    
    path('createVerification/',createVerification),
    path('updateVerification/<int:pk>/',updateVerification),
    path('deleteVerification/<int:pk>/', deleteVerification),
    # path('getAllSpecialNotes/', getVerificationById),
    path('viewAllVerifications/', viewAllVerifications),


    path('upload-documents/', upload_documents, name='upload-documents'),
    path('document-uploads/', get_document_uploads, name='get-document-uploads'),


]