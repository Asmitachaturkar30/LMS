from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import CustomSetting
from .serializers import CustomSettingSerializer
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createCustomSetting(request):
    try:
        serializer = CustomSettingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Custom setting created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateCustomSetting(request, pk):
    try:
        # Step 1: Extract and validate IDs
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                "result": False,
                "message": "OwnerId, BranchId and DepartmentId are required for validation"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Fetch instance with matching IDs
        instance = CustomSetting.objects.filter(
            pk=pk,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not instance:
            return not_found_response("Custom Setting not found for the given IDs")

        # Step 3: Prepare update data
        data = request.data.copy()
        if hasattr(data, "_mutable"):
            data._mutable = True
        data.pop("OwnerId", None)
        data.pop("BranchId", None)
        data.pop("DepartmentId", None)

        # Step 4: Validate and update
        serializer = CustomSettingSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Custom Setting updated successfully")
        
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteCustomSetting(request, pk):
    try:
        instance = CustomSetting.objects.get(pk=pk)
        instance.delete()
        return success_response(message="Custom Setting deleted successfully")
    except CustomSetting.DoesNotExist:
        return not_found_response("Custom Setting not found")
    except Exception as e:
        return server_error_response(e)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllCustomSettings(request):
    try:
        settings = CustomSetting.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(settings, request)
        serializer = CustomSettingSerializer(settings, many=True)
        return success_response(serializer.data, "Custom settings fetched successfully")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCustomSettingById(request, pk):
    try:
        setting = CustomSetting.objects.get(pk=pk)
        serializer = CustomSettingSerializer(setting)
        return success_response(serializer.data, "Custom setting fetched successfully")
    except CustomSetting.DoesNotExist:
        return not_found_response("Custom Setting not found")
    except Exception as e:
        return server_error_response(e)