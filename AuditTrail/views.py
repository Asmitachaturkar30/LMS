from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import AuditLogs
from .serializers import AuditLogsSerializer
from Masters.models import Branch, Department
from LoginAuth.models import User
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
def createAuditLog(request):
    try:
        serializer = AuditLogsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Audit log created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateAuditLog(request, pk):
    try:
        # Step 1: Extract and validate IDs
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId, BranchId and DepartmentId are required for validation.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Fetch AuditLog with matching IDs
        audit = AuditLogs.objects.filter(
            pk=pk,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not audit:
            return not_found_response('Audit log not found for the given IDs')

        # Step 3: Prepare update data
        data = request.data.copy()
        if hasattr(data, "_mutable"):
            data._mutable = True
        data.pop("OwnerId", None)
        data.pop("BranchId", None)
        data.pop("DepartmentId", None)

        # Step 4: Validate fields
        allowed_fields = set(AuditLogsSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 5: Perform update
        serializer = AuditLogsSerializer(audit, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Audit log updated successfully")
        
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteAuditLog(request, pk):
    try:
        audit = AuditLogs.objects.get(pk=pk)
        audit.delete()
        return success_response(message="Audit log deleted successfully")
    except AuditLogs.DoesNotExist:
        return not_found_response("Audit log not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAuditLog(request, pk):
    try:
        audit = AuditLogs.objects.get(pk=pk)
        serializer = AuditLogsSerializer(audit)
        return success_response(serializer.data, "Audit log fetched successfully")
    except AuditLogs.DoesNotExist:
        return not_found_response("Audit log not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllAuditLogs(request):
    try:
        audits = AuditLogs.objects.all().order_by('-CreatedAt')
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(audits, request)
        serializer = AuditLogsSerializer(audits, many=True)
        return success_response(serializer.data, "Audit logs fetched successfully")
    except Exception as e:
        return server_error_response(e)