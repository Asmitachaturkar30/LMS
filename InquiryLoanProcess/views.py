from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import *
from .serializers import *
from django.core.exceptions import ValidationError
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


#============================= Inquiry Apis ===============================

# API Views
@api_view(['POST'])
@permission_classes([])
def createInquiry(request):
    try:
        # Validate unknown fields
        allowed_fields = set(InquiryModelSerializer().fields.keys())
        input_fields = set(request.data.keys())
        unknown_fields = input_fields - allowed_fields
        if unknown_fields:
            return JsonResponse({
                "result": False,
                "message": f"Unknown field(s) provided: {', '.join(unknown_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate Aadhaar
        aadhaar = request.data.get('AadhaarNumber')
        if aadhaar and NewInquiry.objects.filter(AadhaarNumber=aadhaar).exists():
            return JsonResponse({
                "result": False,
                "message": "Duplicate AadhaarNumber found. Record already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = InquiryModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Inquiry created successfully")
        return validation_error_response(serializer.errors)

    except ValidationError as ve:
        return validation_error_response(ve.message_dict if hasattr(ve, 'message_dict') else {'error': str(ve)})
    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateInquiry(request, pk):
    try:
        # Step 1: Fetch the inquiry record by primary key
        inquiry = NewInquiry.objects.filter(pk=pk).first()
        if not inquiry:
            return not_found_response(inquiry if inquiry else type('NewInquiry', (), {'id': pk})())

        # Step 2: Prepare data (don't add UpdateBy to data directly)
        data = request.data.copy()

        # Step 3: Aadhaar uniqueness check
        aadhaar = data.get("AadhaarNumber")
        if aadhaar and NewInquiry.objects.filter(AadhaarNumber=aadhaar).exclude(pk=pk).exists():
            return JsonResponse({
                "result": False,
                "message": "Duplicate AadhaarNumber found. Record already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Validate unexpected fields
        allowed_fields = set(InquiryModelSerializer().get_fields().keys())
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                "result": False,
                "message": f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 5: Serialize and update
        serializer = InquiryModelSerializer(inquiry, data=data, partial=True)
        if serializer.is_valid():
            updated_instance = serializer.save()
            updated_instance.UpdateBy = request.user.username  # Set manually
            updated_instance.save()  # Save again after setting
            return success_response(serializer.data, "Inquiry updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(['DELETE'])
@permission_classes([])
def deleteInquiry(request, pk):
    try:
        inquiry = NewInquiry.objects.get(pk=pk)
        inquiry.delete()
        return success_response(message="Inquiry deleted successfully")
    except NewInquiry.DoesNotExist:
        return not_found_response("Inquiry with the given ID does not exist")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getInquiryById(request, pk):
    try:
        inquiry = NewInquiry.objects.get(pk=pk)
        serializer = InquiryModelSerializer(inquiry)
        return success_response(serializer.data, "Inquiry retrieved successfully")
    except NewInquiry.DoesNotExist:
        return not_found_response("Inquiry with the given ID does not exist")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllInquiries(request):
    try:
        inquiries = NewInquiry.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(inquiries, request)

        serializer = InquiryModelSerializer(inquiries, many=True)
        return success_response(serializer.data, "Inquiries retrieved successfully")
    except Exception as e:
        return server_error_response(e)
    
    

#============================= LoanApplication Apis ===============================

# API Views
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def createLoanApplication(request):
#     try:
#         data = request.data.copy()
#         serializer = LoanApplicationModelSerializer(data=data)
        
#         if serializer.is_valid():
#             # Manual model clean() validations
#             instance = LoanApplication(**serializer.validated_data)
#             try:
#                 instance.clean()
#             except ValidationError as ve:
#                 return validation_error_response(ve.message_dict)
            
#             instance.save()
#             serialized = LoanApplicationModelSerializer(instance)
#             return created_response(serialized.data, "Loan Application created successfully")
        
#         return validation_error_response(serializer.errors)

#     except Exception as e:
#         return server_error_response(e)

from rest_framework.parsers import MultiPartParser, FormParser
from .models import LoanApplicationAttachment  # Assuming you've added this model

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def createLoanApplication(request):
    try:
        data = request.data.copy()
        files = request.FILES.getlist('MoreAttachmentFile')  # Accept multiple files with same key
        inquiry_id = data.get("InquiryId")

        if not inquiry_id:
            return validation_error_response({"InquiryId": "InquiryId is required"})

        try:
            inquiry = NewInquiry.objects.get(pk=inquiry_id)
        except NewInquiry.DoesNotExist:
            return not_found_response("Inquiry not found")

        # Auto-fill data from inquiry
        auto_fields = [
            "FirstName", "MiddleName", "LastName", "Gender", "MaritalStatus", "DateOfBirth",
            "PhoneNumber", "AlternatePhoneNumber", "EmailAddress", "FathersMothersName",
            "AddressLine1", "AddressLine2", "City", "State", "Pincode", "Country", "Landmark",
            "AddressType", "DurationAtAddress"
        ]
        for field in auto_fields:
            data[field] = getattr(inquiry, field)

        serializer = LoanApplicationModelSerializer(data=data)
        
        if serializer.is_valid():
            instance = LoanApplication(**serializer.validated_data)
            try:
                instance.clean()
            except ValidationError as ve:
                return validation_error_response(ve.message_dict)

            instance.save()

            # ✅ Save multiple attachments
            for file in files:
                LoanApplicationAttachment.objects.create(Loan=instance, File=file)

            serialized = LoanApplicationModelSerializer(instance)
            return created_response(serialized.data, "Loan Application created successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)



@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def updateLoanApplication(request, pk):
    try:
        # Validate required context fields
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")
        Product_id =  request.data.get("ProductId")
        Inquiry_id = request.data.get("InquiryId")

        if not Owner_id or not branch_id or not department_id and Product_id and Inquiry_id:
            return JsonResponse({
                "result": False,
                "message": "OwnerId, BranchId and DepartmentId ,ProductId, InquiryId are required for update."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get LoanApplication object with context
        try:
            loan_app = LoanApplication.objects.get(pk=pk, OwnerId=Owner_id, BranchId=branch_id, DepartmentId=department_id, ProductId=Product_id, InquiryId=Inquiry_id)
        except LoanApplication.DoesNotExist:
            return not_found_response("Loan Application not found for given BranchId and DepartmentId,ProductId")

        # Prepare update data
        data = request.data.copy()
        # Remove context fields that shouldn't be updated
        for field in ["OwnerId", "BranchId", "DepartmentId", "ProductId", "InquiryId"]:
            data.pop(field, None)

        # Handle file fields - only update if new files are provided
        file_fields = [
            'GuarantorPANCardCopy', 
            'GuarantorAadhaarCardCopy', 
            'GuarantorBankStatement',
            'MoreAttachmentFile'
        ]
        for field in file_fields:
            if field not in request.FILES:
                data.pop(field, None)  # Remove field if no new file is provided


        # Check for unexpected fields
        allowed_fields = set(LoanApplicationModelSerializer().get_fields().keys()) - {"OwnerId", "BranchId", "DepartmentId","ProductId","InquiryId"}
        unknown_fields = set(data.keys()) - allowed_fields
        if unknown_fields:
            return JsonResponse({
                "result": False,
                "message": f"Unexpected field(s): {', '.join(unknown_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate and update
        serializer = LoanApplicationModelSerializer(loan_app, data=data, partial=True)
        if serializer.is_valid():
            try:
                updated_instance = LoanApplication(**{**serializer.validated_data, 'id': loan_app.id})
                updated_instance.clean()
            except ValidationError as ve:
                return validation_error_response(ve.message_dict)
            
            serializer.save()
            return success_response(serializer.data, "Loan Application updated successfully")
        
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllLoanApplications(request):
    try:
        all_data = LoanApplication.objects.all().order_by("-id")
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(all_data, request)

        serializer = LoanApplicationModelSerializer(all_data, many=True)
        return success_response(serializer.data, "All LoanApplications fetched successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getLoanApplicationById(request, pk):
    try:
        instance = LoanApplication.objects.get(pk=pk)
        serializer = LoanApplicationModelSerializer(instance)
        return success_response(serializer.data, "LoanApplication fetched successfully")
    except LoanApplication.DoesNotExist:
        return not_found_response("LoanApplication not found")
    except Exception as e:
        return server_error_response(e)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteLoanApplication(request, pk):
    try:
        instance = LoanApplication.objects.get(pk=pk)
        instance.delete()
        return success_response(message="LoanApplication deleted successfully")
    except LoanApplication.DoesNotExist:
        return not_found_response("LoanApplication not found")
    except Exception as e:
        return server_error_response(e)


#============================= Full_kyc Apis ===============================

# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_full_kyc(request):
    try:
        required_fields = ['PANCard', 'AadhaarCard', 'BankStatement', 'CreateBy', 'UpdateBy']
        missing_fields = [field for field in required_fields if field not in request.data or request.data[field] in [None, '']]
        
        if missing_fields:
            return JsonResponse({
                "result": False,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate PAN + Aadhaar
        existing = Full_KYC.objects.filter(
            PANCard=request.FILES.get('PANCard'),
            AadhaarCard=request.FILES.get('AadhaarCard')
        ).first()
        if existing:
            return JsonResponse({
                "result": False,
                "message": "Duplicate KYC record found with same PAN and Aadhaar"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = FullKYCSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "KYC created successfully")
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

from rest_framework.parsers import MultiPartParser, FormParser

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_full_kyc(request, kyc_id):
    try:
        # Step 1: Fetch KYC instance by primary key
        kyc_instance = Full_KYC.objects.filter(pk=kyc_id).first()
        if not kyc_instance:
            return not_found_response(kyc_instance if kyc_instance else type('Full_KYC', (), {'id': kyc_id})())

        # Step 2: Prepare update data
        data = request.data.copy()
        data['UpdateBy'] = request.user.email  # Optional audit tracking

        # Optional: Check for duplicate PAN + Aadhaar
        pan = request.FILES.get('PANCard') or data.get('PANCard')
        aadhaar = request.FILES.get('AadhaarCard') or data.get('AadhaarCard')
        if pan and aadhaar:
            is_duplicate = Full_KYC.objects.filter(
                PANCard=pan,
                AadhaarCard=aadhaar
            ).exclude(pk=kyc_id).exists()

            if is_duplicate:
                return JsonResponse({
                    "result": False,
                    "message": "Duplicate KYC record with same PAN and Aadhaar exists"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Validate and update
        serializer = FullKYCSerializer(kyc_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "KYC updated successfully")
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllKyc(request):
    try:
        kyc_records = Full_KYC.objects.all().order_by('-id')
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(kyc_records, request)

        serializer = FullKYCSerializer(kyc_records, many=True)
        return success_response(serializer.data, "All KYC records fetched successfully")
    except Exception as e:
        return server_error_response(e)
    

#============================= Approval Apis ===============================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createApproval(request):
    try:
        data = request.data.copy()
        data['CreateBy'] = request.user.username
        data['UpdateBy'] = request.user.username

        serializer = ApprovalSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Approval created successfully')

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateApproval(request, pk):
    try:
        # Step 1: Fetch the Approval record by primary key
        instance = ApprovalInfo.objects.filter(pk=pk).first()
        if not instance:
            return not_found_response(instance if instance else type('ApprovalInfo', (), {'id': pk})())

        # Step 2: Prepare update data
        data = request.data.copy()
        data['UpdateBy'] = request.user.username  # Optional audit trail

        # Step 3: Validate and update
        serializer = ApprovalSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Approval updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllApprovals(request):
    """
    Get all approval records
    """
    try:
        approvals = ApprovalInfo.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(approvals, request)

        serializer = ApprovalSerializer(approvals, many=True)
        return success_response(serializer.data, 'Approvals retrieved successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getApprovalById(request, pk):
    """
    Get approval by ID
    """
    try:
        approval = ApprovalInfo.objects.get(pk=pk)
        serializer = ApprovalSerializer(approval)
        return success_response(serializer.data, 'Approval retrieved successfully')
    except ApprovalInfo.DoesNotExist:
        return not_found_response('Approval not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteApproval(request, pk):
    """
    Delete approval by ID
    """
    try:
        approval = ApprovalInfo.objects.get(pk=pk)
        approval.delete()
        return success_response(message='Approval deleted successfully')
    except ApprovalInfo.DoesNotExist:
        return not_found_response('Approval not found')
    except Exception as e:
        return server_error_response(e)



#============================= Foreclosure Apis ===============================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createForeclosure(request):
    """
    Create a new Foreclosure entry
    """
    try:
        data = request.data.copy()
        data['createBy'] = request.user.username
        data['updateBy'] = request.user.username

        serializer = ForeclosureSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Foreclosure created successfully')

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def updateForeclosure(request, pk):
    try:
        # Step 1: Retrieve the Foreclosure instance
        instance = Foreclosure.objects.filter(pk=pk).first()
        if not instance:
            return not_found_response(instance if instance else type('Foreclosure', (), {'id': pk})())

        # Step 2: Prepare data
        data = request.data.copy()
        data['UpdateBy'] = request.user.username  # Track updater

        # Step 3: Serialize and update
        serializer = ForeclosureSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Foreclosure updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllForeclosures(request):
    """
    Retrieve all foreclosure records
    """
    try:
        foreclosures = Foreclosure.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(foreclosures, request)

        serializer = ForeclosureSerializer(foreclosures, many=True)
        return success_response(serializer.data, 'Foreclosures retrieved successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getForeclosureById(request, pk):
    """
    Retrieve a foreclosure record by ID
    """
    try:
        foreclosure = Foreclosure.objects.get(pk=pk)
        serializer = ForeclosureSerializer(foreclosure)
        return success_response(serializer.data, 'Foreclosure retrieved successfully')
    except Foreclosure.DoesNotExist:
        return not_found_response('Foreclosure not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteForeclosure(request, pk):
    """
    Delete a foreclosure record by ID
    """
    try:
        foreclosure = Foreclosure.objects.get(pk=pk)
        foreclosure.delete()
        return success_response(message='Foreclosure deleted successfully')
    except Foreclosure.DoesNotExist:
        return not_found_response('Foreclosure not found')
    except Exception as e:
        return server_error_response(e)


#============================= EMI Apis ===============================


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createEMI(request):
    try:
        data = request.data.copy()
        data['CreateBy'] = request.user.username
        data['UpdateBy'] = request.user.username

        serializer = EMISetupSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'EMI setup created successfully')

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateEMI(request, pk):
    try:
        # Step 1: Find EMISetup record by primary key
        instance = EMISetup.objects.filter(pk=pk).first()
        if not instance:
            return not_found_response(instance if instance else type('EMISetup', (), {'id': pk})())

        # Step 2: Prepare data
        data = request.data.copy()
        data['UpdateBy'] = request.user.username  # Track updater

        # Step 3: Serialize and update
        serializer = EMISetupSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "EMI Setup updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllEMI(request):
    """
    Retrieve all EMI setup records
    """
    try:
        emis = EMISetup.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(emis, request)

        serializer = EMISetupSerializer(emis, many=True)
        return success_response(serializer.data, 'EMI setups retrieved successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getEmiById(request, pk):
    """
    Retrieve EMI setup record by ID
    """
    try:
        emi = EMISetup.objects.get(pk=pk)
        serializer = EMISetupSerializer(emi)
        return success_response(serializer.data, 'EMI setup retrieved successfully')
    except EMISetup.DoesNotExist:
        return not_found_response('EMI setup not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteEMI(request, pk):
    """
    Delete EMI setup record by ID
    """
    try:
        emi = EMISetup.objects.get(pk=pk)
        emi.delete()
        return success_response(message='EMI setup deleted successfully')
    except EMISetup.DoesNotExist:
        return not_found_response('EMI setup not found')
    except Exception as e:
        return server_error_response(e)



#============================= Penalty Apis ===============================


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createPenalty(request):
    try:
        data = request.data.copy()
        data['createBy'] = request.user.username
        data['updateBy'] = request.user.username

        serializer = PenaltySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Penalty created successfully')

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def updatePenalty(request, pk):
    try:
        # Step 1: Get the record
        instance = Penalty.objects.filter(pk=pk).first()
        if not instance:
            return not_found_response(instance if instance else type('Penalty', (), {'id': pk})())

        # Step 2: Prepare update data
        data = request.data.copy()
        data['UpdateBy'] = request.user.username  # Track updater

        # Step 3: Serialize and save
        serializer = PenaltySerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Penalty updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllPenalty(request):
    """
    Retrieve all penalty records
    """
    try:
        penalties = Penalty.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(penalties, request)

        serializer = PenaltySerializer(penalties, many=True)
        return success_response(serializer.data, 'Penalties retrieved successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPenaltyById(request, pk):
    """
    Retrieve penalty by ID
    """
    try:
        penalty = Penalty.objects.get(pk=pk)
        serializer = PenaltySerializer(penalty)
        return success_response(serializer.data, 'Penalty retrieved successfully')
    except Penalty.DoesNotExist:
        return not_found_response('Penalty not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletePenalty(request, pk):
    """
    Delete penalty by ID
    """
    try:
        penalty = Penalty.objects.get(pk=pk)
        penalty.delete()
        return success_response(message='Penalty deleted successfully')
    except Penalty.DoesNotExist:
        return not_found_response('Penalty not found')
    except Exception as e:
        return server_error_response(e)
    

#============================= DisbursementInfo Apis ===============================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createDisbursementInfo(request):
    try:
        data = request.data.copy()
        data['createBy'] = request.user.username
        data['updateBy'] = request.user.username

        serializer = DisbursementInfoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Disbursement info created successfully')

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def updateDisbursementInfo(request, pk):
    try:
        # Step 1: Fetch the record by primary key
        instance = DisbursementInfo.objects.filter(pk=pk).first()
        if not instance:
            return not_found_response(instance if instance else type('DisbursementInfo', (), {'id': pk})())

        # Step 2: Prepare and clean input data
        data = request.data.copy()
        data['UpdateBy'] = request.user.username  # For audit trail

        # Step 3: Serialize and update
        serializer = DisbursementInfoSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, 'Disbursement info updated successfully')

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllDisbursementInfo(request):
    try:
        queryset = DisbursementInfo.objects.all().order_by('-CreatedAt')
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(queryset, request)

        serializer = DisbursementInfoSerializer(queryset, many=True)
        return success_response(serializer.data, 'Disbursement records retrieved successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDisbursementInfoById(request, pk):
    try:
        disbursement = DisbursementInfo.objects.get(pk=pk)
        serializer = DisbursementInfoSerializer(disbursement)
        return success_response(serializer.data, 'DisbursementInfo retrieved successfully')
    except DisbursementInfo.DoesNotExist:
        return not_found_response('DisbursementInfo not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteDisbursementInfo(request, pk):
    try:
        disbursement = DisbursementInfo.objects.get(pk=pk)
        disbursement.delete()
        return success_response(message='DisbursementInfo deleted successfully')
    except DisbursementInfo.DoesNotExist:
        return not_found_response('DisbursementInfo not found')
    except Exception as e:
        return server_error_response(e)