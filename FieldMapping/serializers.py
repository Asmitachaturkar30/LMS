from rest_framework import serializers
from .models import FieldKeyMapping

class FieldKeyMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldKeyMapping
        fields = ['field_id', 'model_name', 'field_name', 'display_name']
