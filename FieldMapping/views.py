from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import FieldKeyMapping
from .serializers import FieldKeyMappingSerializer
from .utils import field_exists_in_model

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getFieldMappings(request):
    model_name = request.GET.get('model_name')

    if not model_name:
        return Response({"error": "model_name is required"}, status=status.HTTP_400_BAD_REQUEST)

    mappings = FieldKeyMapping.objects.filter(model_name=model_name)
    serializer = FieldKeyMappingSerializer(mappings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def updateFieldLabel(request):
    model_name = request.data.get('model_name')
    field_name = request.data.get('field_name')
    display_name = request.data.get('display_name')

    if not (model_name and field_name and display_name):
        return Response(
            {"error": "model_name, field_name, and display_name are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not field_exists_in_model(model_name, field_name):
        return Response(
            {"error": f"Invalid field: '{field_name}' does not exist in model '{model_name}'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        mapping, created = FieldKeyMapping.objects.update_or_create(
            model_name=model_name,
            field_name=field_name,
            defaults={'display_name': display_name}
        )
        serializer = FieldKeyMappingSerializer(mapping)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def deleteFieldLabel(request):
#     model_name = request.data.get('model_name')
#     field_name = request.data.get('field_name')

#     if not (model_name and field_name):
#         return Response(
#             {"error": "model_name and field_name are required"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     try:
#         mapping = FieldKeyMapping.objects.get(model_name=model_name, field_name=field_name)
#         mapping.delete()
#         return Response({"status": "Deleted successfully"}, status=status.HTTP_200_OK)
#     except FieldKeyMapping.DoesNotExist:
#         return Response(
#             {"error": "Mapping not found"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     except Exception as e:
#         return Response(
#             {"error": f"Internal Server Error: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
