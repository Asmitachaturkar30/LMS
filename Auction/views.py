from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
# Response helper functions
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def createAuction(request):
    try:
        serializer = AuctionSetupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Auction setup created successfully")
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def updateAuction(request, AuctionId):
    try:
        # Step 1: Extract IDs for validation
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")
        Loan_id = request.data.get("LoanId")

        if not Owner_id or not branch_id or not department_id or not Loan_id:
            return JsonResponse({
                'success': False,
                'message': 'OwnerId, BranchId and DepartmentId,LoanId  are required for validation.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Verify auction exists
        auction = AuctionSetup.objects.filter(
            pk=AuctionId,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id,
            LoanId=Loan_id
        ).first()

        if not auction:
            return not_found_response('AuctionSetup not found for the given IDs')

        # Step 3: Prepare update data
        data = request.data.copy()
        if hasattr(data, "_mutable"):
            data._mutable = True
        data.pop("OwnerId", None)
        data.pop("BranchId", None)
        data.pop("DepartmentId", None)
        data.pop("LoanId",None)

        # Step 4: Handle file fields - only update if new files are provided
        file_fields = [
            'SeizureOrderCopy', 'ValuationReport', 'AssetPhotos', 'InsurancePolicy',
            'BidderPanCard', 'BidderAadhaar', 'EMD_Receipt', 'BidDeclarationForm',
            'SaleDeed', 'BuyerKycPackage', 'PaymentProof', 'HandoverReport',
            'RBI_AuctionReport', 'AuditTrailLog', 'TDS_Certificate'
        ]
        
        for field in file_fields:
            if field not in request.FILES:
                data.pop(field, None)  # Remove field if no new file is provided

        # Step 5: Validate fields
        allowed_fields = set(AuctionSetupSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId','LoanId'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 6: Perform update
        serializer = AuctionSetupSerializer(auction, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Auction setup updated successfully")
        
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllAuctions(request):
    try:
        auctions = AuctionSetup.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(auctions, request)
        serializer = AuctionSetupSerializer(auctions, many=True)
        return success_response(serializer.data, "Auction setups fetched successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAuctionById(request, AuctionId):
    try:
        auction = AuctionSetup.objects.get(pk=AuctionId)
        serializer = AuctionSetupSerializer(auction)
        return success_response(serializer.data, f"Auction setup {AuctionId} fetched successfully")
    except AuctionSetup.DoesNotExist:
        return not_found_response(f"AuctionSetup {AuctionId} not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteAuction(request, AuctionId):
    try:
        auction = AuctionSetup.objects.get(pk=AuctionId)
        auction.delete()
        return success_response(message=f"Auction setup {AuctionId} deleted successfully")
    except AuctionSetup.DoesNotExist:
        return not_found_response(f"AuctionSetup {AuctionId} not found")
    except Exception as e:
        return server_error_response(e)