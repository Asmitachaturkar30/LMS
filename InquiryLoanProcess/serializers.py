from rest_framework import serializers
from .models import *
# from .utils import base64_to_file
import re
from .validation import loan_application_FIELD_DEFINITIONS
from datetime import datetime, date
from django.core.exceptions import ValidationError
from .models import *
from LoginAuth.models import User
from Masters.models import Branch, Department, Customer
from InquiryLoanProcess.models import LoanApplication

class CaseInsensitiveChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            for key in self.choices.keys():
                if key.lower() == data.lower():
                    return key
        self.fail("invalid_choice", input=data)

    def to_representation(self, value):
        return super().to_representation(value)


class InquiryModelSerializer(serializers.ModelSerializer):
    Gender = CaseInsensitiveChoiceField(choices=NewInquiry.GENDER_CHOICES)
    InquiryStatus = CaseInsensitiveChoiceField(choices=NewInquiry.INQUIRY_STATUS_CHOICES)

    class Meta:
        model = NewInquiry
        fields = '__all__'
        extra_kwargs = {
            # Keep these ForeignKeys required
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},

            # Make everything else optional
            'Date': {'allow_null': True},
            'FirstName': {'required': True, 'allow_null': True},
            'MiddleName': {'allow_null': True},
            'LastName': {'required': True, 'allow_null': True},
            'Gender': {'allow_null': True},
            'MaritalStatus': {'allow_null': True},
            'DateOfBirth': {'allow_null': True},
            'PhoneNumber': {'allow_null': True},
            'AlternatePhoneNumber': {'allow_null': True},
            'EmailAddress': {'allow_null': True},
            'FathersMothersName': {'allow_null': True},
            'PANNumber': {'allow_null': True},
            'AadhaarNumber': {'allow_null': True},
            'AddressLine1': {'allow_null': True},
            'AddressLine2': {'allow_null': True},
            'City': {'allow_null': True},
            'State': {'allow_null': True},
            'Pincode': {'allow_null': True},
            'Country': {'allow_null': True},
            'Landmark': {'allow_null': True},
            'AddressType': {'allow_null': True},
            'DurationAtAddress': {'allow_null': True},
            'LoanPurpose': {'allow_null': True},
            'LoanAmountRequested': {'allow_null': True},
            'Source': {'allow_null': True},
            'FollowUpNotes': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not NewInquiry.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not NewInquiry.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not NewInquiry.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value


