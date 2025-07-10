from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from .models import *
from .utils import * 
from .serializers import *
from django.core.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from simpleeval import simple_eval

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


def multi_status_response(data, errors, message):
    return JsonResponse({
        "result": bool(data) and not bool(errors),
        "message": message,
        "data": data,
        "errors": errors
    }, status=status.HTTP_207_MULTI_STATUS)



#============================= Source Apis ===============================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createSource(request):
    try:
        data = request.data.copy()
        data['CreateBy'] = request.user.email
        data['UpdateBy'] = request.user.email

        serializer = SourceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Source created successfully')
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getSource(request, SourceId):
    try:
        source = Source.objects.get(pk=SourceId)
        serializer = SourceSerializer(source)
        return success_response(serializer.data, 'Source fetched successfully')
    except Source.DoesNotExist:
        return not_found_response(f'No source found with ID {SourceId}')
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateSource(request, SourceId):
    try:
        # Validate required fields
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId, BranchId and DepartmentId are required for validation.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get source with context
        source = Source.objects.filter(
            pk=SourceId,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not source:
            return not_found_response('Source not found for the given OwnerId, BranchId and DepartmentId')

        # Prepare update data
        data = request.data.copy()
        data.pop('OwnerId', None)
        data.pop('BranchId', None)
        data.pop('DepartmentId', None)

        # Validate unexpected fields
        allowed_fields = set(SourceSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed.',
                'errors': {'message': f"Unexpected field(s): {', '.join(invalid_fields)}"}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save
        serializer = SourceSerializer(source, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, 'Source updated successfully')
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteSource(request, SourceId):
    try:
        source = Source.objects.get(pk=SourceId)
        source.delete()
        return success_response(message='Source deleted successfully')
    except Source.DoesNotExist:
        return not_found_response(f'No source found with ID {SourceId}')
    except Exception as e:
        return server_error_response(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulkCreateSource(request):
    try:
        sources = request.data

        if not sources or not isinstance(sources, list):
            return validation_error_response({'sources': ['A list of source objects is required.']})

        serializer = SourceSerializer(data=sources, many=True)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Sources created successfully')

        # Format validation errors
        error_messages = []
        for index, item_errors in enumerate(serializer.errors):
            for field, messages in item_errors.items():
                msg = ", ".join(messages)
                error_messages.append(f"Item {index} → {field}: {msg}")

        return validation_error_response({'bulkErrors': error_messages})

    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def bulkUpdateSource(request):
    try:
        sources = request.data

        if not sources or not isinstance(sources, list):
            return validation_error_response({'sources': ['A list of source objects is required']})

        updated_data = []
        error_data = []

        for source_data in sources:
            Owner_id = source_data.get('OwnerId')
            source_id = source_data.get('SourceId')
            branch_id = source_data.get('BranchId')
            department_id = source_data.get('DepartmentId')

            if not Owner_id or not source_id or not branch_id or not department_id:
                error_data.append({
                    'SourceId': source_id,
                    'message': 'Missing OwnerId, SourceId, BranchId or DepartmentId'
                })
                continue

            try:
                source_instance = Source.objects.filter(
                    pk=source_id,
                    OwnerId=Owner_id,
                    BranchId=branch_id,
                    DepartmentId=department_id
                ).first()

                if not source_instance:
                    error_data.append({
                        'SourceId': source_id,
                        'message': 'Source not found for the given context'
                    })
                    continue

                update_data = source_data.copy()
                update_data.pop('OwnerId', None)
                update_data.pop('BranchId', None)
                update_data.pop('DepartmentId', None)

                allowed_fields = set(SourceSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
                invalid_fields = set(update_data.keys()) - allowed_fields - {'SourceId'}
                if invalid_fields:
                    error_data.append({
                        'SourceId': source_id,
                        'message': f"Unexpected field(s): {', '.join(invalid_fields)}"
                    })
                    continue

                serializer = SourceSerializer(source_instance, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_data.append(serializer.data)
                else:
                    error_data.append({
                        'SourceId': source_id,
                        'message': f"Validation failed for field(s): {', '.join(serializer.errors.keys())}"
                    })

            except Exception as e:
                error_data.append({
                    'SourceId': source_id,
                    'message': str(e)
                })

        if updated_data:
            response = {
                'result': True,
                'message': 'Bulk update completed',
                'data': updated_data
            }
            if error_data:
                response['errors'] = {'failedUpdates': error_data}
            return success_response(response)
        
        return JsonResponse({
            'result': False,
            'message': 'No sources were updated',
            'errors': {'failedUpdates': error_data}
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllSources(request):
    try:
        sources = Source.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(sources, request)

        if not sources.exists():
            return success_response([], 'No sources found')
        
        serializer = SourceSerializer(sources, many=True)
        return success_response(serializer.data, 'Sources fetched successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bulkDeleteSource(request):
    try:
        source_ids = request.data.get('SourceIds')

        if not source_ids or not isinstance(source_ids, list):
            return validation_error_response({'SourceIds': ['A list of source IDs is required']})

        deleted = []
        not_found = []

        for source_id in source_ids:
            try:
                source = Source.objects.get(pk=source_id)
                source.delete()
                deleted.append(source_id)
            except Source.DoesNotExist:
                not_found.append(source_id)

        response = {
            'message': f"Deleted {len(deleted)} source(s). {len(not_found)} not found",
            'data': {'deleted': deleted}
        }
        if not_found:
            response['errors'] = {'not_found': not_found}
        
        return success_response(response)

    except Exception as e:
        return server_error_response(e)

#============================= Rating Apis ===============================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createRating(request):
    try:
        data = request.data.copy()
        data['CreateBy'] = request.user.email
        data['UpdateBy'] = request.user.email

        serializer = RatingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Rating created successfully')
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRating(request, RateId):
    try:
        rating = Rating.objects.get(pk=RateId)
        serializer = RatingSerializer(rating)
        return success_response(serializer.data, 'Rating fetched successfully')
    except Rating.DoesNotExist:
        return not_found_response(f'No rating found with ID {RateId}')
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateRating(request, RateId):
    try:
        # Validate required fields
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId, BranchId and DepartmentId are required for validation.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get rating with context
        rating = Rating.objects.filter(
            pk=RateId,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not rating:
            return not_found_response('Rating not found for the given OwnerId, BranchId and DepartmentId')

        # Prepare update data
        data = request.data.copy()
        data.pop('OwnerId', None)
        data.pop('BranchId', None)
        data.pop('DepartmentId', None)

        # Validate unexpected fields
        allowed_fields = set(RatingSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed.',
                'errors': {'message': f"Unexpected field(s): {', '.join(invalid_fields)}"}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save
        serializer = RatingSerializer(rating, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, 'Rating updated successfully')
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteRating(request, RateId):
    try:
        rating = Rating.objects.get(pk=RateId)
        rating.delete()
        return success_response(message='Rating deleted successfully')
    except Rating.DoesNotExist:
        return not_found_response(f'No rating found with ID {RateId}')
    except Exception as e:
        return server_error_response(e)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulkCreateRating(request):
    try:
        ratings = request.data

        if not ratings or not isinstance(ratings, list):
            return validation_error_response({'ratings': ['A list of rating objects is required.']})

        serializer = RatingSerializer(data=ratings, many=True)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Ratings created successfully')

        # Format bulk validation errors
        error_messages = []
        for index, item_errors in enumerate(serializer.errors):
            for field, messages in item_errors.items():
                error_messages.append(f"Item {index} → {field}: {', '.join(messages)}")

        return validation_error_response({'bulkErrors': error_messages})

    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def bulkUpdateRating(request):
    try:
        ratings = request.data

        if not ratings or not isinstance(ratings, list):
            return validation_error_response({'ratings': ['A list of rating objects is required']})

        updated_data = []
        error_data = []

        for rating_data in ratings:
            Owner_id = rating_data.get("OwnerId")
            rate_id = rating_data.get("RateId")
            branch_id = rating_data.get("BranchId")
            department_id = rating_data.get("DepartmentId")

            if not Owner_id or not rate_id or not branch_id or not department_id:
                error_data.append({
                    'RateId': rate_id,
                    'message': 'OwnerId, RateId, BranchId and DepartmentId are required'
                })
                continue

            try:
                rating = Rating.objects.filter(
                    pk=rate_id,
                    OwnerId=Owner_id,
                    BranchId=branch_id,
                    DepartmentId=department_id
                ).first()

                if not rating:
                    error_data.append({
                        'RateId': rate_id,
                        'message': 'Rating not found for the given context'
                    })
                    continue

                update_data = rating_data.copy()
                update_data.pop('OwnerId', None)
                update_data.pop('BranchId', None)
                update_data.pop('DepartmentId', None)

                allowed_fields = set(RatingSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
                invalid_fields = set(update_data.keys()) - allowed_fields - {'RateId'}
                if invalid_fields:
                    error_data.append({
                        'RateId': rate_id,
                        'message': f"Unexpected field(s): {', '.join(invalid_fields)}"
                    })
                    continue

                serializer = RatingSerializer(rating, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_data.append(serializer.data)
                else:
                    error_data.append({
                        'RateId': rate_id,
                        'message': f"Validation failed for field(s): {', '.join(serializer.errors.keys())}"
                    })

            except Exception as e:
                error_data.append({
                    'RateId': rate_id,
                    'message': str(e)
                })

        if updated_data:
            response = {
                'result': True,
                'message': 'Bulk update completed',
                'data': updated_data
            }
            if error_data:
                response['errors'] = {'failedUpdates': error_data}
            return success_response(response)
        
        return JsonResponse({
            'result': False,
            'message': 'No ratings were updated',
            'errors': {'failedUpdates': error_data}
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllRatings(request):
    try:
        ratings = Rating.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(ratings, request)

        serializer = RatingSerializer(ratings, many=True)
        return success_response(serializer.data, 'Ratings fetched successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bulkDeleteRating(request):
    try:
        rate_ids = request.data.get('RateIds')

        if not rate_ids or not isinstance(rate_ids, list):
            return validation_error_response({'RateIds': ['A list of rate IDs is required']})

        deleted = []
        not_found = []

        for rate_id in rate_ids:
            try:
                rating = Rating.objects.get(pk=rate_id)
                rating.delete()
                deleted.append(rate_id)
            except Rating.DoesNotExist:
                not_found.append(rate_id)

        response = {
            'message': f"Deleted {len(deleted)} rating(s). {len(not_found)} not found",
            'data': {'deleted': deleted}
        }
        if not_found:
            response['errors'] = {'not_found': not_found}
        
        return success_response(response)

    except Exception as e:
        return server_error_response(e)



#============================= Branch Apis ===============================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createBranch(request):
    try:
        data = request.data.copy()
        data['CreateBy'] = request.user.email
        data['UpdateBy'] = request.user.email

        serializer = BranchSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Branch created successfully')

        # Optional: clean unique email error message
        if 'Email' in serializer.errors and 'unique' in str(serializer.errors['Email'][0]).lower():
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': 'Branch with this Email already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)

        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getBranch(request, BranchId):
    try:
        branch = Branch.objects.get(pk=BranchId)
        serializer = BranchSerializer(branch)
        return success_response(serializer.data, 'Branch fetched successfully')
    except Branch.DoesNotExist:
        return not_found_response(f'No branch found with ID {BranchId}')
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateBranch(request, BranchId):
    try:
        Owner_id = request.data.get("OwnerId")
        
        if not Owner_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId is required for validation.'
            }, status=status.HTTP_400_BAD_REQUEST)

        branch = Branch.objects.filter(pk=BranchId, OwnerId=Owner_id).first()

        if not branch:
            return not_found_response(f'Branch or OwnerId not found with BranchID:{BranchId} or OwnerId:{Owner_id}')

        data = request.data.copy()
        data.pop("OwnerId", None)

        allowed_fields = set(BranchSerializer().get_fields().keys()) - {'OwnerId'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = BranchSerializer(branch, data={**data, 'OwnerId': Owner_id}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, 'Branch updated successfully')
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteBranch(request, BranchId):
    try:
        branch = Branch.objects.get(pk=BranchId)
        branch.delete()
        return success_response(message='Branch deleted successfully')
    except Branch.DoesNotExist:
        return not_found_response(f'No branch found with ID {BranchId}')
    except Exception as e:
        return server_error_response(e)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulkCreateBranch(request):
    try:
        branches = request.data

        if not branches or not isinstance(branches, list):
            return validation_error_response({'branches': ['A list of branch objects is required.']})

        emails = [branch.get('Email') for branch in branches if branch.get('Email')]
        if Branch.objects.filter(Email__in=emails).exists():
            return validation_error_response({'Email': ['One or more branches with these emails already exist.']})

        serializer = BranchSerializer(data=branches, many=True)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Branches created successfully')

        error_messages = []
        for index, item_errors in enumerate(serializer.errors):
            for field, messages in item_errors.items():
                error_messages.append(f"Item {index} → {field}: {', '.join(messages)}")

        return validation_error_response({'bulkErrors': error_messages})

    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def bulkUpdateBranch(request):
    try:
        branches = request.data

        if not isinstance(branches, list):
            return validation_error_response({'branches': ['A list of branch objects is required']})

        updated_data = []
        error_data = []

        for branch_data in branches:
            Owner_id = branch_data.get("OwnerId")
            branch_id = branch_data.get("BranchId")

            if not branch_id or not Owner_id:
                error_data.append({
                    "branchId": branch_id,
                    "message": "BranchId, OwnerId are required"
                })
                continue

            try:
                branch = Branch.objects.filter(
                    pk=branch_id,
                    OwnerId=Owner_id
                ).first()

                if not branch:
                    error_data.append({
                        "branchId": branch_id,
                        "message": f"Branch not found with ID {branch_id}"
                    })
                    continue

                update_data = branch_data.copy()
                update_data.pop("OwnerId", None)

                allowed_fields = set(BranchSerializer().get_fields().keys()) - {'OwnerId'}
                invalid_fields = set(update_data.keys()) - allowed_fields - {"BranchId"}
                if invalid_fields:
                    error_data.append({
                        "branchId": branch_id,
                        "message": f"Unexpected field(s): {', '.join(invalid_fields)}"
                    })
                    continue

                serializer = BranchSerializer(branch, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_data.append({
                        "branchId": branch_id,
                        "data": serializer.data
                    })
                else:
                    error_data.append({
                        "branchId": branch_id,
                        "message": "Validation error",
                        "errors": serializer.errors
                    })

            except Exception as e:
                error_data.append({
                    "branchId": branch_id,
                    "message": str(e)
                })

        if updated_data:
            response = {
                "message": "Bulk update completed",
                "data": updated_data
            }
            if error_data:
                response['errors'] = {"failedUpdates": error_data}
                return JsonResponse({
                    "result": True,
                    **response
                }, status=status.HTTP_207_MULTI_STATUS)
            return success_response(response)
        
        return JsonResponse({
            "result": False,
            "message": "No branches were updated",
            "errors": {"failedUpdates": error_data}
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllBranch(request):
    try:
        branches = Branch.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(branches, request)

        serializer = BranchSerializer(branches, many=True)
        return success_response(serializer.data, 'Branches fetched successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bulkDeleteBranch(request):
    try:
        branch_ids = request.data.get('BranchIds')

        if not branch_ids or not isinstance(branch_ids, list):
            return validation_error_response({'BranchIds': ['A list of branch IDs is required']})

        deleted_ids = []
        not_found_ids = []

        for branch_id in branch_ids:
            try:
                branch = Branch.objects.get(pk=branch_id)
                branch.delete()
                deleted_ids.append(branch_id)
            except Branch.DoesNotExist:
                not_found_ids.append(branch_id)

        response = {
            "message": f"Deleted {len(deleted_ids)} branches. {len(not_found_ids)} IDs not found",
            "data": {"deleted": deleted_ids}
        }
        if not_found_ids:
            response["errors"] = {"not_found": not_found_ids}
        
        return success_response(response)

    except Exception as e:
        return server_error_response(e)



#============================= Department Apis ===============================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createDepartment(request):
    try:
        data = request.data.copy()
        data['CreateBy'] = request.user.email
        data['UpdateBy'] = request.user.email

        serializer = DepartmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Department created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDepartmentById(request, DepartmentId):
    try:
        department = Department.objects.get(pk=DepartmentId)
        serializer = DepartmentListSerializer(department)
        return success_response(serializer.data, 'Department fetched successfully')
    except Department.DoesNotExist:
        return not_found_response(f'No branch found with ID {DepartmentId}')
    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateDepartment(request, DepartmentId):
    try:
        # Validate required fields
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        if not Owner_id or not branch_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId and BranchId are required for verification'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get department with context
        department = Department.objects.filter(
            pk=DepartmentId,
            OwnerId=Owner_id,
            BranchId=branch_id
        ).first()

        if not department:
            return not_found_response(f"Department not found with ID {DepartmentId} and BranchId {branch_id}")

        # Prepare update data
        data = request.data.copy()
        data.pop("OwnerId", None)
        data.pop("BranchId", None)

        # Validate unexpected fields
        allowed_fields = set(DepartmentUpdateSerializer().get_fields().keys()) - {'OwnerId', 'BranchId'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate and update
        serializer = DepartmentUpdateSerializer(department, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, 'Department updated successfully')
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteDepartment(request, DepartmentId):
    try:
        department = Department.objects.get(pk=DepartmentId)
        department.delete()
        return success_response(message='Department deleted successfully')
    except Department.DoesNotExist:
        return not_found_response(f'No department found with ID {DepartmentId}')
    except Exception as e:
        return server_error_response(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulkCreateDepartment(request):
    try:
        departments = request.data

        if not departments or not isinstance(departments, list):
            return validation_error_response({'departments': ['A list of department objects is required.']})

        serializer = DepartmentCreateSerializer(data=departments, many=True)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Departments created successfully')

        # Format validation errors like: Item 1 → field: message
        error_messages = []
        for index, item_errors in enumerate(serializer.errors):
            for field, messages in item_errors.items():
                error_messages.append(f"Item {index} → {field}: {', '.join(messages)}")

        return validation_error_response({'bulkErrors': error_messages})

    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def bulkUpdateDepartment(request):
    try:
        departments = request.data

        if not isinstance(departments, list):
            return validation_error_response({'departments': ['A list of department objects is required']})

        updated_data = []
        error_data = []

        for dept_data in departments:
            department_id = dept_data.get("DepartmentId")
            Owner_id = dept_data.get("OwnerId")
            branch_id = dept_data.get("BranchId")

            if not department_id or not Owner_id or not branch_id:
                error_data.append({
                    'DepartmentId': department_id,
                    'message': 'DepartmentId, OwnerId and BranchId are required'
                })
                continue

            try:
                department = Department.objects.filter(
                    pk=department_id,
                    OwnerId=Owner_id,
                    BranchId=branch_id
                ).first()

                if not department:
                    error_data.append({
                        'DepartmentId': department_id,
                        'message': f'Department not found with ID {department_id} and BranchId {branch_id}'
                    })
                    continue

                update_data = dept_data.copy()
                update_data.pop("OwnerId", None)
                update_data.pop("BranchId", None)

                allowed_fields = set(DepartmentUpdateSerializer().get_fields().keys()) - {'OwnerId', 'BranchId'}
                invalid_fields = set(update_data.keys()) - allowed_fields - {'DepartmentId'}
                if invalid_fields:
                    error_data.append({
                        'DepartmentId': department_id,
                        'message': f"Unexpected field(s): {', '.join(invalid_fields)}"
                    })
                    continue

                serializer = DepartmentUpdateSerializer(department, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_data.append({
                        'DepartmentId': department_id,
                        'data': serializer.data
                    })
                else:
                    error_data.append({
                        'DepartmentId': department_id,
                        'message': 'Validation failed',
                        'errors': serializer.errors
                    })

            except Exception as e:
                error_data.append({
                    'DepartmentId': department_id,
                    'message': str(e)
                })

        if updated_data:
            if error_data:
                return multi_status_response(
                    data=updated_data,
                    errors={'failedUpdates': error_data},
                    message='Some departments updated, others failed'
                )
            return success_response(updated_data, 'Departments updated successfully')
        
        return JsonResponse({
            'result': False,
            'message': 'No departments were updated',
            'errors': {'failedUpdates': error_data}
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllDepartments(request):
    try:
        departments = Department.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(departments, request)

        if not departments.exists():
            return success_response([], 'No departments found')
        
        serializer = DepartmentListSerializer(departments, many=True)
        return success_response(serializer.data, 'Departments fetched successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bulkDeleteDepartment(request):
    try:
        department_ids = request.data.get('DepartmentIds')

        if not department_ids or not isinstance(department_ids, list):
            return validation_error_response({'DepartmentIds': ['A list of department IDs is required']})

        deleted_ids = []
        not_found_ids = []

        for dept_id in department_ids:
            try:
                department = Department.objects.get(pk=dept_id)
                department.delete()
                deleted_ids.append(dept_id)
            except Department.DoesNotExist:
                not_found_ids.append(dept_id)

        response = {
            'message': f"{len(deleted_ids)} department(s) deleted successfully",
            'data': {
                'deleted': deleted_ids,
                'not_found': not_found_ids
            }
        }
        return success_response(response)

    except Exception as e:
        return server_error_response(e)


#------------------------- Designation Master apis -----------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createDesignation(request):
    try:
        data = request.data.copy()
        data['CreateBy'] = request.user.email
        data['UpdateBy'] = request.user.email

        # Duplicate check (case-insensitive by name and branch, modify as needed)
        Name = data.get('Name')

        if Designation.objects.filter(
            Name__iexact=Name,
        ).exists():
            return validation_error_response({
                "Name": ["This designation already exists in the selected branch."]
            })

        serializer = DesignationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Designation created successfully')
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateDesignation(request, DesignationId):
    try:
        designation = Designation.objects.filter(pk=DesignationId).first()
        if not designation:
            return JsonResponse({
                "result": False,
                "message": f"Designation with ID {DesignationId} not found"
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['UpdateBy'] = request.user.email  # optional: auto update field

        serializer = DesignationSerializer(designation, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Designation updated successfully")
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteDesignation(request, DesignationId):
    try:
        designation = Designation.objects.get(pk=DesignationId)
        designation.delete()
        return success_response(message='Designation deleted successfully')
    except Designation.DoesNotExist:
        return not_found_response(f'No designation found with ID {DesignationId}')
    except Exception as e:
        return server_error_response(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulkCreateDesignation(request):
    try:
        designations = request.data

        if not isinstance(designations, list):
            return validation_error_response({'designations': ['A list of designation objects is required.']})

        names = [d.get('Name') for d in designations if d.get('Name')]
        if Designation.objects.filter(Name__in=names).exists():
            return validation_error_response({'Name': ['One or more designations with these names already exist.']})

        serializer = DesignationSerializer(data=designations, many=True)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Designations created successfully')

        error_messages = []
        for index, item_errors in enumerate(serializer.errors):
            for field, messages in item_errors.items():
                error_messages.append(f"Item {index} → {field}: {', '.join(messages)}")

        return validation_error_response({'bulkErrors': error_messages})

    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def bulkUpdateDesignation(request):
    try:
        designations = request.data

        if not isinstance(designations, list):
            return validation_error_response({'designations': ['A list of designation objects is required']})

        updated_data = []
        error_data = []

        for desig_data in designations:
            designation_id = desig_data.get("DesignationId")
            Owner_id = desig_data.get("OwnerId")
            branch_id = desig_data.get("BranchId")
            department_id = desig_data.get("DepartmentId")

            if not designation_id or not Owner_id or not branch_id or not department_id:
                error_data.append({
                    "DesignationId": designation_id,
                    "message": "DesignationId, OwnerId, BranchId and DepartmentId are required"
                })
                continue

            try:
                designation = Designation.objects.filter(
                    pk=designation_id,
                    OwnerId=Owner_id,
                    BranchId=branch_id,
                    DepartmentId=department_id
                ).first()

                if not designation:
                    error_data.append({
                        "DesignationId": designation_id,
                        "message": f"Designation not found with ID {designation_id} for given context"
                    })
                    continue

                update_data = desig_data.copy()
                update_data.pop("OwnerId", None)
                update_data.pop("BranchId", None)
                update_data.pop("DepartmentId", None)

                allowed_fields = set(DesignationSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
                invalid_fields = set(update_data.keys()) - allowed_fields - {"DesignationId"}
                if invalid_fields:
                    error_data.append({
                        "DesignationId": designation_id,
                        "message": f"Unexpected field(s): {', '.join(invalid_fields)}"
                    })
                    continue

                serializer = DesignationSerializer(designation, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_data.append({
                        "DesignationId": designation_id,
                        "data": serializer.data
                    })
                else:
                    error_data.append({
                        "DesignationId": designation_id,
                        "message": "Validation failed",
                        "errors": serializer.errors
                    })

            except Exception as e:
                error_data.append({
                    "DesignationId": designation_id,
                    "message": str(e)
                })

        if updated_data:
            if error_data:
                return multi_status_response(
                    data=updated_data,
                    errors={'failedUpdates': error_data},
                    message='Some designations updated, others failed'
                )
            return success_response(updated_data, 'Designations updated successfully')
        
        return JsonResponse({
            "result": False,
            "message": "No designations were updated",
            "errors": {"failedUpdates": error_data}
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewAllDesignations(request):
    try:
        designations = Designation.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(designations, request)

        serializer = DesignationSerializer(designations, many=True)
        return success_response(serializer.data, 'Designations fetched successfully')
    except Exception as e:
        return server_error_response(e)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDesignationsById(request, DesignationId):
    try:
        designation = Designation.objects.get(DesignationId=DesignationId)
        serializer = DesignationSerializer(designation)
        return success_response(serializer.data, 'designation fetched successfully')
    except Designation.DoesNotExist:
        return not_found_response(f'No branch found with ID {DesignationId}')
    except Exception as e:
        return server_error_response(e)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bulkDeleteDesignation(request):
    try:
        designation_ids = request.data.get('DesignationIds')

        if not designation_ids or not isinstance(designation_ids, list):
            return validation_error_response({'DesignationIds': ['A list of designation IDs is required']})

        deleted_ids = []
        not_found_ids = []

        for designation_id in designation_ids:
            try:
                designation = Designation.objects.get(pk=designation_id)
                designation.delete()
                deleted_ids.append(designation_id)
            except Designation.DoesNotExist:
                not_found_ids.append(designation_id)

        response = {
            "message": f"Deleted {len(deleted_ids)} designation(s). {len(not_found_ids)} not found",
            "data": {
                "deleted": deleted_ids,
                "not_found": not_found_ids
            }
        }
        return success_response(response)

    except Exception as e:
        return server_error_response(e)


#------------------------------ Products Master Api ------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    try:
        data = request.data.copy()
        data['CreateBy'] = request.user.email
        data['UpdateBy'] = request.user.email

        serializer = ProductsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Product created successfully')
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_products(request):
    try:
        products = Products.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(products, request)

        serializer = ProductsSerializer(products, many=True)
        return success_response(serializer.data, 'Products retrieved successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, pk):
    try:
        # Validate required fields
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return JsonResponse({
                'result': False,
                'message': 'OwnerId, BranchId and DepartmentId are required for verification'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get product with context
        product = Products.objects.filter(
            pk=pk,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not product:
            return not_found_response(f'Product not found with ID {pk} for given context')

        # Prepare update data
        data = request.data.copy()
        data.pop("OwnerId", None)
        data.pop("BranchId", None)
        data.pop("DepartmentId", None)

        # Validate unexpected fields
        allowed_fields = set(ProductsSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate and update
        serializer = ProductsSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, 'Product updated successfully')
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, pk):
    try:
        product = Products.objects.get(pk=pk)
        product.delete()
        return no_content_response('Product deleted successfully')
    except Products.DoesNotExist:
        return not_found_response(f'No product found with ID {pk}')
    except Exception as e:
        return server_error_response(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_insert_products(request):
    try:
        products = request.data

        if not products or not isinstance(products, list):
            return validation_error_response({'products': ['A list of products is required']})

        # Check for duplicate names
        names = [p.get('Name') for p in products if p.get('Name')]
        if Products.objects.filter(Name__in=names).exists():
            return JsonResponse({
                'result': False,
                'message': 'Validation failed',
                'errors': 'One or more products with these names already exist'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductsSerializer(data=products, many=True)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Products created successfully')

        # Format bulk validation errors
        error_messages = []
        for idx, error in enumerate(serializer.errors):
            row_errors = [f"{field}: {', '.join(msgs)}" for field, msgs in error.items()]
            error_messages.append(f"Row {idx + 1}: " + "; ".join(row_errors))
        
        return JsonResponse({
            'result': False,
            'message': 'Validation failed',
            'errors': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def bulk_update_products(request):
    try:
        products = request.data

        if not isinstance(products, list):
            return validation_error_response({'products': ['A list of product objects is required']})

        updated_data = []
        error_data = []

        for prod_data in products:
            product_id = prod_data.get("id")
            Owner_id = prod_data.get("OwnerId")
            branch_id = prod_data.get("BranchId")
            department_id = prod_data.get("DepartmentId")

            if not product_id or not Owner_id or not branch_id or not department_id:
                error_data.append({
                    'id': product_id,
                    'message': 'ProductId, OwnerId, BranchId and DepartmentId are required'
                })
                continue

            try:
                product = Products.objects.filter(
                    id=product_id,
                    OwnerId=Owner_id,
                    BranchId=branch_id,
                    DepartmentId=department_id
                ).first()

                if not product:
                    error_data.append({
                        'id': product_id,
                        'message': f'Product not found with ID {product_id} for given context'
                    })
                    continue

                update_data = prod_data.copy()
                update_data.pop("OwnerId", None)
                update_data.pop("BranchId", None)
                update_data.pop("DepartmentId", None)

                allowed_fields = set(ProductsSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
                invalid_fields = set(update_data.keys()) - allowed_fields - {"id"}
                if invalid_fields:
                    error_data.append({
                        'id': product_id,
                        'message': f"Unexpected field(s): {', '.join(invalid_fields)}"
                    })
                    continue

                serializer = ProductsSerializer(product, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_data.append({
                        'id': product_id,
                        'data': serializer.data
                    })
                else:
                    error_data.append({
                        'id': product_id,
                        'message': 'Validation failed',
                        'errors': serializer.errors
                    })

            except Exception as e:
                error_data.append({
                    'id': product_id,
                    'message': str(e)
                })

        if updated_data:
            if error_data:
                return multi_status_response(
                    data=updated_data,
                    errors={'failedUpdates': error_data},
                    message='Some products updated, others failed'
                )
            return success_response(updated_data, 'Products updated successfully')
        
        return JsonResponse({
            'result': False,
            'message': 'No products were updated',
            'errors': {'failedUpdates': error_data}
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bulk_delete_products(request):
    try:
        ids = request.data.get('ids', [])

        if not ids or not isinstance(ids, list):
            return validation_error_response({'ids': ['A list of product IDs is required']})

        existing_ids = list(Products.objects.filter(id__in=ids).values_list('id', flat=True))
        missing_ids = list(set(ids) - set(existing_ids))

        if not existing_ids:
            return not_found_response(f'No products found for IDs: {", ".join(map(str, ids))}')

        deleted_count, _ = Products.objects.filter(id__in=existing_ids).delete()

        response = {
            'message': f"{deleted_count} product(s) deleted successfully",
            'data': {
                'deleted_ids': existing_ids,
                'not_found_ids': missing_ids
            }
        }
        return success_response(response)

    except Exception as e:
        return server_error_response(e)

#-----------------------  Broker Master ------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def createBroker(request):
    try:
        serializer = BrokerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Broker created successfully')
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_BrokerIdentification(request, BrokerId):
    try:
        broker = Broker.objects.get(pk=BrokerId)
        data = {
            "BrokerId": broker.BrokerId,
            "OwnerId": broker.OwnerId.id if broker.OwnerId else None,
            "BranchId": broker.BranchId_id,
            "DepartmentId": broker.DepartmentId_id,
            "LenderAssignedCode": broker.LenderAssignedCode,
            "BrokerName": broker.BrokerName,
            "BrokerType": broker.BrokerType,
            "ContactPerson": broker.ContactPerson,
            "BrokerCategory": broker.BrokerCategory
        }
        return success_response(data, 'Broker identification retrieved successfully')
    except Broker.DoesNotExist:
        return not_found_response('Broker not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_broker_contact_details(request, BrokerId):
    try:
        broker = Broker.objects.get(pk=BrokerId)
        data = {
            "PhoneNumber": broker.PhoneNumber,
            "AltPhoneNumber": broker.AltPhoneNumber,
            "Email": broker.Email,
            "Address": broker.Address,
            "City": broker.City,
            "state": broker.State,
            "Pincode": broker.Pincode,
            "AreaOfOperation": broker.AreaOfOperation
        }
        return success_response(data, 'Broker contact details retrieved successfully')
    except Broker.DoesNotExist:
        return not_found_response('Broker not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_broker_kyc_compliance(request, BrokerId):
    try:
        broker = Broker.objects.get(pk=BrokerId)
        data = {
            "PanNumber": broker.PanNumber,
            "GST_Number": broker.GST_Number,
            "AadhaarNumber": broker.AadhaarNumber,
            "IncorporationCert": broker.IncorporationCert.url if broker.IncorporationCert else None,
            "MSME_Certificate": broker.MSME_Certificate.url if broker.MSME_Certificate else None,
            "KycStatus": broker.KycStatus
        }
        return success_response(data, 'Broker KYC details retrieved successfully')
    except Broker.DoesNotExist:
        return not_found_response('Broker not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_broker_bank_details(request, BrokerId):
    try:
        broker = Broker.objects.get(pk=BrokerId)
        data = {
            "BankName": broker.BankName,
            "AccountNumber": broker.AccountNumber,
            "AccountHolderName": broker.AccountHolderName,
            "IFSC_Code": broker.IFSC_Code,
            "UPI_Id": broker.UPI_Id
        }
        return success_response(data, 'Broker bank details retrieved successfully')
    except Broker.DoesNotExist:
        return not_found_response('Broker not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_broker_agreement(request, BrokerId):
    try:
        broker = Broker.objects.get(pk=BrokerId)
        data = {
            "AgreementStartDate": broker.AgreementStartDate,
            "AgreementEndDate": broker.AgreementEndDate,
            "CommissionRate": broker.CommissionRate,
            "CommissionType": broker.CommissionType,
            "SignedAgreement": broker.SignedAgreement.url if broker.SignedAgreement else None,
            "TermsAndConditions": broker.TermsAndConditions
        }
        return success_response(data, 'Broker agreement details retrieved successfully')
    except Broker.DoesNotExist:
        return not_found_response('Broker not found')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_broker_status_audit(request, BrokerId):
    try:
        broker = Broker.objects.get(pk=BrokerId)
        data = {
            "Status": broker.Status,
            "Blacklisted": broker.Blacklisted,
            "LastAuditDate": broker.LastAuditDate,
            "Rating": broker.Rating
        }
        return success_response(data, 'Broker status and audit details retrieved successfully')
    except Broker.DoesNotExist:
        return not_found_response('Broker not found')
    except Exception as e:
        return server_error_response(e)


# GET ALL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllBrokerInfo(request):
    try:
        brokers = Broker.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(assignments, request)

        serializer = BrokerSerializer(brokers, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getBrokerInfoById(request, id):
    try:
        broker = Broker.objects.filter(BrokerId=id).first()
        if not broker:
            return not_found_response('broker not found')
        serializer = BrokerSerializer(broker)
        return success_response(serializer.data, 'broker retrieved successfully')
    except Exception as e:
        return server_error_response(e)


# GET ALL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getBrokerByIdInfo(request):
    try:
        brokers = Broker.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(assignments, request)

        serializer = AssignAgentSerializer(brokers, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_broker(request, BrokerId):
    try:
        broker = Broker.objects.filter(pk=BrokerId).first()
        if not broker:
            return not_found_response(broker if broker else type('Broker', (), {'id': BrokerId})())

        data = request.data.copy()
        data['UpdateBy'] = request.user.email  # auto-capture user
        # Remove file fields if no new file is provided (keep existing files)
        for field in ['IncorporationCert', 'MSME_Certificate', 'SignedAgreement']:
            if field not in request.FILES:
                data.pop(field, None)  
                
        serializer = BrokerSerializer(broker, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Broker updated successfully")
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_broker(request, BrokerId):
    try:
        broker = Broker.objects.get(BrokerId=BrokerId)
        broker.delete()
        return success_response(message='Broker deleted successfully')
    except Broker.DoesNotExist:
        return not_found_response('Broker not found')
    except Exception as e:
        return server_error_response(e)


#-----------------------  CustomerInfo Master ------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createCustomerInfo(request):
    try:
        serializer = CustomerInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Customer created successfully')
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

        
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateCustomerInfo(request, CustomerId):
    try:
        customer = Customer.objects.filter(pk=CustomerId).first()
        if not customer:
            return not_found_response(customer if customer else type('Customer', (), {'id': CustomerId})())

        data = request.data.copy()
        data['UpdateBy'] = request.user.email  # optional: track updater

        serializer = CustomerInfoSerializer(customer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Customer updated successfully")
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteCustomerInfo(request, CustomerId):
    try:
        customer = Customer.objects.filter(CustomerId=CustomerId).first()
        if not customer:
            return not_found_response('Customer not found')
        customer.delete()
        return success_response(message='Customer deleted successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCustomerInfoById(request, CustomerId):
    try:
        customer = Customer.objects.filter(CustomerId=CustomerId).first()
        if not customer:
            return not_found_response('Customer not found')
        serializer = CustomerInfoSerializer(customer)
        return success_response(serializer.data, 'Customer retrieved successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllCustomerInfo(request):
    try:
        customers = Customer.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(customers, request)

        serializer = CustomerInfoSerializer(customers, many=True)
        return success_response(serializer.data, 'Customers retrieved successfully')
    except Exception as e:
        return server_error_response(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulkCreateCustomersInfo(request):
    try:
        customers_data = request.data.get('customers')
        if not customers_data or not isinstance(customers_data, list):
            return validation_error_response({'customers': ['A list of customers is required']})
        
        serializer = CustomerInfoSerializer(data=customers_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, 'Bulk customers created successfully')
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulkDeleteCustomersInfo(request):
    try:
        ids = request.data.get("CustomerIds", [])
        if not ids or not isinstance(ids, list):
            return validation_error_response({'CustomerIds': ['A list of customer IDs is required']})

        deleted_count, _ = Customer.objects.filter(CustomerId__in=ids).delete()
        return success_response(
            data={"deleted_count": deleted_count},
            message=f"{deleted_count} customers deleted successfully"
        )
    except Exception as e:
        return server_error_response(e)
    
#--------------------------- vehicle apis ---------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def createVehicle(request):
    try:
        serializer = VehicleSerializer(data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Vehicle created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateVehicle(request, pk):
    try:
        # Step 1: Extract OwnerId, BranchId and DepartmentId from request for validation
        Owner_id = request.data.get("OwnerId")
        branch_id = request.data.get("BranchId")
        department_id = request.data.get("DepartmentId")

        if not Owner_id or not branch_id or not department_id:
            return validation_error_response({
                'message': ['OwnerId, BranchId and DepartmentId are required for validation.']
            })

        # Step 2: Fetch vehicle by pk, branch, and department
        vehicle = Vehicle.objects.filter(
            pk=pk,
            OwnerId=Owner_id,
            BranchId=branch_id,
            DepartmentId=department_id
        ).first()

        if not vehicle:
            return not_found_response('Vehicle not found for the given OwnerId, BranchId and DepartmentId.')

        # Step 3: Clean data (remove branch & dept to avoid override)
        data = request.data.copy()
        if hasattr(data, '_mutable'):
            data._mutable = True
        data.pop('OwnerId', None)
        data.pop('BranchId', None)
        data.pop('DepartmentId', None)

        # Step 4: Validate unexpected fields
        allowed_fields = set(VehicleSerializer().get_fields().keys()) - {'OwnerId', 'BranchId', 'DepartmentId'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            return validation_error_response({
                'message': [f"Unexpected field(s): {', '.join(invalid_fields)}"]
            })

        # Step 5: Validate and update
        serializer = VehicleSerializer(vehicle, data=data, partial=True)
        if serializer.is_valid():
            vehicle = serializer.save()

            # Step 6: Handle file updates
            file_fields = ['RC_Copy', 'InsuranceCopy', 'InvoiceCopy', 'FitnessCertificate']
            for file_field in file_fields:
                if file_field in request.FILES:
                    setattr(vehicle, file_field, request.FILES[file_field])
            vehicle.save()

            return success_response(serializer.data, 'Vehicle updated successfully.')

        # Step 7: Handle serializer errors
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteVehicle(request, pk):
    try:
        vehicle = Vehicle.objects.get(pk=pk)
        vehicle.delete()
        return success_response(message="Vehicle deleted successfully")
    except Vehicle.DoesNotExist:
        return not_found_response("Vehicle not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllVehicles(request):
    try:
        vehicles = Vehicle.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(vehicles, request)

        serializer = VehicleSerializer(vehicles, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getVehicleById(request, pk):
    try:
        vehicle = Vehicle.objects.get(pk=pk)
        serializer = VehicleSerializer(vehicle)
        return success_response(serializer.data)
    except Vehicle.DoesNotExist:
        return not_found_response("Vehicle not found")
    except Exception as e:
        return server_error_response(e)
    

#-----------------------------  Seizure apis ----------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def createSeizure(request):
    try:
        serializer = InitiateSeizureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Seizure created successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)


# GET ALL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllSeizures(request):
    try:
        seizures = InitiateSeizure.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(seizures, request)

        serializer = InitiateSeizureSerializer(seizures, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getSeizureById(request, Id):
    try:
        seizure = InitiateSeizure.objects.filter(Id=Id).first()
        if not seizure:
            return not_found_response("Seizure not found")
        serializer = InitiateSeizureSerializer(seizure)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# UPDATE BY ID
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def updateSeizure(request, Id):
    try:
        seizure = InitiateSeizure.objects.filter(pk=Id).first()
        if not seizure:
            return not_found_response(seizure if seizure else type('InitiateSeizure', (), {'id': Id})())

        data = request.data.copy()
        data['UpdateBy'] = request.user.email  # Optional audit info

        serializer = InitiateSeizureSerializer(seizure, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, 'Seizure updated successfully.')
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)
    

# DELETE BY ID
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteSeizure(request, Id):
    try:
        seizure = InitiateSeizure.objects.filter(Id=Id).first()
        if not seizure:
            return not_found_response("Seizure not found")
        seizure.delete()
        return success_response(message="Seizure deleted successfully")
    except Exception as e:
        return server_error_response(e)
    

#------------------------------ AssignAgent  ------------------------ 


# CREATE
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def createAssignAgent(request):
    try:
        data = request.data.copy()
        photos = request.FILES.getlist('SitePhotosPre')

        serializer = AssignAgentSerializer(data=data)
        if serializer.is_valid():
            assign_agent = serializer.save()

            # Save SitePhotos
            for photo in photos:
                img = SitePhoto.objects.create(Image=photo)
                assign_agent.SitePhotosPre.add(img)

            return created_response(
                AssignAgentSerializer(assign_agent).data,
                "Agent assigned successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# GET ALL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllAssignAgent(request):
    try:
        assignments = AssignAgent.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(assignments, request)

        serializer = AssignAgentSerializer(assignments, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAssignAgentById(request, Id):
    try:
        assign = AssignAgent.objects.filter(Id=Id).first()
        if not assign:
            return not_found_response("AssignAgent not found")
        serializer = AssignAgentSerializer(assign)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def updateAssignAgent(request, Id):
    try:
        instance = AssignAgent.objects.filter(Id=Id).first()
        if not instance:
            return not_found_response("AssignAgent not found")

        data = request.data.copy()
        photos = request.FILES.getlist('SitePhotosPre')

        serializer = AssignAgentSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            assign_agent_instance = serializer.save()

            # Optional new photos
            for photo in photos:
                img = SitePhoto.objects.create(Image=photo)
                assign_agent_instance.SitePhotosPre.add(img)

            return success_response(
                AssignAgentSerializer(assign_agent_instance).data,
                "AssignAgent updated successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteAssignAgent(request, Id):
    try:
        assign = AssignAgent.objects.filter(Id=Id).first()
        if not assign:
            return not_found_response("AssignAgent not found")
        assign.delete()
        return success_response(message="AssignAgent deleted successfully")
    except Exception as e:
        return server_error_response(e)
    

#------------------------------ SeizureExecution  ------------------------ 

# CREATE
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def createSeizureExecution(request):
    try:
        data = request.data.copy()
        asset_photos = request.FILES.getlist('AssetPhotos')
        
        serializer = SeizureExecutionSerializer(data=data)
        if serializer.is_valid():
            execution = serializer.save()

            # Save AssetPhotos
            for photo in asset_photos:
                image_obj = AssetPhoto.objects.create(Image=photo)
                execution.AssetPhotos.add(image_obj)

            return created_response(
                SeizureExecutionSerializer(execution).data,
                "Seizure execution created successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# GET ALL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllSeizureExecution(request):
    try:
        executions = SeizureExecution.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(executions, request)

        serializer = SeizureExecutionSerializer(executions, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getSeizureExecutionById(request, Id):
    try:
        execution = SeizureExecution.objects.filter(Id=Id).first()
        if not execution:
            return not_found_response("Execution not found")
        serializer = SeizureExecutionSerializer(execution)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def updateSeizureExecution(request, Id):
    try:
        instance = SeizureExecution.objects.filter(Id=Id).first()
        if not instance:
            return not_found_response("Execution not found")

        data = request.data.copy()
        asset_photos = request.FILES.getlist('AssetPhotos')

        serializer = SeizureExecutionSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            execution = serializer.save()

            # Save new AssetPhotos
            for photo in asset_photos:
                photo_obj = AssetPhoto.objects.create(Image=photo)
                execution.AssetPhotos.add(photo_obj)

            return success_response(
                SeizureExecutionSerializer(execution).data,
                "Seizure execution updated successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteSeizureExecution(request, Id):
    try:
        execution = SeizureExecution.objects.filter(Id=Id).first()
        if not execution:
            return not_found_response("Execution not found")
        execution.delete()
        return success_response(message="Execution deleted successfully")
    except Exception as e:
        return server_error_response
    
#------------------------------------AssignBroker-----------------

# CREATE
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def createAssignBroker(request):
    try:
        serializer = AssignBrokerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(serializer.data, "Broker assigned successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# GET ALL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllAssignBrokers(request):
    try:
        brokers = AssignBroker.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(brokers, request)

        serializer = AssignBrokerSerializer(brokers, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAssignBrokerById(request, Id):
    try:
        broker = AssignBroker.objects.filter(Id=Id).first()
        if not broker:
            return not_found_response("Broker assignment not found")
        serializer = AssignBrokerSerializer(broker)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def updateAssignBroker(request, Id):
    try:
        broker = AssignBroker.objects.filter(Id=Id).first()
        if not broker:
            return not_found_response("Broker assignment not found")

        serializer = AssignBrokerSerializer(broker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Broker assignment updated successfully")
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteAssignBroker(request, Id):
    try:
        broker = AssignBroker.objects.filter(Id=Id).first()
        if not broker:
            return not_found_response("Broker assignment not found")
        broker.delete()
        return success_response(message="Broker assignment deleted successfully")
    except Exception as e:
        return server_error_response(e)

#------------------------------------ SaleExecution -----------------

# CREATE
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def createSaleExecution(request):
    try:
        serializer = SaleExecutionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(
                serializer.data, 
                "Sale executed successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# GET ALL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllSaleExecutions(request):
    try:
        executions = SaleExecution.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(executions, request)

        serializer = SaleExecutionSerializer(executions, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getSaleExecutionById(request, Id):
    try:
        execution = SaleExecution.objects.filter(Id=Id).first()
        if not execution:
            return not_found_response("Sale execution not found")
        serializer = SaleExecutionSerializer(execution)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def updateSaleExecution(request, Id):
    try:
        execution = SaleExecution.objects.filter(Id=Id).first()
        if not execution:
            return not_found_response("Sale execution not found")

        serializer = SaleExecutionSerializer(
            execution, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return success_response(
                serializer.data,
                "Sale execution updated successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteSaleExecution(request, Id):
    try:
        execution = SaleExecution.objects.filter(Id=Id).first()
        if not execution:
            return not_found_response("Sale execution not found")
        execution.delete()
        return success_response(message="Sale execution deleted successfully")
    except Exception as e:
        return server_error_response(e)
    
#-------------------------------------- RecoveryClosure ----------------------------------- 

# CREATE
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def createRecoveryClosure(request):
    try:
        serializer = RecoveryClosureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(
                serializer.data,
                "Recovery closure created successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# GET ALL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllRecoveryClosures(request):
    try:
        closures = RecoveryClosure.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(closures, request)

        serializer = RecoveryClosureSerializer(closures, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getRecoveryClosureById(request, Id):
    try:
        closure = RecoveryClosure.objects.filter(Id=Id).first()
        if not closure:
            return not_found_response("Recovery closure not found")
        serializer = RecoveryClosureSerializer(closure)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def updateRecoveryClosure(request, Id):
    try:
        closure = RecoveryClosure.objects.filter(Id=Id).first()
        if not closure:
            return not_found_response("Recovery closure not found")
        data = request.data.copy()  # Make mutable
        
        # If no new file is uploaded, remove the field to keep the existing file
        if "NodalApproval" not in request.FILES:
            data.pop("NodalApproval", None)
        if "AuditReport" not in request.FILES:
            data.pop("AuditReport", None)

        serializer = RecoveryClosureSerializer(closure, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                serializer.data,
                "Recovery closure updated successfully"
            )
        
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteRecoveryClosure(request, Id):
    try:
        closure = RecoveryClosure.objects.filter(Id=Id).first()
        if not closure:
            return not_found_response("Recovery closure not found")
        closure.delete()
        return success_response(message="Recovery closure deleted successfully")
    except Exception as e:
        return server_error_response(e)


from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

# ------------------ Create Collateral ------------------


from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from datetime import datetime
import json
import uuid
from django.http import QueryDict

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def createCollateral(request):
    try:
        data = request.data
        # Convert request.data to mutable if needed
        if isinstance(request.data, QueryDict):
            data = request.data.dict()
        else:
            data = request.data.copy()
        
        # Handle list fields like AssetId
        if 'AssetId' in data and isinstance(data['AssetId'], str):
            try:
                data['AssetId'] = json.loads(data['AssetId'])
            except json.JSONDecodeError:
                data['AssetId'] = [int(id.strip()) for id in data['AssetId'].split(',') if id.strip()]
        # Validate required fields
        required_fields = [
            'OwnerId', 'BranchId', 'DepartmentId', 'LoanId','AssetId', 'CollateralType','CollateralStatus',
            'OwnerName', 'OwnershipPercentage', 'TitleDocNumber', 'CurrentValue',
            'ValuationDate', 'ValuerRegNumber', 'CollateralScore','EncumbranceStatus','LienHolderDetails',
            'InsurancePolicyNo','TitleDeedCopy', 'ValuationReport','InsuranceDocument', 'SitePhotos'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return validation_error_response({field: ["This field is required."] for field in missing_fields})

        # Validate collateral type
        collateral_type = data['CollateralType'].lower()
        valid_types = [choice[0] for choice in Collateral.COLLATERAL_TYPES]
        if collateral_type not in valid_types:
            return validation_error_response({
                'CollateralType': [f"Invalid collateral type. Must be one of: {', '.join(valid_types)}"]
            })
        
        # Validate ownership percentage
        try:
            ownership_percentage = float(data['OwnershipPercentage'])
            if not (0 < ownership_percentage <= 100):
                raise ValueError
        except ValueError:
            return validation_error_response({
                'OwnershipPercentage': ["Must be a decimal number between 0 and 100."]
            })
        
    # Convert string boolean to Python boolean
        def parse_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.strip().lower() in ['true', '1', 'yes']
            return False
        
        data['EncumbranceStatus'] = parse_bool(data['EncumbranceStatus'])
        data['FireSafetyCert'] = parse_bool(data['FireSafetyCert'])
        
        # Validate type-specific fields
        type_specific_fields = {}
        type_specific_validations = {
            'real estate': validate_real_estate_fields,
            'vehicle': validate_vehicle_fields,
            'financial': validate_financial_fields,
            'inventory': validate_inventory_fields,
            'machinery': validate_machinery_fields,
            'others': validate_others_fields
        }
        
        validation_func = type_specific_validations.get(collateral_type)
        if validation_func:
            validation_result = validation_func(data)
            if validation_result:
                return validation_result
            type_specific_fields = {k: v for k, v in data.items() if k not in required_fields}
        
        # Create collateral in transaction
        with transaction.atomic():
            # Create main collateral record
            collateral_data = {
                'OwnerId_id': data['OwnerId'],
                'BranchId_id': data['BranchId'],
                'DepartmentId_id': data['DepartmentId'],
                'LoanId_id': data['LoanId'],
                # 'AssetId':data['AssetId'],
                'CollateralType': data['CollateralType'],
                'CollateralStatus': data.get('CollateralStatus', 'active'),
                'OwnerName': data['OwnerName'],
                'OwnershipPercentage': ownership_percentage,
                'TitleDocNumber': data['TitleDocNumber'],
                'EncumbranceStatus': data['EncumbranceStatus'],
                'LienHolderDetails': data.get('LienHolderDetails'),
                'CurrentValue': data['CurrentValue'],
                'ValuationDate': data['ValuationDate'],
                'ValuerRegNumber': data['ValuerRegNumber'],
                'InsurancePolicyNo': data.get('InsurancePolicyNo'),
                'CollateralScore': data['CollateralScore'],
            }
            print(collateral_data)  
            collateral = Collateral(**collateral_data)
            collateral.full_clean()
            collateral.save()

            # Now set the M2M field
            if 'AssetId' in data:
                collateral.AssetId.set(data['AssetId'])

            
            # Create type-specific collateral record
            type_specific_models = {
                'real estate': RealEstateCollateral,
                'vehicle': VehicleCollateral,
                'financial': FinancialCollateral,
                'inventory': InventoryCollateral,
                'machinery': MachineryCollateral,
                'others': OthersCollateral
            }
            
            model_class = type_specific_models.get(collateral_type)
            if model_class:
                type_specific_fields['CollateralId_id'] = collateral.CollateralId
                type_specific_record = model_class(**type_specific_fields)
                type_specific_record.full_clean()
                type_specific_record.save()
            
            # Handle document uploads
            document_fields = {
                'TitleDeedCopy': request.FILES.get('TitleDeedCopy'),
                'ValuationReport': request.FILES.get('ValuationReport'),
                'InsuranceDocument': request.FILES.get('InsuranceDocument'),
                'SitePhotos': request.FILES.get('SitePhotos')
            }
            
            if any(document_fields.values()):
                document_data = {
                    'CollateralId_id': collateral.CollateralId,
                    **{k: v for k, v in document_fields.items() if v is not None}
                }
                CollateralDocuments.objects.create(**document_data)
            
            # Prepare response data
            response_data = {
                'collateral_id': collateral.CollateralId,
                'collateral_type': collateral.get_CollateralType_display(),
                'status': collateral.get_CollateralStatus_display(),
                'owner_name': collateral.OwnerName,
                'current_value': collateral.CurrentValue,
                'risk_flag': collateral.RiskFlag,
                'documents_uploaded': bool(any(document_fields.values()))
            }

            return created_response(response_data, "Collateral created successfully")
    
    except ValidationError as e:
        return validation_error_response(e.message_dict)
    except Exception as e:
        return server_error_response(e)

# Validation functions for type-specific fields
def validate_real_estate_fields(data):
    required_fields = ['Latitude', 'Longitude', 'BuildingType', 'AreaSqft']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for real estate collateral."] for field in missing_fields})
    
    try:
        latitude = float(data['Latitude'])
        if not (-90 <= latitude <= 90):
            raise ValueError
    except ValueError:
        return validation_error_response({
            'Latitude': ["Must be a valid latitude between -90 and 90."]
        })
    
    try:
        longitude = float(data['Longitude'])
        if not (-180 <= longitude <= 180):
            raise ValueError
    except ValueError:
        return validation_error_response({
            'Longitude': ["Must be a valid longitude between -180 and 180."]
        })
    
    try:
        area_sqft = float(data['AreaSqft'])
        if area_sqft <= 0:
            raise ValueError
    except ValueError:
        return validation_error_response({
            'AreaSqft': ["Must be a positive number."]
        })
    
    return None

def validate_vehicle_fields(data):
    required_fields = ['VehicleRC_Number', 'EngineNumber', 'ChassisNumber']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for vehicle collateral."] for field in missing_fields})
    

    return None

def validate_financial_fields(data):
    required_fields = ['InstrumentType', 'Instrument_ISIN', 'InstitutionName', 'MaturityDate']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for financial collateral."] for field in missing_fields})
    
    # try:
    #     maturity_date = datetime.strptime(data['MaturityDate'], '%Y-%m-%d').date()
    #     if maturity_date < datetime.now().date():
    #         return validation_error_response({
    #             'MaturityDate': ["Maturity date cannot be in the past."]
    #         })
    # except ValueError:
    #     return validation_error_response({
    #         'MaturityDate': ["Invalid date format. Use YYYY-MM-DD."]
    #     })
    
    try:
        haircut = float(data.get('HaircutPercentage', 0))
        if not (0 <= haircut <= 100):
            raise ValueError
    except ValueError:
        return validation_error_response({
            'HaircutPercentage': ["Must be a decimal number between 0 and 100."]
        })
    
    return None

def validate_inventory_fields(data):
    required_fields = ['Description', 'Quantity', 'StorageLocation']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for inventory collateral."] for field in missing_fields})
    
    try:
        quantity = int(data['Quantity'])
        if quantity <= 0:
            raise ValueError
    except ValueError:
        return validation_error_response({
            'Quantity': ["Must be a positive integer."]
        })
    
    return None

def validate_machinery_fields(data):
    required_fields = ['MachineType', 'Manufacturer', 'PurchaseYear']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for machinery collateral."] for field in missing_fields})
    
    # try:
    #     purchase_year = int(data['PurchaseYear'])
    #     current_year = datetime.now().year
    #     if not (1900 <= purchase_year <= current_year):
    #         raise ValueError
    # except ValueError:
    #     return validation_error_response({
    #         'PurchaseYear': [f"Must be a valid year between 1900 and {current_year}."]
    #     })
    
    return None

def validate_others_fields(data):
    if 'Description' not in data:
        return validation_error_response({
            'Description': ["This field is required for other collateral types."]
        })
    return None

# ------------------ Get All Collateral ------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllCollateral(request):
    try:
        collateral = Collateral.objects.all().prefetch_related(
            'RealEstate',
            'Vehicle',
            'Financial',
            'Inventory',
            'Machinery',
            'Others',
            'Documents'  # Add this to prefetch documents
        )
        serializer = CollateralSerializer(collateral, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)
# ------------------ Get Collateral by ID ------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCollateralById(request, CollateralId):
    try:
        collateral = Collateral.objects.select_related(
            'OwnerId', 'BranchId', 'DepartmentId', 'LoanId'
        ).prefetch_related(
            'RealEstate',
            'Vehicle',
            'Financial',
            'Inventory',
            'Machinery',
            'Others',
            'Documents'
        ).get(CollateralId=CollateralId)
        
        serializer = CollateralSerializer(collateral)
        return success_response(serializer.data)
    except Collateral.DoesNotExist:
        return not_found_response("Collateral not found.")
    except Exception as e:
        return server_error_response(e)
# ------------------ Update Collateral ------------------
@api_view(['PUT', 'PATCH'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def updateCollateral(request, CollateralId):
    try:
        try:
            # Fix: Use prefetch_related for M2M fields
            collateral = Collateral.objects.select_related(
                'OwnerId', 'BranchId', 'DepartmentId', 'LoanId'
            ).prefetch_related(
                'AssetId',
                'RealEstate',
                'Vehicle',
                'Financial',
                'Inventory',
                'Machinery',
                'Others',
                'Documents'
            ).get(CollateralId=CollateralId)
        except Collateral.DoesNotExist:
            return not_found_response("Collateral not found")

        # Verify IDs match the request
        id_checks = {
            'OwnerId': request.data.get('OwnerId'),
            'BranchId': request.data.get('BranchId'),
            'DepartmentId': request.data.get('DepartmentId'),
            'LoanId': request.data.get('LoanId'),
            # 'AssetId': request.data.get('AssetId')
        }

        for field, value in id_checks.items():
            if value and str(getattr(collateral, f"{field}_id", getattr(collateral, field))) != str(value):
                return validation_error_response({
                    field: ["Cannot change reference IDs during update"]
                })

        # Prepare data for serializer
        data = request.data.copy()
        files = request.FILES

        # Handle file uploads
        document_fields = {
            'TitleDeedCopy': files.get('TitleDeedCopy'),
            'ValuationReport': files.get('ValuationReport'),
            'InsuranceDocument': files.get('InsuranceDocument'),
            'SitePhotos': files.get('SitePhotos')
        }

        if any(document_fields.values()):
            data['Documents'] = {k: v for k, v in document_fields.items() if v}

        # Validate and update
        serializer = CollateralUpdateSerializer(
            collateral,
            data=data,
            partial=request.method == 'PATCH'
        )

        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        try:
            with transaction.atomic():
                updated_collateral = serializer.save()
                
                # Recalculate RiskFlag if CollateralScore updated
                if 'CollateralScore' in data:
                    updated_collateral.RiskFlag = updated_collateral.CollateralScore >= 8
                    updated_collateral.save()

                # Prepare response data
                response_data = CollateralSerializer(updated_collateral).data
                return success_response(response_data, "Collateral updated successfully")

        except Exception as e:
            return server_error_response(str(e))

    except Exception as e:
        return server_error_response(str(e))

# ------------------ Delete Collateral ------------------
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteCollateral(request, CollateralId):
    try:
        collateral = Collateral.objects.get(CollateralId=CollateralId)
        collateral.delete()
        return no_content_response("Collateral deleted successfully.")
    except ObjectDoesNotExist:
        return not_found_response("Collateral not found.")
    except Exception as e:
        return server_error_response(e)


#---------------------------------LoanProductList-------------------------------------------

# Combined List and Create view
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def LoanProductListCreate(request):
    try:
        if request.method == 'GET':
            products = LoanProductMaster.objects.all()
            # paginator = PageNumberPagination()
            # paginated_auctions = paginator.paginate_queryset(products, request)

            serializer = LoanProductMasterSerializer(products, many=True)
            return success_response(serializer.data)
            
        elif request.method == 'POST':
            data = request.data.copy()
            data['CreatedBy'] = request.user.email

            serializer = LoanProductMasterSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return created_response(serializer.data, "Loan Product created successfully")

            return validation_error_response(serializer.errors)


    except Exception as e:
        return server_error_response(e)
    


# Detail, Update, Delete view
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def LoanProductDetail(request, pk):
    try:
        try:
            product = LoanProductMaster.objects.get(ProductId=pk)
        except LoanProductMaster.DoesNotExist:
            return not_found_response("Loan Product not found")

        if request.method == 'GET':
            serializer = LoanProductMasterSerializer(product)
            return success_response(serializer.data)

        elif request.method == 'PUT':
            try:
                product = LoanProductMaster.objects.filter(pk=pk).first()
                if not product:
                    return not_found_response(product if product else type('LoanProductMaster', (), {'id': pk})())

                data = request.data.copy()
                data['UpdateBy'] = request.user.email  # Optional: track who updated it

                serializer = LoanProductMasterSerializer(product, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return success_response(serializer.data, "Loan Product updated successfully")
                return validation_error_response(serializer.errors)
            except Exception as e:
                return server_error_response(e)

        elif request.method == 'DELETE':
            product.delete()
            return success_response(message="Loan Product deleted successfully")

    except Exception as e:
        return server_error_response(e)


#----------------------- InterestConfiguration ----------------------------------------

# CREATE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_interest_config(request):
    try:
        ProductId = request.data.get('ProductId')

        if InterestConfiguration.objects.filter(ProductId=ProductId).exists():
            return validation_error_response({
                'ProductId': ['Configuration already exists for this product']
            })

        serializer = InterestConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(
                serializer.data,
                "Configuration created successfully"
            )
        return validation_error_response(serializer.errors)

    except Exception as e:
        return server_error_response(e)

# LIST ALL
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_interest_configs(request):
    try:
        configs = InterestConfiguration.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(configs, request)

        serializer = InterestConfigSerializer(configs, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY PRODUCT ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_interest_config_by_product(request, ProductId):
    try:
        config = InterestConfiguration.objects.get(ProductId_id=ProductId)
        serializer = InterestConfigSerializer(config)
        return success_response(serializer.data)
    except InterestConfiguration.DoesNotExist:
        return not_found_response("Configuration not found")
    except Exception as e:
        return server_error_response(e)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_interest_config(request, id):
    try:
        config = InterestConfiguration.objects.get(id=id)
        serializer = InterestConfigSerializer(config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                serializer.data,
                "Configuration updated successfully"
            )
        return validation_error_response(serializer.errors)
    except InterestConfiguration.DoesNotExist:
        return not_found_response("Configuration not found")
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_interest_config(request, ProductId):
    try:
        config = InterestConfiguration.objects.get(ProductId_id=ProductId)
        config.delete()
        return success_response(message="Configuration deleted successfully")
    except InterestConfiguration.DoesNotExist:
        return not_found_response("Configuration not found")
    except Exception as e:
        return server_error_response(e)

# --------------------------- calculate_emi ---------------------------- 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_emi(request):
    try:
        # Validate required fields
        ProductId = request.data.get("ProductId")
        principal = request.data.get("Principal")
        tenure = request.data.get("TenureMonths")

        if not all([ProductId, principal, tenure]):
            return validation_error_response({
                'message': ['ProductId, Principal and TenureMonths are required']
            })

        # Get interest configuration
        config = InterestConfiguration.objects.get(ProductId_id=ProductId)

        # Calculate EMI based on interest type
        if config.InterestType == "Fixed":
            emi = calculate_fixed_emi(principal, float(config.BaseInterestRate), tenure)
        elif config.InterestType == "Reducing":
            emi = calculate_reducing_emi(principal, float(config.BaseInterestRate), tenure)
        elif config.InterestType == "Custom":
            if not config.InterestFormula:
                return validation_error_response({
                    'InterestFormula': ['Custom formula is missing in configuration']
                })
            emi = calculate_custom_formula(principal, float(config.BaseInterestRate), tenure, config.InterestFormula)
        else:
            return validation_error_response({
                'InterestType': ['Invalid interest type specified']
            })

        # Return successful response with EMI data
        return success_response({
            "ProductId": ProductId,
            "interest_type": config.InterestType,
            "emi": emi,
            "interest_rate": config.BaseInterestRate,
            "tenure_months": tenure,
            "principal_amount": principal
        }, "EMI calculated successfully")

    except InterestConfiguration.DoesNotExist:
        return not_found_response("Interest configuration not found for this product")
    except ValueError as ve:
        return validation_error_response({
            'calculation': [str(ve)]
        })
    except Exception as e:
        return server_error_response(e)
    

#------------------------------ Charge -----------------------------------

# CREATE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createCharge(request):
    try:
        serializer = ChargeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(
                serializer.data,
                "Charge created successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# GET ALL
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllCharges(request):
    try:
        charges = Charge.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(charges, request)

        serializer = ChargeSerializer(charges, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getChargeById(request, id):
    try:
        charge = Charge.objects.get(id=id)
        serializer = ChargeSerializer(charge)
        return success_response(serializer.data)
    except Charge.DoesNotExist:
        return not_found_response("Charge not found")
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateCharge(request, id):
    try:
        charge = Charge.objects.get(id=id)
        serializer = ChargeSerializer(charge, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                serializer.data,
                "Charge updated successfully"
            )
        return validation_error_response(serializer.errors)
    except Charge.DoesNotExist:
        return not_found_response("Charge not found")
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteCharge(request, id):
    try:
        charge = Charge.objects.get(id=id)
        charge.delete()
        return success_response(message="Charge deleted successfully")
    except Charge.DoesNotExist:
        return not_found_response("Charge not found")
    except Exception as e:
        return server_error_response(e)
    
#----------------------------------------------  
# CREATE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createPenalty(request):
    try:
        serializer = PenaltySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(
                serializer.data,
                "Penalty created successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# LIST ALL
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listPenalties(request):
    try:
        penalties = Penalty.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(penalties, request)

        serializer = PenaltySerializer(penalties, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPenaltyById(request, pk):
    try:
        penalty = Penalty.objects.get(pk=pk)
        serializer = PenaltySerializer(penalty)
        return success_response(serializer.data)
    except Penalty.DoesNotExist:
        return not_found_response("Penalty not found")
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updatePenalty(request, pk):
    try:
        penalty = Penalty.objects.get(pk=pk)
        serializer = PenaltySerializer(penalty, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                serializer.data,
                "Penalty updated successfully"
            )
        return validation_error_response(serializer.errors)
    except Penalty.DoesNotExist:
        return not_found_response("Penalty not found")
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletePenalty(request, pk):
    try:
        penalty = Penalty.objects.get(pk=pk)
        penalty.delete()
        return success_response(message="Penalty deleted successfully")
    except Penalty.DoesNotExist:
        return not_found_response("Penalty not found")
    except Exception as e:
        return server_error_response(e)
    

#---------------------------------------------------------------------

# CREATE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createTenureAmount(request):
    try:
        serializer = TenureAmountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(
                serializer.data,
                "Tenure & Amount created successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# LIST ALL
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listTenureAmounts(request):
    try:
        objs = TenureAmount.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(objs, request)

        serializer = TenureAmountSerializer(objs, many=True)
        return success_response(serializer.data)
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTenureAmountById(request, pk):
    try:
        obj = TenureAmount.objects.get(pk=pk)
        serializer = TenureAmountSerializer(obj)
        return success_response(serializer.data)
    except TenureAmount.DoesNotExist:
        return not_found_response("Tenure & Amount not found")
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateTenureAmount(request, pk):
    try:
        obj = TenureAmount.objects.get(pk=pk)
        serializer = TenureAmountSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                serializer.data,
                "Tenure & Amount updated successfully"
            )
        return validation_error_response(serializer.errors)
    except TenureAmount.DoesNotExist:
        return not_found_response("Tenure & Amount not found")
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteTenureAmount(request, pk):
    try:
        obj = TenureAmount.objects.get(pk=pk)
        obj.delete()
        return success_response(message="Tenure & Amount deleted successfully")
    except TenureAmount.DoesNotExist:
        return not_found_response("Tenure & Amount not found")
    except Exception as e:
        return server_error_response(e)

#--------------------------------------------------

# CREATE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createBusinessRule(request):
    try:
        serializer = BusinessRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(
                serializer.data,
                "BusinessRule created successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# LIST ALL
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listBusinessRules(request):
    try:
        rules = BusinessRule.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(rules, request)

        serializer = BusinessRuleSerializer(rules, many=True)
        return success_response(
            serializer.data,
            "Business Rules fetched successfully"
        )
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getBusinessRuleById(request, pk):
    try:
        rule = BusinessRule.objects.get(pk=pk)
        serializer = BusinessRuleSerializer(rule)
        return success_response(
            serializer.data,
            "Business Rule fetched successfully"
        )
    except BusinessRule.DoesNotExist:
        return not_found_response("Business Rule not found")
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateBusinessRule(request, pk):
    try:
        rule = BusinessRule.objects.get(pk=pk)
        serializer = BusinessRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                serializer.data,
                "Business Rule updated successfully"
            )
        return validation_error_response(serializer.errors)
    except BusinessRule.DoesNotExist:
        return not_found_response("Business Rule not found")
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteBusinessRule(request, pk):
    try:
        rule = BusinessRule.objects.get(pk=pk)
        rule.delete()
        return success_response(message="Business Rule deleted successfully")
    except BusinessRule.DoesNotExist:
        return not_found_response("Business Rule not found")
    except Exception as e:
        return server_error_response(e)
    

#----------------------------------------------------------

# CREATE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createUDF_Mapping(request):
    try:
        serializer = UDFMappingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return created_response(
                serializer.data,
                "UDF Mapping created successfully"
            )
        return validation_error_response(serializer.errors)
    except Exception as e:
        return server_error_response(e)

# LIST ALL
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listUDF_Mapping(request):
    try:
        mappings = UDFMapping.objects.all()
        # paginator = PageNumberPagination()
        # paginated_auctions = paginator.paginate_queryset(mappings, request)

        serializer = UDFMappingSerializer(mappings, many=True)
        return success_response(
            serializer.data,
            "UDF Mappings fetched successfully"
        )
    except Exception as e:
        return server_error_response(e)

# GET BY ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUDF_MappingById(request, pk):
    try:
        mapping = UDFMapping.objects.get(pk=pk)
        serializer = UDFMappingSerializer(mapping)
        return success_response(
            serializer.data,
            "UDF Mapping fetched successfully"
        )
    except UDFMapping.DoesNotExist:
        return not_found_response("UDF Mapping not found")
    except Exception as e:
        return server_error_response(e)

# UPDATE
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUDF_Mapping(request, pk):
    try:
        mapping = UDFMapping.objects.get(pk=pk)
        serializer = UDFMappingSerializer(mapping, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                serializer.data,
                "UDF Mapping updated successfully"
            )
        return validation_error_response(serializer.errors)
    except UDFMapping.DoesNotExist:
        return not_found_response("UDF Mapping not found")
    except Exception as e:
        return server_error_response(e)

# DELETE
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUDF_Mapping(request, pk):
    try:
        mapping = UDFMapping.objects.get(pk=pk)
        mapping.delete()
        return success_response(message="UDF Mapping deleted successfully")
    except UDFMapping.DoesNotExist:
        return not_found_response("UDF Mapping not found")
    except Exception as e:
        return server_error_response(e)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_countries(request):
    countries = Country.objects.all()
    serializer = CountrySerializer(countries, many=True)
    return success_response(
            serializer.data,
            "all_countries fetched successfully"
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_currencies(request):
    currencies = Currency.objects.all()
    serializer = CurrencySerializer(currencies, many=True)
    return success_response(
            serializer.data,
            "all_currencie fetched successfully"
        )


#-------------------------------------------------------------------------------------
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from .models import LoanMasters
from Masters.models import Customer, Broker, Collateral, InitiateSeizure
from InquiryLoanProcess.models import NewInquiry, LoanApplication
from DisSetSystem.models import Disbursement, LoanClosure, LoanForeclosure, LoanRenewal
from Auction.models import AuctionSetup
from LoginAuth.models import User
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import json
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
@transaction.atomic
def createLoanMasters(request):
    try:
        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "result": False,
                "message": "Invalid JSON data"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate field names in request
        required_fields = [
            'customer_id', 'inquiry_id', 'loan_id', 'owner_id',
            'disbursement_id', 'closure_id', 'foreclosure_id',
            'renewal_id', 'collateral_id', 'seizure_id',
            'auction_id', 'broker_id'
        ]

        # Check for missing or extra fields
        validation_errors = {}
        for field in required_fields:
            if field not in data:
                validation_errors[field] = ["This field is required"]
            elif not isinstance(data[field], int):
                validation_errors[field] = ["Must be an integer"]

        if validation_errors:
            return JsonResponse({
                "result": False,
                "message": "Validation failed",
                "errors": validation_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate LoanMasters record
        if LoanMasters.objects.filter(
            customer_id=data['customer_id'],
            inquiry_id=data['inquiry_id'],
            loan_id=data['loan_id']
        ).exists():
            return JsonResponse({
                "result": False,
                "message": "A LoanMasters record with these customer, inquiry, and loan IDs already exists"
            }, status=status.HTTP_409_CONFLICT)

        # Get all related objects
        related_objects = {}
        try:
            related_objects['customer'] = Customer.objects.get(CustomerId=data['customer_id'])
            related_objects['inquiry'] = NewInquiry.objects.get(id=data['inquiry_id'])
            related_objects['loan'] = LoanApplication.objects.get(id=data['loan_id'])
            related_objects['owner'] = User.objects.get(id=data['owner_id'])
            related_objects['disbursement'] = Disbursement.objects.get(DisbursementId=data['disbursement_id'])
            related_objects['closure'] = LoanClosure.objects.get(ClosureId=data['closure_id'])
            related_objects['foreclosure'] = LoanForeclosure.objects.get(ForeclosureId=data['foreclosure_id'])
            related_objects['renewal'] = LoanRenewal.objects.get(RenewalId=data['renewal_id'])
            related_objects['collateral'] = Collateral.objects.get(CollateralId=data['collateral_id'])
            related_objects['seizure'] = InitiateSeizure.objects.get(Id=data['seizure_id'])
            related_objects['auction'] = AuctionSetup.objects.get(AuctionId=data['auction_id'])
            related_objects['broker'] = Broker.objects.get(BrokerId=data['broker_id'])
        except ObjectDoesNotExist as e:
            return JsonResponse({
                "result": False,
                "message": f"Related object not found: {str(e)}"
            }, status=status.HTTP_404_NOT_FOUND)

        # Custom JSON encoder to handle dates and other non-serializable objects
        class CustomJSONEncoder(DjangoJSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime.date):
                    return obj.isoformat()
                elif hasattr(obj, 'url'):
                    return obj.url
                return super().default(obj)

        # Prepare custom field data with proper serialization
        custom_field_data = {
            'customer': json.loads(json.dumps(model_to_dict(related_objects['customer']), cls=CustomJSONEncoder)),
            'inquiry': json.loads(json.dumps(model_to_dict(related_objects['inquiry']), cls=CustomJSONEncoder)),
            'loan': json.loads(json.dumps(model_to_dict(related_objects['loan']), cls=CustomJSONEncoder)),
            'disbursement': json.loads(json.dumps(model_to_dict(related_objects['disbursement']), cls=CustomJSONEncoder)),
            'closure': json.loads(json.dumps(model_to_dict(related_objects['closure']), cls=CustomJSONEncoder)),
            'foreclosure': json.loads(json.dumps(model_to_dict(related_objects['foreclosure']), cls=CustomJSONEncoder)),
            'renewal': json.loads(json.dumps(model_to_dict(related_objects['renewal']), cls=CustomJSONEncoder)),
            'collateral': json.loads(json.dumps(model_to_dict(related_objects['collateral']), cls=CustomJSONEncoder)),
            'seizure': json.loads(json.dumps(model_to_dict(related_objects['seizure']), cls=CustomJSONEncoder)),
            'auction': json.loads(json.dumps(model_to_dict(related_objects['auction']), cls=CustomJSONEncoder)),
            'broker': json.loads(json.dumps(model_to_dict(related_objects['broker']), cls=CustomJSONEncoder))
        }

        # Create the LoanMasters record
        loan_master = LoanMasters.objects.create(
            customer_id=related_objects['customer'],
            inquiry_id=related_objects['inquiry'],
            loan_id=related_objects['loan'],
            owner_id=related_objects['owner'],
            disbursement_id=related_objects['disbursement'],
            closure_id=related_objects['closure'],
            foreclosure_id=related_objects['foreclosure'],
            renewal_id=related_objects['renewal'],
            collateral_id=related_objects['collateral'],
            seizure_id=related_objects['seizure'],
            auction_id=related_objects['auction'],
            broker_id=related_objects['broker'],
            CustomField=custom_field_data
        )

        return JsonResponse({
            "result": True,
            "message": "LoanMasters record created successfully",
            "data": {
                "loan_master_id": loan_master.id,
                "custom_field_data": custom_field_data
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse({
            "result": False,
            "message": "Internal server error",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def model_to_dict(instance):
    from django.forms.models import model_to_dict
    data = model_to_dict(instance)
    # Handle file fields and other special cases
    for field in instance._meta.fields:
        if field.get_internal_type() in ['FileField', 'ImageField']:
            file = getattr(instance, field.name)
            if file:
                data[field.name] = file.url
        elif field.get_internal_type() == 'DateTimeField':
            dt = getattr(instance, field.name)
            if dt:
                data[field.name] = dt.isoformat()
    return data

# Helper function to validate foreign key relationships
def validate_foreign_key(model, id_field, id_value):
    try:
        instance = model.objects.get(**{id_field: id_value})
        return {'exists': True, 'instance': instance}
    except ObjectDoesNotExist:
        return {'exists': False, 'error': f"{model.__name__} with {id_field}={id_value} not found"}

# Helper function to serialize model instances
def serialize_model_instance(instance):
    data = {}
    for field in instance._meta.fields:
        field_value = getattr(instance, field.name)
        if field.many_to_one or field.one_to_one:
            data[field.name] = str(field_value.pk) if field_value else None
        elif isinstance(field, models.FileField):
            data[field.name] = field_value.url if field_value else None
        else:
            data[field.name] = field_value
    return data



@api_view(['GET'])
def loan_emi_calculator(request):
    from .emi_calculator import calculate_emi_schedule

    try:
        principal = request.GET.get('principal')
        annual_rate = request.GET.get('annual_rate')
        tenure_months = request.GET.get('tenure_months')
        method = request.GET.get('method')

        emi, schedule = calculate_emi_schedule(principal, annual_rate, tenure_months, method)

        return Response({
            "principal": principal,
            "annual_rate": annual_rate,
            "tenure_months": tenure_months,
            "method": method,
            "emi": emi,
            "schedule": schedule
        }, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def save_emi_schedule(request):
    from .emi_calculator import calculate_emi_schedule
    from django.db import transaction
    from decimal import Decimal

    try:
        data = request.data
        loan_id = data.get("loanId")
        principal = data.get("principal")
        annual_rate = data.get("annual_rate")
        tenure_months = data.get("tenure_months")
        method = data.get("method")

        # Get related loan
        loan = LoanApplication.objects.get(id=loan_id)

        # Calculate EMI & Schedule
        emi, schedule = calculate_emi_schedule(principal, annual_rate, tenure_months, method)

        with transaction.atomic():
            emi_record = LoanEMiCalculator.objects.create(
                loanId=loan,
                principal=Decimal(principal),
                annualRate=Decimal(annual_rate),
                tenureMonths=int(tenure_months),
                method=method,
                emi=Decimal(emi)
            )

            LoanEMiSchedule.objects.bulk_create([
                LoanEMiSchedule(
                    EMiCalculator=emi_record,
                    month=s["month"],
                    emi=s["emi"],
                    interest=s["interest"],
                    principal=s["principal"],
                    remaining_balance=s["remaining_balance"]
                ) for s in schedule
            ])

        return Response({
            "message": "Schedule saved",
            "emi_id": emi_record.id,
            "emi": emi,
            "tenure": tenure_months,
            "loanId": loan_id
        }, status=201)

    except LoanApplication.DoesNotExist:
        return Response({"error": "Loan ID not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


