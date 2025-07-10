# UserManagement/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import UserManagement
from .serializers import UserManagementSerializer
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createUser(request):
    try:
        serializer = UserManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'result': True,
                'message': 'User created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        # Extract first error message and flatten it
        first_field, messages = next(iter(serializer.errors.items()))
        message_str = messages[0] if isinstance(messages, list) else messages

        return Response({
            'result': False,
            'message': 'Validation failed.',
            'errors': message_str
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'result': False,
            'message': 'Internal server error.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#------------------------------------------------------------------------------------    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    try:
        # Step 1: Check if User exists
        user = UserManagement.objects.get(pk=pk)

        # Step 2: Validate unexpected fields
        allowed_fields = set(UserManagementSerializer().get_fields().keys())
        invalid_fields = set(request.data.keys()) - allowed_fields
        if invalid_fields:
            return Response({
                'result': False,
                'message': 'Validation failed.',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Validate serializer and save if valid
        serializer = UserManagementSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'result': True,
                'message': 'User updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        # Step 4: Handle field-level validation errors (flattened)
        first_field, messages = next(iter(serializer.errors.items()))
        message_str = messages[0] if isinstance(messages, list) else messages

        return Response({
            'result': False,
            'message': 'Validation failed.',
            'errors': message_str
        }, status=status.HTTP_400_BAD_REQUEST)

    except UserManagement.DoesNotExist:
        return Response({
            'result': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # Step 5: Handle any unexpected internal server error
        return Response({
            'result': False,
            'message': 'Internal server error.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#------------------------------------------------------------------------------------
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request, pk):
    try:
        # Step 1: Check if User exists
        user = UserManagement.objects.get(pk=pk)

        # Step 2: Delete the user
        user.delete()

        return Response({
            'result': True,
            'message': 'User deleted successfully.'
        }, status=status.HTTP_200_OK)

    except UserManagement.DoesNotExist:
        return Response({
            'result': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # Step 3: Handle any unexpected errors
        return Response({
            'result': False,
            'message': 'Internal server error.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserById(request, pk):
    try:
        user = UserManagement.objects.get(pk=pk)
        serializer = UserManagementSerializer(user)
        return Response({
            'result': True,
            'message': 'User fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    except UserManagement.DoesNotExist:
        return Response({
            'result': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'result': False,
            'message': 'Internal server error.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllUser(request):
    try:
        users = UserManagement.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(users, request)

        serializer = UserManagementSerializer(users, many=True)
        return Response({
            'result': True,
            'message': 'Users fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'result': False,
            'message': 'Internal server error.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#------------------------------------------------------------------------------------