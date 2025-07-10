from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination

#============================= Response helper functions ===============================

def validation_error_response(errors):
    error_messages = []
    for field, field_errors in errors.items():
        error_messages.append(f"{field}: {', '.join(field_errors)}")
    
    return JsonResponse({
        "result": False,
        "message": "Validation failed",
        "errors": ". ".join(error_messages)
    }, status=status.HTTP_400_BAD_REQUEST)

def not_found_response(message):
    return JsonResponse({
        "result": False,
        "message": message
    }, status=status.HTTP_404_NOT_FOUND)

def server_error_response(error):
    return JsonResponse({
        "result": False,
        "message": "Internal server error",
        "error": str(error)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def success_response(data=None, message="Success"):
    response = {
        "result": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return JsonResponse(response, status=status.HTTP_200_OK)

def created_response(data, message="Resource created successfully"):
    return JsonResponse({
        "result": True,
        "message": message,
        "data": data
    }, status=status.HTTP_201_CREATED)

def no_content_response(message="Resource deleted successfully"):
    return JsonResponse({
        "result": True,
        "message": message
    }, status=status.HTTP_204_NO_CONTENT)


#============================= Followup Apis ===============================

# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createFollowup(request):
    try:
        serializer = FollowUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "FollowUp created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateFollowup(request, pk):
    try:
        # Step 1: Fetch the FollowUp record by primary key
        followup = FollowUp.objects.filter(pk=pk).first()
        if not followup:
            return not_found_response(followup if followup else type('FollowUp', (), {'id': pk})())

        # Step 2: Copy request data and set UpdateBy
        data = request.data.copy()
        data["UpdateBy"] = request.user.email  # Optional audit field

        # Step 3: Validate and update using serializer
        serializer = FollowUpSerializer(followup, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "FollowUp updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteFollowup(request, pk):
    try:
        followup = FollowUp.objects.get(pk=pk)
        followup.delete()
        return no_content_response("FollowUp deleted successfully")
    except FollowUp.DoesNotExist:
        return not_found_response("FollowUp not found")
    except Exception as e:
        return server_error_response(e)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllFollowups(request):
    try:
        followups = FollowUp.objects.all()
        serializer = FollowUpSerializer(followups, many=True)
        return success_response(serializer.data, "FollowUp list fetched successfully")
    except Exception as e:
        return server_error_response(e)

#============================= Assign Apis ===============================

# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createAssign(request):
    try:
        serializer = AssignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Assign created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllAssign(request):
    try:
        assigns = Assign.objects.all()
        serializer = AssignSerializer(assigns, many=True)
        return success_response(serializer.data, "Assign list fetched successfully")
    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateAssign(request, pk):
    try:
        # Step 1: Fetch the Assign record by primary key
        assign_obj = Assign.objects.filter(pk=pk).first()
        if not assign_obj:
            return not_found_response(assign_obj if assign_obj else type('Assign', (), {'id': pk})())

        # Step 2: Copy and modify update data
        data = request.data.copy()
        data['UpdateBy'] = request.user.email  # Optional audit tracking

        # Step 3: Validate and update using serializer
        serializer = AssignSerializer(assign_obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Assign updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

#============================= InquiryNote Apis ===============================

# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createInquiryNote(request):
    try:
        serializer = InquiryNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Inquiry Note created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateInquiryNote(request, pk):
    try:
        # Step 1: Check if InquiryNote exists
        note = InquiryNote.objects.get(pk=pk)

        # Step 2: Validate unexpected fields
        allowed_fields = set(InquiryNoteSerializer().get_fields().keys())
        invalid_fields = set(request.data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Validate and update
        serializer = InquiryNoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Inquiry Note updated successfully")
        
        return validation_error_response(serializer.errors)

    except InquiryNote.DoesNotExist:
        return not_found_response("Inquiry Note not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteInquiryNote(request, pk):
    try:
        note = InquiryNote.objects.get(pk=pk)
        note.delete()
        return success_response(message="InquiryNote deleted successfully")
    except InquiryNote.DoesNotExist:
        return not_found_response("InquiryNote not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllInquiryNotes(request):
    try:
        notes = InquiryNote.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(notes, request)

        serializer = InquiryNoteSerializer(notes, many=True)
        return success_response(serializer.data, "InquiryNotes fetched successfully")
    except Exception as e:
        return server_error_response(e)
    

#============================= SpecialNote Apis ===============================

# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createSpecialNote(request):
    try:
        serializer = SpecialNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Special Note created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateSpecialNote(request, pk):
    try:
        # Step 1: Check if SpecialNote exists
        note = SpecialNote.objects.get(pk=pk)

        # Step 2: Validate unexpected fields
        allowed_fields = set(SpecialNoteSerializer().get_fields().keys())
        invalid_fields = set(request.data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Validate and update
        serializer = SpecialNoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Special Note updated successfully")
        
        return validation_error_response(serializer.errors)

    except SpecialNote.DoesNotExist:
        return not_found_response("Special Note not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteSpecialNote(request, pk):
    try:
        note = SpecialNote.objects.get(pk=pk)
        note.delete()
        return success_response(message="Special Note deleted successfully")
    except SpecialNote.DoesNotExist:
        return not_found_response("Special Note not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllSpecialNotes(request):
    try:
        notes = SpecialNote.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(notes, request)

        serializer = SpecialNoteSerializer(notes, many=True)
        return success_response(serializer.data, "Special Notes fetched successfully")
    except Exception as e:
        return server_error_response(e)
    


#============================= Verification Apis ===============================

# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createVerification(request):
    try:
        data = request.data.copy()
        data['CreateBy'] = request.user.username

        serializer = VerificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Verification created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateVerification(request, pk):
    try:
        # Step 1: Check if Verification exists
        instance = Verification.objects.get(pk=pk)

        # Step 2: Validate unexpected fields
        allowed_fields = set(VerificationSerializer().get_fields().keys())
        invalid_fields = set(request.data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Add audit info
        data = request.data.copy()
        data['update_by'] = request.user.username

        # Step 4: Validate and save
        serializer = VerificationSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Verification updated successfully")
        
        return validation_error_response(serializer.errors)

    except Verification.DoesNotExist:
        return not_found_response("Verification not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteVerification(request, pk):
    try:
        instance = Verification.objects.get(pk=pk)
        instance.delete()
        return success_response(message="Verification deleted successfully")
    except Verification.DoesNotExist:
        return not_found_response("Verification not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllVerifications(request):
    try:
        verifications = Verification.objects.all().order_by('-CreatedAt')
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(verifications, request)

        serializer = VerificationSerializer(verifications, many=True)
        return success_response(serializer.data, "Verifications retrieved successfully")
    except Exception as e:
        return server_error_response(e)
    



# views.py
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db import transaction
from .serializers import DocumentUploadSerializer

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_documents(request):
    """
    Upload multiple documents with validation
    """
    try:
        with transaction.atomic():
            serializer = DocumentUploadSerializer(data=request.data)
            
            if serializer.is_valid():
                # Save the document upload with files
                document_upload = serializer.save()
                
                # Return response with created data
                response_serializer = DocumentUploadSerializer(document_upload)
                return Response({
                    'success': True,
                    'message': 'Documents uploaded successfully',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while uploading documents',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_document_uploads(request):
    """
    Get all document uploads with files
    """
    try:
        document_uploads = DocumentUpload.objects.all().order_by('-created_at')
        serializer = DocumentUploadSerializer(document_uploads, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching documents',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
