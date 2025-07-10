from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import CompanyProfile
from .serializers import CompanyProfileSerializer

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


# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_company_profile(request):
    try:
        serializer = CompanyProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Company profile created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_company_profile(request, pk):
    try:
        # Step 1: Extract IDs for validation
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                'success': False,
                'message': 'OwnerId, BranchId and DepartmentId are required for validation.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Verify company profile exists with these IDs
        company_profile = CompanyProfile.objects.filter(
            pk=pk,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not company_profile:
            return not_found_response('Company profile not found for the given IDs')

        # Step 3: Prepare update data
        data = request.data.copy()
        if hasattr(data, "_mutable"):
            data._mutable = True
        data.pop("OwnerId", None)
        data.pop("BranchId", None)
        data.pop("DepartmentId", None)
                
        # Step 4: Handle file fields - only update if new files are provided
        file_fields = ['Logo', 'UserProfileImage']
        for field in file_fields:
            if field not in request.FILES:
                data.pop(field, None)  # Remove field if no new file is provided

        # Step 5: Validate fields
        allowed_fields = set(CompanyProfileSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 6: Perform update
        serializer = CompanyProfileSerializer(company_profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Company profile updated successfully")
        
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCompanyProfileById(request, pk):
    try:
        companyProfiles = CompanyProfile.objects.get(pk=pk)
        serializer = CompanyProfileSerializer(companyProfiles)
        return success_response(serializer.data, 'Department fetched successfully')
    except CompanyProfile.DoesNotExist:
        return not_found_response(f'No branch found with ID {pk}')
    except Exception as e:
        return server_error_response(e)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCompanyProfile(request):
    try:
        profiles = CompanyProfile.objects.all()
        serializer = CompanyProfileSerializer(profiles, many=True)  # Note many=True for querysets
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(str(e))  # Convert exception to string