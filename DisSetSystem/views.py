from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework import status
from .models import *
from .serializers import *
from InquiryLoanProcess.models import LoanApplication
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

def not_found_response(message, details=None):
    full_message = message
    if details:
        full_message = f"{message}: {details}"
    return JsonResponse({
        "result": False,
        "message": full_message
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


#============================= Disbursment Apis ===============================
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def createDisbursment(request):
#     try:
#         serializer = DisbursementSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return created_response(serializer.data, "Disbursement created successfully")
#         return validation_error_response(serializer.errors)
#     except Exception as e:
#         return server_error_response(e)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createDisbursment(request):
    try:
        serializer = DisbursementSerializer(data=request.data)
        if serializer.is_valid():
            disbursed = serializer.save()

            # Update related LoanApplication with Disbursement info
            loan = disbursed.Loan
            loan.DisbursementType = 'Full'
            loan.DisbursementMode = disbursed.ModeOfTransfer.upper()  # To map to NEFT/CHEQUE/UPI
            loan.DisbursementDate = disbursed.DisbursementDate
            loan.DisbursementStatus = 'Completed'
            loan.DisbursementNotes = disbursed.Remarks
            loan.save()

            return created_response(serializer.data, "Disbursement created successfully")
        
        # 👇 Add this to view the errors if serializer is not valid
        print("Validation Errors:", serializer.errors)
        return validation_error_response(serializer.errors)
        
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateDisbursment(request, disbursement_id):
    try:
        # Step 1: Extract IDs for validation
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId, BranchId and DepartmentId are required for validation'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Verify disbursement exists with matching IDs
        disbursement = Disbursement.objects.filter(
            pk=disbursement_id,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not disbursement:
            return not_found_response("Disbursement not found for the given IDs")

        # Step 3: Validate fields
        allowed_fields = set(DisbursementSerializer().get_fields().keys())
        invalid_fields = set(request.data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Perform update
        serializer = DisbursementSerializer(disbursement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Disbursement updated successfully")
        
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteDisbursment(request, disbursement_id):
    try:
        disbursement = Disbursement.objects.get(pk=disbursement_id)
        disbursement.delete()
        return success_response(message="Disbursement deleted successfully")
    except Disbursement.DoesNotExist:
        return not_found_response(f"Disbursement with ID {disbursement_id} not found")
    except Exception as e:
        return server_error_response(e)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllDisbursment(request):
    try:
        disbursements = Disbursement.objects.all()
        
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(disbursements, request)

        serializer = DisbursementSerializer(disbursements, many=True)
        return success_response(serializer.data, "Disbursement list retrieved successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getDisbursmentById(request, disbursement_id):
    try:
        disbursement = Disbursement.objects.get(pk=disbursement_id)
        serializer = DisbursementSerializer(disbursement)
        return success_response(serializer.data, "Disbursement retrieved successfully")
    except Disbursement.DoesNotExist:
        return not_found_response(f"Disbursement with ID {disbursement_id} not found")
    except Exception as e:
        return server_error_response(e)


#============================= RepaymentSchedule Apis ================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createRepaymentSchedule(request):
    try:
        serializer = RepaymentScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Repayment schedule created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)
    


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateRepaymentSchedule(request, pk):
    try:
        # Step 1: Extract IDs for validation
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId, BranchId and DepartmentId are required for validation'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Verify schedule exists with matching IDs
        schedule = RepaymentSchedule.objects.filter(
            pk=pk,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not schedule:
            return not_found_response("Repayment schedule not found for the given IDs")

        # Step 3: Validate fields
        allowed_fields = set(RepaymentScheduleSerializer().get_fields().keys())
        invalid_fields = set(request.data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Perform update
        serializer = RepaymentScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Repayment schedule updated successfully")
        
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteRepaymentSchedule(request, pk):
    try:
        schedule = RepaymentSchedule.objects.get(pk=pk)
        schedule.delete()
        return success_response(message="Repayment schedule deleted successfully")
    except RepaymentSchedule.DoesNotExist:
        return not_found_response(f"Repayment schedule with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllRepaymentSchedules(request):
    try:
        schedules = RepaymentSchedule.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(schedules, request)

        serializer = RepaymentScheduleSerializer(schedules, many=True)
        return success_response(serializer.data, "Repayment schedules retrieved successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getRepaymentScheduleById(request, pk):
    try:
        schedule = RepaymentSchedule.objects.get(pk=pk)
        serializer = RepaymentScheduleSerializer(schedule)
        return success_response(serializer.data, "Repayment schedule retrieved successfully")
    except RepaymentSchedule.DoesNotExist:
        return JsonResponse({
            "result": False,
            "message": f"Repayment schedule with ID {pk} not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return server_error_response(e)

#============================= PaymentCollection Apis ================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createPaymentCollection(request):
    try:
        data = request.data.copy()
        data["CreateBy"] = request.user.email
        data["UpdateBy"] = request.user.email

        serializer = PaymentCollectionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Payment collection created successfully")
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllPaymentCollections(request):
    try:
        collections = PaymentCollection.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(collections, request)

        serializer = PaymentCollectionSerializer(collections, many=True)
        return success_response(serializer.data, "Payment collections fetched successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getPaymentCollectionById(request, pk):
    try:
        collection = PaymentCollection.objects.get(pk=pk)
        serializer = PaymentCollectionSerializer(collection)
        return success_response(serializer.data, "Payment collection fetched successfully")
    except PaymentCollection.DoesNotExist:
        return not_found_response(f"Payment collection with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updatePaymentCollection(request, pk):
    try:
        # Step 1: Extract IDs for validation
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId, BranchId and DepartmentId are required for validation'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Verify collection exists with matching IDs
        collection = PaymentCollection.objects.filter(
            pk=pk,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not collection:
            return not_found_response("Payment collection not found for the given IDs")

        # Step 3: Validate fields
        allowed_fields = set(PaymentCollectionSerializer().get_fields().keys())
        invalid_fields = set(request.data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Perform update
        serializer = PaymentCollectionSerializer(collection, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Payment collection updated successfully")
        
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deletePaymentCollection(request, pk):
    try:
        collection = PaymentCollection.objects.get(pk=pk)
        collection.delete()
        return success_response(message="Payment collection deleted successfully")
    except PaymentCollection.DoesNotExist:
        return not_found_response(f"Payment collection with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)

#============================= LoanClosure Apis ================================

# API Views
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createLoanClosure(request):
    try:
        serializer = LoanClosureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Loan closure created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllLoanClosures(request):
    try:
        closures = LoanClosure.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(closures, request)

        serializer = LoanClosureSerializer(closures, many=True)
        return success_response(serializer.data, "Loan closures fetched successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getLoanClosureById(request, pk):
    try:
        closure = LoanClosure.objects.get(pk=pk)
        serializer = LoanClosureSerializer(closure)
        return success_response(serializer.data, "Loan closure fetched successfully")
    except LoanClosure.DoesNotExist:
        return not_found_response(f"Loan closure with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)

    

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateLoanClosure(request, pk):
    try:
        # Step 1: Find LoanClosure record by primary key
        closure = LoanClosure.objects.filter(pk=pk).first()
        if not closure:
            return not_found_response(closure if closure else type('LoanClosure', (), {'id': pk})())

        # Step 2: Update 'UpdateBy' field if needed
        data = request.data.copy()
        data['UpdateBy'] = request.user.email  # Optional audit field

        # Step 3: Validate and update
        serializer = LoanClosureSerializer(closure, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Loan closure updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteLoanClosure(request, pk):
    try:
        closure = LoanClosure.objects.get(pk=pk)
        closure.delete()
        return success_response(message="Loan closure deleted successfully")
    except LoanClosure.DoesNotExist:
        return not_found_response(f"Loan closure with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)



#============================= LoanForeclosure Apis ================================

# API Views
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createLoanForeclosure(request):
    try:
        serializer = LoanForeclosureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Loan foreclosure created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllLoanForeclosures(request):
    try:
        records = LoanForeclosure.objects.all().order_by('-CreatedAt')
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(records, request)

        serializer = LoanForeclosureSerializer(records, many=True)
        return success_response(serializer.data, "Loan foreclosure records retrieved successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getLoanForeclosureById(request, pk):
    try:
        record = LoanForeclosure.objects.get(pk=pk)
        serializer = LoanForeclosureSerializer(record)
        return success_response(serializer.data, "Loan foreclosure record retrieved successfully")
    except LoanForeclosure.DoesNotExist:
        return not_found_response(f"Foreclosure record with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateLoanForeclosure(request, pk):
    try:
        # Step 1: Get the LoanForeclosure record
        record = LoanForeclosure.objects.filter(pk=pk).first()
        if not record:
            return not_found_response(record if record else type('LoanForeclosure', (), {'id': pk})())

        # Step 2: UpdateBy tracking (optional)
        data = request.data.copy()
        data['UpdateBy'] = request.user.email

        # Step 3: Validate and update
        serializer = LoanForeclosureSerializer(record, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Foreclosure record updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteLoanForeclosure(request, pk):
    try:
        record = LoanForeclosure.objects.get(pk=pk)
        record.delete()
        return success_response(message="Foreclosure record deleted successfully")
    except LoanForeclosure.DoesNotExist:
        return not_found_response(f"Foreclosure record with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)

    
    
#============================= LoanRenewal Apis ================================

# API Views
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createLoanRenewal(request):
    try:
        serializer = LoanRenewalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Loan renewal created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getLoanRenewalById(request, pk):
    try:
        renewal = LoanRenewal.objects.get(pk=pk)
        serializer = LoanRenewalSerializer(renewal)
        return success_response(serializer.data, "Loan renewal fetched successfully")
    except LoanRenewal.DoesNotExist:
        return not_found_response(f"Loan renewal with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllLoanRenewals(request):
    try:
        renewals = LoanRenewal.objects.all().order_by("-CreatedAt")
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(renewals, request)

        serializer = LoanRenewalSerializer(renewals, many=True)
        return success_response(serializer.data, "Loan renewals fetched successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateLoanRenewal(request, pk):
    try:
        # Step 1: Retrieve the renewal record
        renewal = LoanRenewal.objects.filter(pk=pk).first()
        if not renewal:
            return not_found_response(renewal if renewal else type('LoanRenewal', (), {'id': pk})())

        # Step 2: Add audit field (optional)
        data = request.data.copy()
        data['UpdateBy'] = request.user.email

        # Step 3: Validate and perform update
        serializer = LoanRenewalSerializer(renewal, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Loan renewal updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteLoanRenewal(request, pk):
    try:
        renewal = LoanRenewal.objects.get(pk=pk)
        renewal.delete()
        return success_response(message="Loan renewal deleted successfully")
    except LoanRenewal.DoesNotExist:
        return not_found_response(f"Loan renewal with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)

#============================= AutoSquareOff Apis ================================

# API Views
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createAutoSquareOff(request):
    try:
        serializer = AutoSquareOffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Auto square-off created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAutoSquareOffById(request, pk):
    try:
        square_off = AutoSquareOffReconciliation.objects.get(pk=pk)
        serializer = AutoSquareOffSerializer(square_off)
        return success_response(serializer.data, "Auto square-off fetched successfully")
    except AutoSquareOffReconciliation.DoesNotExist:
        return not_found_response(f"Auto square-off with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllAutoSquareOffs(request):
    try:
        square_offs = AutoSquareOffReconciliation.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(square_offs, request)

        serializer = AutoSquareOffSerializer(square_offs, many=True)
        return success_response(serializer.data, "Auto square-offs fetched successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateAutoSquareOff(request, pk):
    try:
        # Step 1: Fetch the record by primary key
        square_off = AutoSquareOffReconciliation.objects.filter(pk=pk).first()
        if not square_off:
            return not_found_response(square_off if square_off else type('AutoSquareOffReconciliation', (), {'id': pk})())

        # Step 2: Copy request data and set UpdateBy
        data = request.data.copy()
        data["UpdateBy"] = request.user.email

        # Step 3: Validate and update using serializer
        serializer = AutoSquareOffSerializer(square_off, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Auto square-off updated successfully")

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteAutoSquareOff(request, pk):
    try:
        square_off = AutoSquareOffReconciliation.objects.get(pk=pk)
        square_off.delete()
        return success_response(message="Auto square-off deleted successfully")
    except AutoSquareOffReconciliation.DoesNotExist:
        return not_found_response(f"Auto square-off with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)

#============================= emi_collection Apis ================================

# API Views
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_emi_collection(request):
    try:
        serializer = EMICollectionAdjustmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "EMI collection created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_emi_collection(request, pk):
    try:
        # Step 1: Extract IDs for validation
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId, BranchId and DepartmentId are required for validation'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Verify record exists with matching IDs
        emi_obj = EMICollectionAdjustment.objects.filter(
            pk=pk,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not emi_obj:
            return not_found_response("Data not found for the given IDs")

        # Step 3: Validate fields
        allowed_fields = set(EMICollectionAdjustmentSerializer().get_fields().keys())
        invalid_fields = set(request.data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Perform update
        serializer = EMICollectionAdjustmentSerializer(emi_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "EMI collection updated successfully")
        
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_emi_collection(request, pk):
    try:
        emi_obj = EMICollectionAdjustment.objects.get(pk=pk)
        emi_obj.delete()
        return no_content_response("EMI collection deleted successfully")
    except EMICollectionAdjustment.DoesNotExist:
        return not_found_response(f"EMI collection with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_emi_collection_by_id(request, pk):
    try:
        emi_obj = EMICollectionAdjustment.objects.get(pk=pk)
        serializer = EMICollectionAdjustmentSerializer(emi_obj)
        return success_response(serializer.data, "EMI collection fetched successfully")
    except EMICollectionAdjustment.DoesNotExist:
        return not_found_response(f"EMI collection with ID {pk} not found")
    except Exception as e:
        return server_error_response(e)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_emi_collections(request):
    try:
        all_objs = EMICollectionAdjustment.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(all_objs, request)

        serializer = EMICollectionAdjustmentSerializer(all_objs, many=True)
        return success_response(serializer.data, "All EMI collections fetched successfully")
    except Exception as e:
        return server_error_response(e)