from rest_framework import serializers
from .models import *
from rest_framework import serializers

class CaseInsensitiveChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            for key in self.choices.keys():
                if key.lower() == data.lower():
                    return key
        self.fail("invalid_choice", input=data)

    def to_representation(self, value):
        return super().to_representation(value)



class DynamicKYCRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=False)
    inquiry_id = serializers.IntegerField(required=False)
    loan_id = serializers.IntegerField(required=False)
    kyc_service = serializers.CharField()
    log_type = CaseInsensitiveChoiceField(choices=KYCLog._meta.get_field('log_type').choices)
    token = serializers.CharField()
    base_url = serializers.URLField()
    endpoint = serializers.CharField()

    # Additional payload fields are allowed dynamically
    aadhaar_number = serializers.CharField(required=False)  # example
    # Add more known fields if needed

    def validate(self, data):
        if not any([data.get("customer_id"), data.get("loan_id"), data.get("inquiry_id")]):
            raise serializers.ValidationError("At least one of customer_id, loan_id, or inquiry_id is required.")
        return data
