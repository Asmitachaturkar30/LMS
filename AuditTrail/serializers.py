from rest_framework import serializers
from .models import AuditLogs

from LoginAuth.models import User
from Masters.models import Branch, Department
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



class AuditLogsSerializer(serializers.ModelSerializer):
    Module = CaseInsensitiveChoiceField(choices=AuditLogs.AUDIT_MODULE_CHOICES)
    ActionPerformed = CaseInsensitiveChoiceField(choices=AuditLogs.AUDIT_ACTION_CHOICES)

    UserID = serializers.CharField(max_length=150, allow_blank=True, required=False)
    OldValue = serializers.JSONField(required=False, allow_null=True)
    NewValue = serializers.JSONField(required=False, allow_null=True)
    CreateBy = serializers.CharField(max_length=50, allow_blank=True, required=False)  # fixed
    UpdateBy = serializers.CharField(max_length=50, allow_blank=True, required=False)  # fixed
    CreatedAt = serializers.DateTimeField(read_only=True)  # fixed
    LastUpdatedAt = serializers.DateTimeField(read_only=True)  # fixed

    class Meta:
        model = AuditLogs
        fields = [
            'id',
            'OwnerId',
            'BranchId',
            'DepartmentId',
            'Module',
            'ActionPerformed',
            'UserID',
            'OldValue',
            'NewValue',
            'CreateBy',
            'UpdateBy',
            'CreatedAt',
            'LastUpdatedAt',
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'Module': {'allow_null': True},
            'ActionPerformed': {'allow_null': True},
            'UserID': {'allow_null': True},
            'OldValue': {'allow_null': True},
            'NewValue': {'allow_null': True},
        }
    def validate(self, data):
        errors = {}

        initial_data = self.initial_data  # raw input from request

        owner_id = initial_data.get('OwnerId')
        branch_id = initial_data.get('BranchId')
        department_id = initial_data.get('DepartmentId')

        # Foreign Key Existence Checks using raw IDs
        if owner_id and not User.objects.filter(id=owner_id).exists():
            errors['OwnerId'] = "User (OwnerId) not found."

        if branch_id and not Branch.objects.filter(BranchId=branch_id).exists():
            errors['BranchId'] = "Branch not found."

        if department_id and not Department.objects.filter(DepartmentId=department_id).exists():
            errors['DepartmentId'] = "Department not found."

        if errors:
            raise serializers.ValidationError(errors)

        return data
