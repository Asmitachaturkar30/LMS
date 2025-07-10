# serializers.py
from rest_framework import serializers
from .models import *
from LoginAuth.models import User
from Masters.models import Branch, Department, LoanMasters
from InquiryLoanProcess.models import EMISetup, LoanApplication
class CaseInsensitiveChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            for key in self.choices.keys():
                if key.lower() == data.lower():
                    return key
        self.fail("invalid_choice", input=data)

    def to_representation(self, value):
        return super().to_representation(value)

class DisbursementSerializer(serializers.ModelSerializer):
    ModeOfTransfer = CaseInsensitiveChoiceField(choices=Disbursement.MODE_CHOICES)

    class Meta:
        model = Disbursement
        fields = [
            'DisbursementId', 'OwnerId', 'BranchId', 'DepartmentId', 'Loan',  # Include Loan
            'DisbursementDate', 'DisbursedAmount', 'ModeOfTransfer',
            'BankAccountNumber', 'ChequeNumber', 'Remarks',
            'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'Loan': {'required': True},
            'DisbursementDate': {'allow_null': True},
            'DisbursedAmount': {'allow_null': True},
            'ModeOfTransfer': {'allow_null': True},
            'BankAccountNumber': {'allow_null': True},
            'ChequeNumber': {'allow_null': True},
            'Remarks': {'allow_null': True},
        }

    def validate_disbursed_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Disbursed amount must be greater than zero.")
        return value

    def validate(self, data):
        owner = data.get('OwnerId')
        branch = data.get('BranchId')
        department = data.get('DepartmentId')
        loan = data.get('Loan')

        errors = {}

        if not owner or not User.objects.filter(id=owner.id).exists():
            errors['OwnerId'] = ["User with this ID does not exist."]
        if branch and not Branch.objects.filter(BranchId=branch.BranchId).exists():
            errors['BranchId'] = ["Branch with this ID does not exist."]
        if department and not Department.objects.filter(DepartmentId=department.DepartmentId).exists():
            errors['DepartmentId'] = ["Department with this ID does not exist."]
        if not loan or not LoanApplication.objects.filter(pk=loan.pk).exists():
            errors['Loan'] = ["Loan with this ID does not exist."]
        if loan and Disbursement.objects.filter(Loan=loan).exists():
            errors['Loan'] = ["Disbursement already exists for this Loan ID."]

        if errors:
            raise serializers.ValidationError(errors)

        return data


class RepaymentScheduleSerializer(serializers.ModelSerializer):
    Status = CaseInsensitiveChoiceField(choices=RepaymentSchedule.STATUS_CHOICES)

    class Meta:
        model = RepaymentSchedule
        fields = [
            'ScheduleId', 'OwnerId', 'BranchId', 'DepartmentId',
            'LoanId', 'EMIAmount', 'DueDate', 'Status', 'PaidDate'
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'Loan': {'required': True},
            'EMIAmount': {'allow_null': True},
            'DueDate': {'allow_null': True},
            'Status': {'allow_null': True},
            'PaidDate': {'allow_null': True},
        }

    def validate_EMIAmount(self, value):
        if value <= 0:
            raise serializers.ValidationError("EMI amount must be greater than zero.")
        return value

    def validate(self, data):
        errors = {}

        # Validate foreign key existence
        if not data.get('OwnerId') or not User.objects.filter(id=data['OwnerId'].id).exists():
            errors['OwnerId'] = ["User with this ID does not exist."]

        if not data.get('BranchId') or not Branch.objects.filter(BranchId=data['BranchId'].BranchId).exists():
            errors['BranchId'] = ["Branch with this ID does not exist."]

        if not data.get('DepartmentId') or not Department.objects.filter(DepartmentId=data['DepartmentId'].DepartmentId).exists():
            errors['DepartmentId'] = ["Department with this ID does not exist."]

        if not data.get('LoanId') or not LoanApplication.objects.filter(id=data['LoanId'].id).exists():
            errors['LoanId'] = ["Loan with this ID does not exist."]

        if errors:
            raise serializers.ValidationError(errors)

        return data

