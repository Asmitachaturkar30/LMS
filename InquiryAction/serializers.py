from rest_framework import serializers
from .models import *
from LoginAuth.models import User
from Masters.models import Branch, Department, Customer
from InquiryLoanProcess.models import LoanApplication,NewInquiry
from django.contrib.auth import get_user_model



class CaseInsensitiveChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            for key in self.choices.keys():
                if key.lower() == data.lower():
                    return key
        self.fail("invalid_choice", input=data)

    def to_representation(self, value):
        return super().to_representation(value)




class FollowUpSerializer(serializers.ModelSerializer):
    Type = CaseInsensitiveChoiceField(choices=FollowUp.TYPE_CHOICES)

    class Meta:
        model = FollowUp
        fields = [
            'id', 'InquiryId','OwnerId','BranchId','DepartmentId','LoanId','CustomerId', 'Name', 'Date', 'Time', 'Type',
            'Subject', 'Description', 'AssignedTo',
            'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        read_only_fields = ['id', 'Date', 'Time', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'InquiryId': {'required': True},
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'LoanId': {'required': True},
            'CustomerId': {'required': True,},
            'Name': {'allow_null': True},
            'Type': {'allow_null': True},
            'Subject': {'allow_null': True},
            'Description': {'allow_null': True},
            'AssignedTo': {'allow_null': True},
            'CreateBy': {'allow_null': True},
            'UpdateBy': {'allow_null': True},
        }

    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not FollowUp.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not FollowUp.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not FollowUp.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value
    
    def validate_LoanId(self, value):
        if value is not None:
            if self.instance is None:
                if not LoanApplication.objects.filter(pk=value.pk).exists():
                    raise serializers.ValidationError("Loan with this ID does not exist.")
            else:
                if not FollowUp.objects.filter(pk=self.instance.pk, LoanId=value).exists():
                    raise serializers.ValidationError("This LoanId does not belong to the record being updated.")
        return value


    def validate_InquiryId(self, value):
        if value is not None:  # Only validate if InquiryId is provided
            if self.instance is None:  # Creating new record
                if not NewInquiry.objects.filter(pk=value.pk).exists():
                    raise serializers.ValidationError("Inquiry with this ID does not exist.")
            else:  # Updating existing record
                if not FollowUp.objects.filter(pk=self.instance.pk, InquiryId=value).exists():
                    raise serializers.ValidationError("This InquiryId does not belong to the record being updated.")
        return value

    def validate_CustomerId(self, value):
        if value is not None:
            if self.instance is None:  # Create
                if not Customer.objects.filter(pk=value.pk).exists():
                    raise serializers.ValidationError("Customer with this ID does not exist.")
            else:  # Update
                if not FollowUp.objects.filter(pk=self.instance.pk, CustomerId=value).exists():
                    raise serializers.ValidationError("This CustomerId does not belong to the record being updated.")
        return value




class InquiryActionSerializer(serializers.ModelSerializer):
    Action = CaseInsensitiveChoiceField(choices=inquiryAction.ACTION_CHOICES)

    class Meta:
        model = inquiryAction
        fields = [
            'id', 'Action','OwnerId','BranchId','DepartmentId', 'InquiryId', 'CreateBy',
            'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        read_only_fields = ['id', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'InquiryId': {'required': True},
            'Action': {'allow_null': True},
        }


User = get_user_model()

class AssignSerializer(serializers.ModelSerializer):
    Users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Assign
        fields = [
            'id', 'BranchId', 'DepartmentId', 'InquiryId', 'Users',
            'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        read_only_fields = ['id', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'InquiryId': {'required': True},
            'Users': {'required': True},
        }
    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Assign.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Assign.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value


class InquiryNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryNote
        fields = [
            'id', 'InquiryId','OwnerId', 'Description', 'AssignedTo',
            'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        read_only_fields = ['id', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'InquiryId': {'required': True},
            'OwnerId': {'required': True},
            'Description': {'allow_null': True},
            'AssignedTo': {'allow_null': True}
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not InquiryNote.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value



class SpecialNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialNote
        fields = [
            'id', 'InquiryId','OwnerId', 'Description', 'AssignedTo',
            'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        read_only_fields = ['id', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'InquiryId': {'required': True},
            'OwnerId': {'required': True},
            'Description': {'allow_null': True},
            'AssignedTo': {'allow_null': True}
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not SpecialNote.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value


class VerificationSerializer(serializers.ModelSerializer):
    VerificationMode = CaseInsensitiveChoiceField(choices=Verification.VERIFICATION_MODE_CHOICES)
    VerificationStatus = CaseInsensitiveChoiceField(choices=Verification.STATUS_CHOICES)

    class Meta:
        model = Verification
        fields = [
            'id', 'InquiryId','OwnerId', 'VerificationMode', 'AssignTo',
            'Remark', 'VerificationStatus', 'VerificationDate',
            'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        read_only_fields = ['id', 'VerificationDate', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'InquiryId': {'required': True},
            'OwnerId': {'required': True},
            'VerificationMode': {'allow_null': True},
            'AssignTo': {'allow_null': True},
            'Remark': {'allow_null': True},
            'VerificationStatus': {'allow_null': True}
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not Verification.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value





# serializers.py
from rest_framework import serializers
from .models import DocumentUpload, DocumentFile
from Masters.models import *
from InquiryLoanProcess.models import *

class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ['id', 'file', 'original_filename', 'file_size', 'file_type', 'created_at']
        read_only_fields = ['id', 'original_filename', 'file_size', 'file_type', 'created_at']

class DocumentUploadSerializer(serializers.ModelSerializer):
    files = DocumentFileSerializer(many=True, read_only=True)
    multiDocs = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = DocumentUpload
        fields = ['id', 'CustomerId', 'LoanId', 'InquiryId', 'Worker',
                 'files', 'multiDocs', 'created_at', 'updated_at']
        read_only_fields = ['id', 'files', 'created_at', 'updated_at']

    def validate_LoanId(self, value):
        if value is not None:
            if self.instance is None:
                if not LoanApplication.objects.filter(pk=value.pk).exists():
                    raise serializers.ValidationError("Loan with this ID does not exist.")
            else:
                if not DocumentUpload.objects.filter(pk=self.instance.pk, LoanId=value).exists():
                    raise serializers.ValidationError("This LoanId does not belong to the record being updated.")
        return value

    def validate_InquiryId(self, value):
        if value is not None:
            if self.instance is None:
                if not NewInquiry.objects.filter(pk=value.pk).exists():
                    raise serializers.ValidationError("Inquiry with this ID does not exist.")
            else:
                if not DocumentUpload.objects.filter(pk=self.instance.pk, InquiryId=value).exists():
                    raise serializers.ValidationError("This InquiryId does not belong to the record being updated.")
        return value

    def validate_CustomerId(self, value):
        if value is not None:
            if self.instance is None:
                if not Customer.objects.filter(pk=value.pk).exists():
                    raise serializers.ValidationError("Customer with this ID does not exist.")
            else:
                if not DocumentUpload.objects.filter(pk=self.instance.pk, CustomerId=value).exists():
                    raise serializers.ValidationError("This CustomerId does not belong to the record being updated.")
        return value

    def validate_multiDocs(self, files):
        if files:
            # Validate file types
            allowed_types = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'txt']
            for file in files:
                # Check file extension
                file_extension = file.name.split('.')[-1].lower()
                if file_extension not in allowed_types:
                    raise serializers.ValidationError(f"File type '{file_extension}' not allowed. Allowed types: {allowed_types}")
        return files

    def create(self, validated_data):
        files = validated_data.pop('multiDocs', [])
        
        # Create the main document upload record
        document_upload = DocumentUpload.objects.create(**validated_data)
        
        # Create file records for each uploaded file
        for file in files:
            DocumentFile.objects.create(
                document_upload=document_upload,
                file=file,
                original_filename=file.name,
                file_size=file.size,
                file_type=file.name.split('.')[-1].lower()
            )
        
        return document_upload