class LoanApplicationSerializer(serializers.Serializer):
    Gender = CaseInsensitiveChoiceField(choices=NewInquiry.GENDER_CHOICES)
    EmploymentType = CaseInsensitiveChoiceField(choices=[('salaried', 'Salaried'), ('self-employed', 'Self-employed')])
    AccountType = CaseInsensitiveChoiceField(choices=LoanApplication.ACCOUNT_TYPE_CHOICES)
    Frequency = CaseInsensitiveChoiceField(choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ])
    RepaymentMode = CaseInsensitiveChoiceField(choices=[('ecs', 'ECS'), ('online', 'Online'), ('cash', 'Cash')])
    DisbursementType = CaseInsensitiveChoiceField(choices=LoanApplication.DISBURSEMENT_TYPE_CHOICES, allow_null=True)
    DisbursementMode = CaseInsensitiveChoiceField(choices=LoanApplication.DISBURSEMENT_MODE_CHOICES, allow_null=True)
    DisbursementStatus = CaseInsensitiveChoiceField(choices=LoanApplication.DISBURSEMENT_STATUS_CHOICES, allow_null=True)
    module = serializers.CharField()
    section = serializers.CharField()
    form_data = serializers.JSONField()
    createBy = serializers.CharField()
    updateBy = serializers.CharField()
    extra_kwargs = {
            # Keep IDs required
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'ProductId': {'required': True},
            'InquiryId': {'required': True},
            
            # Make rest optional
            'FirstName': {'allow_null': True},
            'MiddleName': {'allow_null': True},
            'LastName': {'allow_null': True},
            'MaritalStatus': {'allow_null': True},
            'DateOfBirth': {'allow_null': True},
            'PhoneNumber': {'allow_null': True},
            'AlternatePhoneNumber': {'allow_null': True},
            'EmailAddress': {'allow_null': True},
            'FathersMothersName': {'allow_null': True},
            'AddressLine1': {'allow_null': True},
            'AddressLine2': {'allow_null': True},
            'City': {'allow_null': True},
            'State': {'allow_null': True},
            'Pincode': {'allow_null': True},
            'Country': {'allow_null': True},
            'Landmark': {'allow_null': True},
            'AddressType': {'allow_null': True},
            'DurationAtAddress': {'allow_null': True},
            'Occupation': {'allow_null': True},
            'CompanyName': {'allow_null': True},
            'IndustryType': {'allow_null': True},
            'WorkExperience': {'allow_null': True},
            'EmployerDuration': {'allow_null': True},
            'OfficeAddress': {'allow_null': True},
            'OfficePhoneNumber': {'allow_null': True},
            'MonthlyIncome': {'allow_null': True},
            'AnnualIncome': {'allow_null': True},
            'BankName': {'allow_null': True},
            'BranchName': {'allow_null': True},
            'AccountNumber': {'allow_null': True},
            'IFSC_Code': {'allow_null': True},
            'LoanAmount': {'allow_null': True},
            'RateOfInterest': {'allow_null': True},
            'LoanTenure': {'allow_null': True},
            'CoApplicant': {'allow_null': True},
            'GuarantorRequired': {'allow_null': True},
            'GuarantorName': {'allow_null': True},
            'GuarantorMobile': {'allow_null': True},
            'GuarantorEmail': {'allow_null': True},
            'GuarantorAddress': {'allow_null': True},
            'GuarantorPANNumber': {'allow_null': True},
            'GuarantorAadhaarNumber': {'allow_null': True},
            'GuarantorPANCardCopy': {'allow_null': True},
            'GuarantorAadhaarCardCopy': {'allow_null': True},
            'GuarantorBankStatement': {'allow_null': True},
            'ExistingLoans': {'allow_null': True},
            'EMI_AmountExisting': {'allow_null': True},
            'DisbursementDate': {'allow_null': True},
            'DisbursementNotes': {'allow_null': True},
            'MoreAttachmentFile': {'allow_null': True},
        }
    def validate(self, data):
        section = data.get("section")
        form_data = data.get("form_data", {})
        errors = {}

        # Only validate fields related to the given section
        section_fields = loan_application_FIELD_DEFINITIONS.get(section, {})

        for field_name, rules in section_fields.items():
            # Required field validation
            if rules.get("required") and not form_data.get(field_name):
                errors[field_name] = "This field is required"

            # Conditional requirement
            if "required_if" in rules:
                condition = rules["required_if"]
                cond_key, cond_val = next(iter(condition.items()))
                if form_data.get(cond_key) == cond_val and not form_data.get(field_name):
                    errors[field_name] = f"Required when {cond_key} is {cond_val}"

        if errors:
            raise serializers.ValidationError({"form_data": errors})

        # Auto-calculate Annual Income only for Employment section
        if section == "Employment Details" and "Monthly Income" in form_data:
            try:
                monthly_income = float(form_data["Monthly Income"])
                data["form_data"]["Annual Income"] = round(monthly_income * 12, 2)
            except Exception:
                pass

        return data

    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not LoanApplication.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not LoanApplication.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not LoanApplication.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value

    def validate_InquiryId(self, value):
        if value is not None:  # Only validate if InquiryId is provided
            if self.instance is None:  # Creating new record
                if not NewInquiry.objects.filter(pk=value.pk).exists():
                    raise serializers.ValidationError("Inquiry with this ID does not exist.")
            else:  # Updating existing record
                if not LoanApplication.objects.filter(pk=self.instance.pk, InquiryId=value).exists():
                    raise serializers.ValidationError("This InquiryId does not belong to the record being updated.")
        return value


    