class PaymentCollectionSerializer(serializers.ModelSerializer):
    Mode = CaseInsensitiveChoiceField(choices=PaymentCollection.MODE_CHOICES)

    class Meta:
        model = PaymentCollection
        fields = [
            'CollectionId', 'OwnerId', 'BranchId', 'DepartmentId',
            'LoanId', 'EMIId', 'CollectedAmount', 'PaymentDate',
            'Mode', 'ReceivedBy', 'CreateBy', 'UpdateBy',
            'CreatedAt', 'LastUpdatedAt'
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'Loan': {'required': True},
            'EMIId': {'required': True},
            'CollectedAmount': {'allow_null': True},
            'PaymentDate': {'allow_null': True},
            'Mode': {'allow_null': True},
            'ReceivedBy': {'allow_null': True},
        }

    def validate_OwnerId(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("User with this ID does not exist.")
        if self.instance and self.instance.OwnerId != value:
            raise serializers.ValidationError("OwnerId cannot be changed.")
        return value

    def validate_BranchId(self, value):
        if value and not Branch.objects.filter(BranchId=value.BranchId).exists():
            raise serializers.ValidationError("Branch with this ID does not exist.")
        if self.instance and self.instance.BranchId != value:
            raise serializers.ValidationError("BranchId cannot be changed.")
        return value

    def validate_DepartmentId(self, value):
        if value and not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
            raise serializers.ValidationError("Department with this ID does not exist.")
        if self.instance and self.instance.DepartmentId != value:
            raise serializers.ValidationError("DepartmentId cannot be changed.")
        return value

    def validate_LoanId(self, value):
        if not LoanApplication.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Loan with this ID does not exist.")
        if self.instance and self.instance.LoanId != value:
            raise serializers.ValidationError("LoanId cannot be changed.")
        return value

    def validate_EMIId(self, value):
        if not EMISetup.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("EMI with this ID does not exist.")
        if self.instance and self.instance.EMIId != value:
            raise serializers.ValidationError("EMIId cannot be changed.")
        return value



class LoanClosureSerializer(serializers.ModelSerializer):
    ClosureType = CaseInsensitiveChoiceField(choices=LoanClosure.CLOSURE_TYPE_CHOICES)

    class Meta:
        model = LoanClosure
        fields = [
            'ClosureId','OwnerId','BranchId','DepartmentId', 'LoanId', 'ClosureDate', 'ClosureType', 'Reason',
            'FinalPayment', 'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'Loan': {'required': True},
            'ClosureDate': {'allow_null': True},
            'ClosureType': {'allow_null': True},
            'Reason': {'allow_null': True},
            'FinalPayment': {'allow_null': True},
        }

    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not LoanClosure.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not LoanClosure.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not LoanClosure.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value
    def validate_LoanId(self, value):
        if self.instance is None:
            if not LoanApplication.objects.filter(pk=value.pk).exists():
                raise serializers.ValidationError("Loan with this ID does not exist.")
        else:
            if not LoanClosure.objects.filter(pk=self.instance.pk, LoanId=value).exists():
                raise serializers.ValidationError("This LoanId does not belong to the record being updated.")
        return value



class LoanForeclosureSerializer(serializers.ModelSerializer):
    Status = CaseInsensitiveChoiceField(choices=LoanForeclosure.STATUS_CHOICES)
    class Meta:
        model = LoanForeclosure
        fields = [
            'ForeclosureId','OwnerId','BranchId','DepartmentId', 'Loan', 'RequestDate', 'PenaltyAmount',
            'FinalPayment', 'Status', 'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'Loan': {'required': True},
            'RequestDate': {'allow_null': True},
            'PenaltyAmount': {'allow_null': True},
            'FinalPayment': {'allow_null': True},
            'Status': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not LoanForeclosure.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not LoanForeclosure.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not LoanForeclosure.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value

    def validate_LoanId(self, value):
        if self.instance is None:
            if not LoanApplication.objects.filter(LoanId=value.LoanId).exists():
                raise serializers.ValidationError("Loan with this ID does not exist.")
        else:
            if not LoanForeclosure.objects.filter(pk=self.instance.pk, LoanId=value.LoanId).exists():
                raise serializers.ValidationError("This LoanId does not belong to the record being updated.")
        return value



class LoanRenewalSerializer(serializers.ModelSerializer):
    ApprovalStatus = CaseInsensitiveChoiceField(choices=LoanRenewal.APPROVAL_STATUS_CHOICES)

    class Meta:
        model = LoanRenewal
        fields = [
            'RenewalId','OwnerId','BranchId','DepartmentId', 'OldLoanId', 'NewTenure', 'NewInterestRate', 'Reason',
            'ApprovalStatus', 'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'OldLoanId': {'required': True},
            'NewTenure': {'allow_null': True},
            'NewInterestRate': {'allow_null': True},
            'Reason': {'allow_null': True},
            'ApprovalStatus': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not LoanRenewal.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not LoanRenewal.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not LoanRenewal.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value


        
class AutoSquareOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoSquareOffReconciliation
        fields = [
            'AdjustmentId','OwnerId','BranchId','DepartmentId', 'loanId', 'OverpaidAmount', 'UnderpaidAmount',
            'AdjustmentDate', 'Remarks', 'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt'
        ]
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'loanId': {'required': True},
            'OverpaidAmount': {'allow_null': True},
            'UnderpaidAmount': {'allow_null': True},
            'AdjustmentDate': {'allow_null': True},
            'Remarks': {'allow_null': True},
            'CreateBy': {'allow_null': True},
            'UpdateBy': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not AutoSquareOffReconciliation.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not AutoSquareOffReconciliation.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not AutoSquareOffReconciliation.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value

class EMICollectionAdjustmentSerializer(serializers.ModelSerializer):
    Mode = CaseInsensitiveChoiceField(choices=EMICollectionAdjustment.MODE_CHOICES)

    class Meta:
        model = EMICollectionAdjustment
        fields = [
            'PaymentId','OwnerId','BranchId','DepartmentId', 'EMIId', 'PaymentDate', 'AmountPaid', 'Mode',
            'ForwardedEMIId', 'BouncingCharges', 'CreateBy', 'UpdateBy',
            'CreatedAt', 'LastUpdatedAt'
        ]

        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'EMIId': {'required': True},
            'PaymentDate': {'allow_null': True},
            'AmountPaid': {'allow_null': True},
            'Mode': {'allow_null': True},
            'ForwardedEMIId': {'allow_null': True},
            'BouncingCharges': {'allow_null': True},
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

        if errors:
            raise serializers.ValidationError(errors)

        return data