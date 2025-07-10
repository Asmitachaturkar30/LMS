from rest_framework import serializers
from .models import *
from LoginAuth.models import User
from Masters.models import Branch, Department
from InquiryLoanProcess.models import LoanApplication
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



class AuctionSetupSerializer(serializers.ModelSerializer):
    AuctionType = CaseInsensitiveChoiceField(choices=[
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('broker-mediated', 'Broker-Mediated')
    ])
    class Meta:
        model = AuctionSetup
        fields = [
            'AuctionId', 'LoanId','OwnerId','BranchId','DepartmentId','SeizureOrderCopy', 'AuctionType', 'ReservePrice', 'PlatformUrl',
            'AssetType', 'ValuationReport', 'AssetPhotos', 'InsurancePolicy', 'BidderPanCard',
            'BidderAadhaar', 'EMD_Receipt', 'BidDeclarationForm', 'SaleDeed', 'BuyerKycPackage',
            'PaymentProof', 'HandoverReport', 'RBI_AuctionReport', 'AuditTrailLog', 'TDS_Certificate'
        ]
        extra_kwargs = {
            'SeizureOrderCopy': {'allow_null': True},
            'AuctionType': {'allow_null': True},
            'ReservePrice': {'allow_null': True},
            'PlatformUrl': {'allow_null': True},
            'AssetType': {'allow_null': True},
            'ValuationReport': {'allow_null': True},
            'AssetPhotos': {'allow_null': True},
            'InsurancePolicy': {'allow_null': True},
            'BidderPanCard': {'allow_null': True},
            'BidderAadhaar': {'allow_null': True},
            'EMD_Receipt': {'allow_null': True},
            'BidDeclarationForm': {'allow_null': True},
            'SaleDeed': {'allow_null': True},
            'BuyerKycPackage': {'allow_null': True},
            'PaymentProof': {'allow_null': True},
            'HandoverReport': {'allow_null': True},
            'RBI_AuctionReport': {'allow_null': True},
            'AuditTrailLog': {'allow_null': True},
            'TDS_Certificate': {'allow_null': True},
            # keep IDs required
            'LoanId': {'required': True},
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
        }

    def validate(self, data):
        errors = {}

        # Handle AuctionType conditional logic
        auction_type = data.get('AuctionType')
        platform_url = data.get('PlatformUrl')

        if auction_type and auction_type.lower() == 'online' and not platform_url:
            errors['PlatformUrl'] = "This field is required when AuctionType is 'Online'."

        # Get raw input data for IDs
        initial_data = self.initial_data

        owner_id = initial_data.get('OwnerId')
        branch_id = initial_data.get('BranchId')
        department_id = initial_data.get('DepartmentId')
        loan_id = initial_data.get('LoanId')

        if owner_id and not User.objects.filter(id=owner_id).exists():
            errors['OwnerId'] = "User (OwnerId) not found."

        if branch_id and not Branch.objects.filter(BranchId=branch_id).exists():
            errors['BranchId'] = "Branch not found."

        if department_id and not Department.objects.filter(DepartmentId=department_id).exists():
            errors['DepartmentId'] = "Department not found."

        if loan_id and not LoanApplication.objects.filter(id=loan_id).exists():
            errors['LoanId'] = "Loan not found."

        if errors:
            raise serializers.ValidationError(errors)

        return data