class LoanApplicationModelSerializer(serializers.ModelSerializer):
    Gender = CaseInsensitiveChoiceField(choices=NewInquiry.GENDER_CHOICES)
    EmploymentType = CaseInsensitiveChoiceField(choices=[('salaried', 'Salaried'), ('self-employed', 'Self-employed')])
    AccountType = CaseInsensitiveChoiceField(choices=LoanApplication.ACCOUNT_TYPE_CHOICES)
    Frequency = CaseInsensitiveChoiceField(choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')])
    RepaymentMode = CaseInsensitiveChoiceField(choices=[('ecs', 'ECS'), ('online', 'Online'), ('cash', 'Cash')])
    ApplicationStatus = CaseInsensitiveChoiceField(choices=LoanApplication.APPLICATION_STATUS_CHOICES)
    LoanStatus = CaseInsensitiveChoiceField(choices=LoanApplication.LOAN_STATUS_CHOICES)
    DisbursementType = CaseInsensitiveChoiceField(choices=LoanApplication.DISBURSEMENT_TYPE_CHOICES, allow_null=True)
    DisbursementMode = CaseInsensitiveChoiceField(choices=LoanApplication.DISBURSEMENT_MODE_CHOICES, allow_null=True)
    DisbursementStatus = CaseInsensitiveChoiceField(choices=LoanApplication.DISBURSEMENT_STATUS_CHOICES, allow_null=True)

    class Meta:
        model = LoanApplication
        fields = '__all__'
        extra_kwargs = {
            # Keep IDs required
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'ProductId': {'required': True},
            'InquiryId': {'required': True},
            
            # Make rest optional
            'FirstName': {'allow_null': True},
            'MiddleName': {'allow_null': True},
            'LastName': {'allow_null': True},
            'MaritalStatus': {'allow_null': True},
            'DateOfBirth': {'allow_null': True},
            'PhoneNumber': {'allow_null': True},
            'AlternatePhoneNumber': {'allow_null': True},
            'EmailAddress': {'allow_null': True},
            'FathersMothersName': {'allow_null': True},
            'AddressLine1': {'allow_null': True},
            'AddressLine2': {'allow_null': True},
            'City': {'allow_null': True},
            'State': {'allow_null': True},
            'Pincode': {'allow_null': True},
            'Country': {'allow_null': True},
            'Landmark': {'allow_null': True},
            'AddressType': {'allow_null': True},
            'DurationAtAddress': {'allow_null': True},
            'Occupation': {'allow_null': True},
            'CompanyName': {'allow_null': True},
            'IndustryType': {'allow_null': True},
            'WorkExperience': {'allow_null': True},
            'EmployerDuration': {'allow_null': True},
            'OfficeAddress': {'allow_null': True},
            'OfficePhoneNumber': {'allow_null': True},
            'MonthlyIncome': {'allow_null': True},
            'AnnualIncome': {'allow_null': True},
            'BankName': {'allow_null': True},
            'BranchName': {'allow_null': True},
            'AccountNumber': {'allow_null': True},
            'IFSC_Code': {'allow_null': True},
            'LoanAmount': {'allow_null': True},
            'RateOfInterest': {'allow_null': True},
            'LoanTenure': {'allow_null': True},
            'CoApplicant': {'allow_null': True},
            'GuarantorRequired': {'allow_null': True},
            'GuarantorName': {'allow_null': True},
            'GuarantorMobile': {'allow_null': True},
            'GuarantorEmail': {'allow_null': True},
            'GuarantorAddress': {'allow_null': True},
            'GuarantorPANNumber': {'allow_null': True},
            'GuarantorAadhaarNumber': {'allow_null': True},
            'GuarantorPANCardCopy': {'allow_null': True},
            'GuarantorAadhaarCardCopy': {'allow_null': True},
            'GuarantorBankStatement': {'allow_null': True},
            'ExistingLoans': {'allow_null': True},
            'EMI_AmountExisting': {'allow_null': True},
            'DisbursementDate': {'allow_null': True},
            'DisbursementNotes': {'allow_null': True},
            'MoreAttachmentFile': {'allow_null': True},
        }
    def validate(self, data):
        # Run model clean validations
        instance = LoanApplication(**data)
        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data


class LoanApplicationAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplicationAttachment
        fields = ['id', 'Loan', 'File']


class FullKYCSerializer(serializers.ModelSerializer):
    KYCStatus = CaseInsensitiveChoiceField(choices=Full_KYC.KYC_STATUS_CHOICES, allow_null=True)

    # Required fields (set explicitly)
    PANCard = serializers.FileField(allow_null=True)
    AadhaarCard = serializers.FileField(allow_null=True)
    BankStatement = serializers.FileField(allow_null=True)

    # Optional supporting documents
    SalarySlips = serializers.FileField(allow_null=True)
    ItrDocs = serializers.FileField(allow_null=True)
    OtherIncomeProof = serializers.FileField(allow_null=True)
    DrivingLicense = serializers.FileField(allow_null=True)
    VoterId = serializers.FileField(allow_null=True)
    ElectricityBill = serializers.FileField(allow_null=True)
    ITRCompliance = serializers.FileField(allow_null=True)
    ReportCibil = serializers.FileField(allow_null=True)
    Digilocker = serializers.FileField(allow_null=True)

    # Status fields (optional for partial updates)
    PANStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    AadhaarStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    SalarySlipsStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    BankStatementStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    ItrDocsStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    OtherIncomeProofStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    DrivingLicenseStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    VoterIdStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    ElectricityBillStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    ITRComplianceStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    ReportCibilStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)
    DigilockerStatus = CaseInsensitiveChoiceField(choices=Full_KYC.DOCUMENT_STATUS_CHOICES, allow_null=True)

    class Meta:
        model = Full_KYC
        fields = [
            'id',
            'OwnerId',
            'BranchId',
            'DepartmentId',
            'PANCard',
            'AadhaarCard',
            'SalarySlips',
            'BankStatement',
            'ItrDocs',
            'OtherIncomeProof',
            'DrivingLicense',
            'VoterId',
            'ElectricityBill',
            'ITRCompliance',
            'ReportCibil',
            'Digilocker',
            'PANStatus',
            'AadhaarStatus',
            'SalarySlipsStatus',
            'BankStatementStatus',
            'ItrDocsStatus',
            'OtherIncomeProofStatus',
            'DrivingLicenseStatus',
            'VoterIdStatus',
            'ElectricityBillStatus',
            'ITRComplianceStatus',
            'ReportCibilStatus',
            'DigilockerStatus',
            'KYCStatus',
            'CreateBy',
            'UpdateBy',
            'Created_at',
            'Updated_at',
        ]
        read_only_fields = ['id', 'Created_at', 'Updated_at']
        extra_kwargs = {
            'OwnerId':{'required':True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'CreateBy': {'required': False},
            'UpdateBy': {'required': False},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not Full_KYC.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Full_KYC.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Full_KYC.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value


class ApprovalSerializer(serializers.ModelSerializer):
    ApprovalStatus = CaseInsensitiveChoiceField(choices=ApprovalInfo._meta.get_field('ApprovalStatus').choices,allow_null=True)

    class Meta:
        model = ApprovalInfo
        fields = [
            'id',
            'OwnerId',
            'BranchId',
            'DepartmentId',
            'ApprovedAmount',
            'ApprovalStatus',
            'ApprovalRemarks',
            'CreateBy',
            'UpdateBy',
            'CreatedAt',
            'LastUpdatedAt',
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'ApprovedAmount': {'allow_null': True},
            'ApprovalRemarks': {'allow_null': True},
            'CreateBy': {'allow_null': True},
            'UpdateBy': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not ApprovalInfo.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not ApprovalInfo.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not ApprovalInfo.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value


class ApprovalStatusUpdateSerializer(serializers.ModelSerializer):
    ApprovalStatus = CaseInsensitiveChoiceField(
        choices=ApprovalInfo._meta.get_field('ApprovalStatus').choices,
        allow_null=True
    )

    class Meta:
        model = ApprovalInfo
        fields = ['ApprovalStatus', 'ApprovalRemarks']



class DisbursementInfoSerializer(serializers.ModelSerializer):
    DisbursementType = CaseInsensitiveChoiceField(
        choices=DisbursementInfo._meta.get_field('DisbursementType').choices,allow_blank=True,allow_null=True
    )
    DisbursementMode = CaseInsensitiveChoiceField(
        choices=DisbursementInfo._meta.get_field('DisbursementMode').choices,allow_blank=True,allow_null=True
    )
    DisbursementStatus = CaseInsensitiveChoiceField(
        choices=DisbursementInfo._meta.get_field('DisbursementStatus').choices,allow_blank=True,allow_null=True
    )
    class Meta:
        model = DisbursementInfo
        fields = [
            'id',
            'OwnerId',
            'BranchId',
            'DepartmentId',
            'DisbursementType',
            'DisbursementMode',
            'DisbursementDate',
            'DisbursementStatus',
            'Notes',
            'CreateBy',
            'UpdateBy', 
            'CreatedAt',
            'LastUpdatedAt',
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'DisbursementDate': {'allow_null': True},
            'Notes': {'allow_null': True},
            'CreateBy': {'allow_null': True},
            'UpdateBy': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not DisbursementInfo.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not DisbursementInfo.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not DisbursementInfo.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value


class EMISetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMISetup
        fields = [
            'id',
            'OwnerId',
            'BranchId',
            'DepartmentId',
            'LoanId',
            'EMI_Amount',
            'StartDate',
            'TotalTenure',
            'RemainingEMIS',
            'PaidEMIS',
            'AutoDebitEnabled',
            'CreateBy',
            'UpdateBy',
            'CreatedAt',
            'LastUpdatedAt',
        ]
        read_only_fields = ['id', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'LoanId': {'required': True},

            # Optional fields that can accept null or be skipped
            'EMI_Amount': {'allow_null': True},
            'StartDate': {'allow_null': True},
            'TotalTenure': {'allow_null': True},
            'RemainingEMIS': {'allow_null': True},
            'PaidEMIS': {'allow_null': True},
            'AutoDebitEnabled': {'allow_null': True},
            'CreateBy': {'allow_null': True},
            'UpdateBy': {'allow_null': True},
        }
    def validate(self, data):
        errors = {}

        # Validate Foreign Keys
        if not User.objects.filter(id=data.get('OwnerId').id).exists():
            errors['OwnerId'] = ["User with this ID does not exist."]
        if not Branch.objects.filter(BranchId=data.get('BranchId').BranchId).exists():
            errors['BranchId'] = ["Branch with this ID does not exist."]
        if not Department.objects.filter(DepartmentId=data.get('DepartmentId').DepartmentId).exists():
            errors['DepartmentId'] = ["Department with this ID does not exist."]

        if not LoanApplication.objects.filter(pk=data.get('LoanId').id).exists():
            errors['LoanId'] = ["LoanId with this ID does not exist."]

        if errors:
            raise serializers.ValidationError(errors)

        return data


class PenaltySerializer(serializers.ModelSerializer):
    PenaltyStatus = CaseInsensitiveChoiceField(
        choices=Penalty._meta.get_field('PenaltyStatus').choices,
        
        allow_blank=True
    )

    class Meta:
        model = Penalty
        fields = [
            'id',
            'OwnerId',
            'BranchId',
            'DepartmentId',
            'BouncedCharges',
            'LatePaymentPenalty',
            'PenaltyStatus',
            'CreateBy',
            'UpdateBy',
            'CreatedAt',
            'LastUpdatedAt',
        ]
        read_only_fields = ['id', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'BouncedCharges': {'allow_null': True},
            'LatePaymentPenalty': {'allow_null': True},
            'CreateBy': {'allow_blank': True, 'allow_null': True},
            'UpdateBy': {'allow_blank': True, 'allow_null': True},
        }

    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not Penalty.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Penalty.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Penalty.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value


class ForeclosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foreclosure
        fields = [
            'id',
            'OwnerId',
            'BranchId',
            'DepartmentId',
            'Requested',
            'Penalty',
            'Status',
            'CreateBy',
            'UpdateBy',
            'CreatedAt',
            'LastUpdatedAt',
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'Requested': {'allow_null': True},
            'Penalty': {'allow_null': True},
            'Status': {'allow_null': True},
            'CreateBy': {'allow_null': True},
            'UpdateBy': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not Foreclosure.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Foreclosure.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Foreclosure.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value
