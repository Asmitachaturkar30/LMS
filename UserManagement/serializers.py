from rest_framework import serializers
from .models import UserManagement
from Masters.models import Branch, Department, Designation

class CaseInsensitiveChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            for key in self.choices.keys():
                if key.lower() == data.lower():
                    return key
        self.fail("invalid_choice", input=data)

    def to_representation(self, value):
        return super().to_representation(value)



class CustomPKRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            msg = f"{self.label or self.field_name.capitalize()} with ID {data} not found."
            raise serializers.ValidationError(msg)

class UserManagementSerializer(serializers.ModelSerializer):
    Department = CustomPKRelatedField(queryset=Department.objects.all(), label="Department")
    Branch = CustomPKRelatedField(queryset=Branch.objects.all(), label="Branch")
    Designation = CustomPKRelatedField(queryset=Designation.objects.all(), label="Designation")
    Status = CaseInsensitiveChoiceField(
        choices=UserManagement._meta.get_field('Status').choices
    )
    Name = serializers.CharField(source='Username.username', read_only=True)
    Email = serializers.CharField(source='Username.email', read_only=True)

    class Meta:
        model = UserManagement
        fields = [
            'id',
            'Username',
            'Name',
            'Email',
            'MobileNumber',
            'Branch',
            'Department',
            'Designation',
            'Role',
            'ReportingManager',
            'Password',
            'CreateBy',
            'UpdateBy',
            'CreatedAt',
            'LastUpdatedAt',
            'Status',
        ]
        extra_kwargs = {
            'Password': {'write_only': True},
            'CreateBy': {'required': False},
            'UpdateBy': {'required': False},
            'CreatedAt': {'read_only': True},
            'LastUpdatedAt': {'read_only': True},
        }

    def create(self, validated_data):
        user = UserManagement.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
