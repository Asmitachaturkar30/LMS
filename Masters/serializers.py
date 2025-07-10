from rest_framework import serializers
from .models import *
from datetime import date
from django.db import transaction
from InquiryLoanProcess.models import NewInquiry
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



class SourceSerializer(serializers.ModelSerializer):
    Name = serializers.CharField(max_length=150)
    Code = serializers.CharField(max_length=50)
    CreateBy = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    UpdateBy = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Source
        fields = ['OwnerId','SourceId', 'BranchId','DepartmentId','Name', 'Code', 'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt']
        read_only_fields = ['SourceId', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'Name': {'allow_null':True},
            'code':{'allow_null':True}
        }
    def to_internal_value(self, data):
        """Encrypt data before validation"""
        data = super().to_internal_value(data)
        
        # Encrypt sensitive fields
        if 'Name' in data:
            data['Name'] = DataEncryptor.encrypt_data(data['Name'])
        if 'Code' in data:
            data['Code'] = DataEncryptor.encrypt_data(data['Code'])
            
        return data

    def to_representation(self, instance):
        """Decrypt data before sending response"""
        data = super().to_representation(instance)
        
        try: 
            data['Name'] = DataEncryptor.decrypt_data(instance.Name)
            data['Code'] = DataEncryptor.decrypt_data(instance.Code)
        except Exception as e:
            # Log error but don't fail the request
            pass
            
        return data

    def validate(self, data):
        errors = {}

        owner_id = data.get('OwnerId')
        branch_id = data.get('BranchId')
        department_id = data.get('DepartmentId')

        if owner_id and not User.objects.filter(id=owner_id.id if hasattr(owner_id, 'id') else owner_id).exists():
            errors['OwnerId'] = ["User with this ID does not exist."]

        if branch_id and not Branch.objects.filter(BranchId=branch_id.BranchId if hasattr(branch_id, 'BranchId') else branch_id).exists():
            errors['BranchId'] = ["Branch with this ID does not exist."]

        if department_id and not Department.objects.filter(DepartmentId=department_id.DepartmentId if hasattr(department_id, 'DepartmentId') else department_id).exists():
            errors['DepartmentId'] = ["Department with this ID does not exist."]

        if errors:
            raise serializers.ValidationError(errors)

        return data

#------------------------------------------------------------------------------
class RatingSerializer(serializers.ModelSerializer):
    Name = serializers.CharField(max_length=150,allow_blank=True)
    Code = serializers.CharField(max_length=50,allow_blank=True)
    CreateBy = serializers.CharField(max_length=50, required=False, allow_blank=True)
    UpdateBy = serializers.CharField(max_length=50, required=False, allow_blank=True)

    class Meta:
        model = Rating
        fields = ['OwnerId','RateId','BranchId','DepartmentId','Name', 'Code', 'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt']
        read_only_fields = ['RateId', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'BranchId': {'required': False},
            'DepartmentId': {'required': False},
            'Name':{'allow_blank':True},
            'Code':{'allow_blank':True},
        }
    def validate(self, data):
        errors = {}

        owner_id = data.get('OwnerId')
        branch_id = data.get('BranchId')
        department_id = data.get('DepartmentId')

        if owner_id and not User.objects.filter(id=owner_id.id if hasattr(owner_id, 'id') else owner_id).exists():
            errors['OwnerId'] = ["User with this ID does not exist."]

        if branch_id and not Branch.objects.filter(BranchId=branch_id.BranchId if hasattr(branch_id, 'BranchId') else branch_id).exists():
            errors['BranchId'] = ["Branch with this ID does not exist."]

        if department_id and not Department.objects.filter(DepartmentId=department_id.DepartmentId if hasattr(department_id, 'DepartmentId') else department_id).exists():
            errors['DepartmentId'] = ["Department with this ID does not exist."]

        if errors:
            raise serializers.ValidationError(errors)

        return data
#------------------------------------------------------------------------------
class BranchSerializer(serializers.ModelSerializer):
    Name = serializers.CharField(max_length=100)
    Code = serializers.CharField(max_length=100)
    Address = serializers.CharField(max_length=255)
    City = serializers.CharField(max_length=100)
    State = serializers.CharField(max_length=100)
    Country = serializers.CharField(max_length=100)
    Mobile = serializers.CharField(max_length=20)  # Changed from IntegerField
    Email = serializers.CharField(max_length=500)  # Changed from EmailField
    CreateBy = serializers.CharField(max_length=50)
    UpdateBy = serializers.CharField(max_length=50)

    class Meta:
        model = Branch
        fields = ['BranchId','OwnerId', 'Name', 'Code', 'Address', 'City', 'State', 'Country', 'Mobile', 'Email', 'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt']
        read_only_fields = ['BranchId', 'CreatedAt', 'LastUpdatedAt']
        extra_kwargs = {
            'OwnerId':{'required': True},
            'BranchId': {'required': False},
            'Name': {'allow_null': True},
            'Code': {'allow_null': True},
            'Address': {'allow_null': True},
            'City': {'allow_null': True},
            'State': {'allow_null': True},
            'Country': {'allow_null': True},
            'Mobile': {'allow_null': True},
            'Email': {'allow_null': True},
            'CreateBy': {'allow_null': True},
            'UpdateBy': {'allow_null': True},
        }

    def to_internal_value(self, data):
        """Encrypt sensitive data before validation"""
        data = super().to_internal_value(data)
        
        # Convert Mobile to string if it's a number
        if 'Mobile' in data:
            data['Mobile'] = str(data['Mobile'])
        
        # Encrypt sensitive fields
        if 'Mobile' in data:
            data['Mobile'] = DataEncryptor.encrypt_data(data['Mobile'])
        if 'Email' in data:
            data['Email'] = DataEncryptor.encrypt_data(data['Email'])
            
        return data

    def to_representation(self, instance):
        """Decrypt data before sending response"""
        data = super().to_representation(instance)
        
        try:
            data['Mobile'] = DataEncryptor.decrypt_data(instance.Mobile)
            data['Email'] = DataEncryptor.decrypt_data(instance.Email)
        except Exception as e:
            # Log error but return encrypted values if decryption fails
            data['Mobile'] = instance.Mobile
            data['Email'] = instance.Email
            
        return data

    def validate_OwnerId(self, value):
        if self.instance is None:
            # 🔹 Create: OwnerId must exist in User table
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User (OwnerId) does not exist.")
        else:
            # 🔹 Update: OwnerId must already exist in the current Branch record
            if not Branch.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the branch being updated.")
        return value


#------------------------------------------------------------------------------
class DepartmentCreateSerializer(serializers.ModelSerializer):
    BranchId = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    Name = serializers.CharField(max_length=100)
    Code = serializers.CharField(max_length=100)
    Mobile = serializers.CharField(max_length=20)  # Changed from IntegerField
    Email = serializers.CharField(max_length=500)  # Changed from EmailField
    Create_by = serializers.CharField(max_length=50, required=False, allow_blank=True)
    Update_by = serializers.CharField(max_length=50, required=False, allow_blank=True)

    class Meta:
        model = Department
        fields = ['DepartmentId','BranchId','OwnerId', 'Name', 'Code', 'Mobile', 'Email', 'Create_by', 'Update_by', 'Created_at', 'Last_updated_at']
        read_only_fields = ['Created_at', 'Last_updated_at']
        extra_kwargs = {
            'BranchId': {'required': True},
            'OwnerId':{'required': True},
            'DepartmentId': {'required': False},
            'Name': {'allow_null': True},
            'Code': {'allow_null': True},
            'Mobile': {'allow_null': True},
            'Email': {'allow_null': True},
            'Create_by': {'allow_null': True},
            'Update_by': {'allow_null': True},
        }
    def to_internal_value(self, data):
        """Encrypt sensitive data before validation"""
        data = super().to_internal_value(data)
        
        # Convert Mobile to string if it's a number
        if 'Mobile' in data:
            data['Mobile'] = str(data['Mobile'])
        
        # Encrypt sensitive fields
        if 'Mobile' in data:
            data['Mobile'] = DataEncryptor.encrypt_data(data['Mobile'])
        if 'Email' in data:
            data['Email'] = DataEncryptor.encrypt_data(data['Email'])
            
        return data

    def to_representation(self, instance):
        """Decrypt data before sending response"""
        data = super().to_representation(instance)
        
        try:
            data['Mobile'] = DataEncryptor.decrypt_data(instance.Mobile)
            data['Email'] = DataEncryptor.decrypt_data(instance.Email)
        except Exception as e:
            # Log error but return encrypted values if decryption fails
            data['Mobile'] = instance.Mobile
            data['Email'] = instance.Email
            
        return data
    def validate(self, data):
        errors = {}

        # Validate Foreign Keys
        if not User.objects.filter(id=data.get('OwnerId').id).exists():
            errors['OwnerId'] = ["User with this ID does not exist."]
        if not Branch.objects.filter(BranchId=data.get('BranchId').BranchId).exists():
            errors['BranchId'] = ["Branch with this ID does not exist."]

        if errors:
            raise serializers.ValidationError(errors)

        return data
    
    def create(self, validated_data):
        validated_data['BranchId'] = validated_data.pop('BranchId')
        return super().create(validated_data)


class DepartmentUpdateSerializer(serializers.ModelSerializer):
    DepartmentId = serializers.IntegerField()

    class Meta:
        model = Department
        fields = ['DepartmentId','OwnerId', 'BranchId', 'Name', 'Code', 'Mobile', 'Email']
        extra_kwargs = {
            'BranchId': {'required': True},
            'OwnerId':{'required': True},
            'DepartmentId': {'required': False},
            'Name': {'allow_null': True},
            'Code': {'allow_null': True},
            'Mobile': {'allow_null': True},
            'Email': {'allow_null': True},
            'Create_by': {'allow_null': True},
            'Update_by': {'allow_null': True},
        }

class DepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
#------------------------------------------------------------------------------

class DesignationSerializer(serializers.ModelSerializer):
    Name = serializers.CharField(max_length=100,allow_blank=True)
    Code = serializers.CharField(max_length=100,allow_blank=True)
    CreateBy = serializers.CharField(max_length=50)
    UpdateBy = serializers.CharField(max_length=50)

    class Meta:
        model = Designation
        fields = ['DesignationId','OwnerId','BranchId','DepartmentId', 'Name', 'Code', 'CreateBy', 'UpdateBy', 'CreatedAt', 'LastUpdatedAt']
        read_only_fields = ['DesignationId', 'CreatedAt', 'lastUpdatedAt']
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'Name': {'allow_null': True},
            'Code': {'allow_null': True},
            'CreateBy': {'allow_null': True},
            'UpdateBy': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not Designation.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Designation.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Designation.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value
#------------------------------------------------------------------------------
from rest_framework import serializers
from .models import Products

class ProductsSerializer(serializers.ModelSerializer):
    term_display = serializers.CharField(source='get_term_display', read_only=True)
    # TermChoices = serializers.SerializerMethodField()  # Changed from 'term_choices' to 'TermChoices'
    Term = CaseInsensitiveChoiceField(choices=Products.TERM_CHOICES)
    class Meta:
        model = Products
        fields = '__all__'
        extra_fields = ['TermChoices']  # Include renamed custom field
        read_only_fields = ['term_display', 'TermChoices']
        extra_kwargs = {
            'OwnerId':{'required':True},
            'BranchId': {'required':True},
            'DepartmentId':{'required':True},
        }
    def get_TermChoices(self, obj):
        return [{'value': choice[0], 'label': choice[1]} for choice in Products.TERM_CHOICES]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['TermChoices'] = self.get_TermChoices(instance)
        return data

    def validate(self, attrs,data):
        # Only validate 'name' if not doing a partial update
        
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

        if not self.partial:
            required_fields = ['Name']
            missing_fields = [field for field in required_fields if not attrs.get(field)]
            if missing_fields:
                raise serializers.ValidationError({
                    'non_field_errors': [f"Missing required field(s): {', '.join(missing_fields)}"]
                })
        return attrs,data


#------------------------------------------------------------------------------

class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broker
        fields = [
            # Broker Identification
            "BrokerId","OwnerId", "BranchId", "DepartmentId", "LenderAssignedCode", "BrokerName", "BrokerType", "ContactPerson", "BrokerCategory",
            
            # Contact Details
            "PhoneNumber", "AltPhoneNumber", "Email", "Address", "City", "State", "Pincode", "AreaOfOperation",
            
            # KYC Compliance
            "PanNumber", "GST_Number", "AadhaarNumber", "IncorporationCert", "MSME_Certificate", "KycStatus",
            
            # Bank Details
            "BankName", "AccountNumber", "AccountHolderName", "IFSC_Code", "UPI_Id",
            
            # Agreement
            "AgreementStartDate", "AgreementEndDate", "CommissionRate", "CommissionType",
            "SignedAgreement", "TermsAndConditions",
            
            # Status Audit
            "Status", "Blacklisted", "LastAuditDate", "Rating",

            # Timestamps
            "CreatedAt", "LastUpdatedAt"
        ]
        extra_kwargs = {
            'OwnerId':{'required':True},
            'BranchId': {'required':True},
            'DepartmentId':{'required':True},
            'LenderAssignedCode': {'allow_null': True},
            'BrokerName': {'allow_null': True},
            'BrokerType': {'allow_null': True},
            'ContactPerson': {'allow_null': True},
            'BrokerCategory': {'allow_null': True},
            'PhoneNumber': {'allow_null': True},
            'AltPhoneNumber': {'allow_null': True},
            'Email': {'allow_null': True},
            'Address': {'allow_null': True},
            'City': {'allow_null': True},
            'State': {'allow_null': True},
            'Pincode': {'allow_null': True},
            'AreaOfOperation': {'allow_null': True},
            'PanNumber': {'allow_null': True},
            'GST_Number': {'allow_null': True},
            'AadhaarNumber': {'allow_null': True},
            'IncorporationCert': {'allow_null': True},
            'MSME_Certificate': {'allow_null': True},
            'KycStatus': {'allow_null': True},
            'BankName': {'allow_null': True},
            'AccountNumber': {'allow_null': True},
            'AccountHolderName': {'allow_null': True},
            'IFSC_Code': {'allow_null': True},
            'UPI_Id': {'allow_null': True},
            'AgreementStartDate': {'allow_null': True},
            'AgreementEndDate': {'allow_null': True},
            'CommissionRate': {'allow_null': True},
            'CommissionType': {'allow_null': True},
            'SignedAgreement': {'allow_null': True},
            'TermsAndConditions': {'allow_null': True},
            'Status': {'allow_null': True},
            'Blacklisted': {'allow_null': True},
            'LastAuditDate': {'allow_null': True},
            'Rating': {'allow_null': True},
        }
    def get_LenderAssignedCode(self, obj):
        return obj.decrypted_LenderAssignedCode

    def get_PhoneNumber(self, obj):
        return obj.decrypted_PhoneNumber

    def get_Email(self, obj):
        return obj.decrypted_Email

    def get_PanNumber(self, obj):
        return obj.decrypted_PanNumber

    def get_GST_Number(self, obj):
        return obj.decrypted_GST_Number

    def get_AadhaarNumber(self, obj):
        return obj.decrypted_AadhaarNumber

    def get_BankName(self, obj):
        return obj.decrypted_BankName

    def get_AccountNumber(self, obj):
        return obj.decrypted_AccountNumber

    def get_AccountHolderName(self, obj):
        return obj.decrypted_AccountHolderName

    def get_IFSC_Code(self, obj):
        return obj.decrypted_IFSC_Code

    def get_UPI_Id(self, obj):
        return obj.decrypted_UPI_Id

    def get_SignedAgreement(self, obj):
        file = obj.decrypted_SignedAgreement
        if file:
            return file.getvalue()
        return None

    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not Broker.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Broker.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Broker.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value

  
# #-----------------------------------------------------------------------------------
class CustomerInfoSerializer(serializers.ModelSerializer):
    Gender = CaseInsensitiveChoiceField(choices=Customer.GENDER_CHOICES)
    Salutation = CaseInsensitiveChoiceField(choices=Customer.SALUTATION_CHOICES, required=False, allow_null=True)
    RelationToCareOf = CaseInsensitiveChoiceField(choices=Customer.RELATION_CHOICES, required=False, allow_null=True)
    PreferredLanguage = CaseInsensitiveChoiceField(choices=Customer.LANGUAGE_CHOICES, required=False, allow_null=True)
    EmploymentType = CaseInsensitiveChoiceField(choices=Customer.EMPLOYMENT_CHOICES)
    AccountType = CaseInsensitiveChoiceField(choices=Customer.ACCOUNT_TYPE_CHOICES)
    ResidenceType = CaseInsensitiveChoiceField(choices=Customer.RESIDENCE_TYPE_CHOICES, required=False, allow_null=True)
    KycStatus = CaseInsensitiveChoiceField(choices=Customer.KYC_STATUS_CHOICES, default='pending')

    class Meta:
        model = Customer
        fields = [
            "CustomerId","OwnerId", "BranchId","DepartmentId","LoanId","InquiryId","FirstName", "MiddleName", "LastName", "DateOfBirth", "Gender",
            "Salutation", "CareOf", "RelationToCareOf", "Mobile", "AlternateMobile", "Email",
            "PreferredLanguage", "SameAsPermanent", "AddressLine1", "AddressLine2", "City", 
            "State", "Pincode", "Landmark", "EmploymentType", "MonthlyIncome", "CompanyName",
            "OfficeAddress", "BankName", "AccountNumber", "IFSC_Code", "AccountType",
            "AadhaarNumber", "PanNumber", "AadhaarFront", "PanCardCopy", "CustomerPhoto",
            "ResidenceType", "ElectricityBill", "CreatedBy", "KycStatus"
        ]
        extra_kwargs = {
            # Only these fields are required (all others will be allow_null)
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'LoanId': {'required': True},
            'InquiryId': {'required': True},

            # All others allow null
            'FirstName': {'allow_null': True},
            'MiddleName': {'allow_null': True},
            'LastName': {'allow_null': True},
            'DateOfBirth': {'allow_null': True},
            'Salutation': {'allow_null': True},
            'CareOf': {'allow_null': True},
            'RelationToCareOf': {'allow_null': True},
            'Mobile': {'allow_null': True},
            'AlternateMobile': {'allow_null': True},
            'Email': {'allow_null': True},
            'PreferredLanguage': {'allow_null': True},
            'SameAsPermanent': {'allow_null': True},
            'AddressLine1': {'allow_null': True},
            'AddressLine2': {'allow_null': True},
            'City': {'allow_null': True},
            'State': {'allow_null': True},
            'Pincode': {'allow_null': True},
            'Landmark': {'allow_null': True},
            'MonthlyIncome': {'allow_null': True},
            'CompanyName': {'allow_null': True},
            'OfficeAddress': {'allow_null': True},
            'BankName': {'allow_null': True},
            'AccountNumber': {'allow_null': True},
            'IFSC_Code': {'allow_null': True},
            'AadhaarNumber': {'allow_null': True},
            'PanNumber': {'allow_null': True},
            'AadhaarFront': {'allow_null': True},
            'PanCardCopy': {'allow_null': True},
            'CustomerPhoto': {'allow_null': True},
            'ResidenceType': {'allow_null': True},
            'ElectricityBill': {'allow_null': True},
            'CreatedBy': {'allow_null': True},
            'KycStatus': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            # Create: Validate in User table
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            # Update: Validate record has same OwnerId
            if not Customer.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not match the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Customer.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not match the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Customer.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not match the record being updated.")
        return value

    def validate_LoanId(self, value):
        if value is not None:
            if self.instance is None:
                if not LoanApplication.objects.filter(pk=value.pk).exists():
                    raise serializers.ValidationError("Loan with this ID does not exist.")
            else:
                if not Customer.objects.filter(pk=self.instance.pk, LoanId=value).exists():
                    raise serializers.ValidationError("This LoanId does not belong to the record being updated.")
        return value

    def validate_InquiryId(self, value):
        if value is not None:  # Only validate if InquiryId is provided
            if self.instance is None:  # Creating new record
                if not NewInquiry.objects.filter(pk=value.pk).exists():
                    raise serializers.ValidationError("Inquiry with this ID does not exist.")
            else:  # Updating existing record
                if not Customer.objects.filter(pk=self.instance.pk, InquiryId=value).exists():
                    raise serializers.ValidationError("This InquiryId does not belong to the record being updated.")
        return value



    def validate(self, data):
        Email = data.get('Email')
        Mobile = data.get('Mobile')

        if self.instance:
            # Update: Exclude current record
            if Customer.objects.exclude(pk=self.instance.pk).filter(Email=Email).exists():
                raise serializers.ValidationError({'Email': "Duplicate Email found."})
            if Customer.objects.exclude(pk=self.instance.pk).filter(Mobile=Mobile).exists():
                raise serializers.ValidationError({'Mobile': "Duplicate Mobile number found."})
        else:
            # Create
            if Customer.objects.filter(Email=Email).exists():
                raise serializers.ValidationError({'Email': "Duplicate Email found."})
            if Customer.objects.filter(Mobile=Mobile).exists():
                raise serializers.ValidationError({'Mobile': "Duplicate Mobile number found."})

        return data


class VehicleSerializer(serializers.ModelSerializer):
    VehicleType = CaseInsensitiveChoiceField(choices=Vehicle.VEHICLE_TYPE_CHOICES)
    FuelType = CaseInsensitiveChoiceField(choices=Vehicle.FUEL_TYPE_CHOICES)
    InsuranceType = CaseInsensitiveChoiceField(choices=Vehicle.INSURANCE_TYPE_CHOICES)
    HP_Status = CaseInsensitiveChoiceField(choices=Vehicle.HP_STATUS_CHOICES)
    RC_Status = CaseInsensitiveChoiceField(choices=Vehicle.RC_STATUS_CHOICES)

    class Meta:
        model = Vehicle
        exclude = ['CreatedAt', 'UpdatedAt']
        extra_kwargs = {
            'OwnerId':{'required':True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            # All others are optional and allow null
            'VehicleType': {'allow_null': True},
            'RegistrationNumber': {'allow_null': True},
            'OwnerName': {'allow_null': True},
            'ManufactureYear': {'allow_null': True},
            'RegistrationDate': {'allow_null': True},
            'Make': {'allow_null': True},
            'Model': {'allow_null': True},
            'Variant': {'allow_null': True},
            'FuelType': {'allow_null': True},
            'EngineNumber': {'allow_null': True},
            'ChassisNumber': {'allow_null': True},
            'VehicleColor': {'allow_null': True},
            'RC_ExpiryDate': {'allow_null': True},
            'InvoiceAmount': {'allow_null': True},
            'OnRoadPrice': {'allow_null': True},
            'MarginMoney': {'allow_null': True},
            'DealerName': {'allow_null': True},
            'DealerPan': {'allow_null': True},
            'InsuranceType': {'allow_null': True},
            'InsuranceCompany': {'allow_null': True},
            'InsuranceNumber': {'allow_null': True},
            'InsuranceExpiry': {'allow_null': True},
            'IDV_Value': {'allow_null': True},
            'HP_Status': {'allow_null': True},
            'RC_Status': {'allow_null': True},
            'LastVerifiedBy': {'allow_null': True},
            'RC_Copy': {'allow_null': True, 'required': False},
            'InsuranceCopy': {'allow_null': True, 'required': False},
            'InvoiceCopy': {'allow_null': True, 'required': False},
            'FitnessCertificate': {'allow_null': True, 'required': False},
        }

    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not Designation.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Designation.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Designation.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value




from rest_framework import serializers
from .models import InitiateSeizure

class InitiateSeizureSerializer(serializers.ModelSerializer):
    SeizureReason = CaseInsensitiveChoiceField(choices=[
        ("default", "Default"),
        ("fraud", "Fraud"),
        ("voluntary surrender", "Voluntary Surrender")
    ])
    class Meta:
        model = InitiateSeizure
        fields = [
            'Id','BranchId','DepartmentId','LoanId', 'SeizureReason', 'InitiatedBy',
            'InitiatedDate', 'LegalOrderCopy', 'BorrowerNotice', 'Remarks'
        ]
        extra_kwargs = {
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'LoanId': {'required': True},
            'InitiatedBy': {'required': True},
            # Optional fields
            'LegalOrderCopy': {'allow_null': True},
            'BorrowerNotice': {'allow_null': True},
            'Remarks': {'allow_null': True},
            'InitiatedDate': {'read_only': True},
        }

    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not InitiateSeizure.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not InitiateSeizure.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not InitiateSeizure.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value
        

from rest_framework import serializers
from .models import AssignAgent, SitePhoto

class SitePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitePhoto
        fields = ['Image', 'Timestamp']


class AssignAgentSerializer(serializers.ModelSerializer):
    SitePhotosPre = SitePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = AssignAgent
        fields = '__all__'
    extra_kwargs = {
            'Seizure': {'required': True},
            'AssignmentDate': {'required': True},
            'AgentAuthorization': {'allow_null': True},
            'ScheduledVisit': {'allow_null': True},
            'GPS_Location': {'allow_null': True},
        }
    def validate(self, data):
        if self.instance is None:
            Seizure = data.get("Seizure")
            if AssignAgent.objects.filter(Seizure=Seizure).exists():
                raise serializers.ValidationError("This agent is already assigned to the seizure.")
        return data



# serializers.py
class AssetPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetPhoto
        fields = ['Image', 'Timestamp']

class SeizureExecutionSerializer(serializers.ModelSerializer):
    Outcome = CaseInsensitiveChoiceField(choices=[
        ("seized", "Seized"),
        ("failed", "Failed"),
        ("settled", "Settled")
    ])
    AssetPhotos = AssetPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = SeizureExecution
        fields = '__all__'
    extra_kwargs = {
            'AssignAgentId': {'required': True},
            'ExecutionDate': {'allow_null': True},
            'Outcome': {'allow_null': True},
            'AssetType': {'allow_null': True},
            'AssetDescription': {'allow_null': True},
            'PoliceFIR_Copy': {'allow_null': True},
            'WitnessProof': {'allow_null': True},
            'AssetLocation': {'allow_null': True},
        }
    def validate(self, data):
        if self.instance is None:
            AssignAgentId = data.get('AssignAgentId')
            if SeizureExecution.objects.filter(AssignAgentId=AssignAgentId).exists():
                raise serializers.ValidationError("Execution for this agent is already recorded.")
        return data


class AssignBrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignBroker
        fields = '__all__'
        extra_kwargs = {
            'AssetId': {'required': True},
            'BrokerId': {'required': True},
            'BrokerAgreement': {'allow_null': True},
            'AssignedDate': {'allow_null': True},
            'ExpectedSaleDate': {'allow_null': True},
            'AssetVideo': {'allow_null': True},
            'BrokerCommission': {'allow_null': True},
            'CommissionType': {'allow_null': True},
        }
    def validate(self, data):
        if self.instance is None:
            AssetId = data.get('AssetId')
            BrokerId = data.get('BrokerId')
            if AssignBroker.objects.filter(AssetId=AssetId, BrokerId=BrokerId).exists():
                raise serializers.ValidationError("This broker is already assigned to this asset.")
        return data



# # serializers.py
class SaleExecutionSerializer(serializers.ModelSerializer):
    SaleStatus = CaseInsensitiveChoiceField(choices=[
        ("sold", "Sold"),
        ("returned", "Returned"),
        ("offer pending", "Offer Pending")
    ])
    class Meta:
        model = SaleExecution
        fields = '__all__'
        extra_kwargs = {
            'AssignBrokerId': {'required': True},
            'SaleStatus': {'allow_null': True},
            'SaleDate': {'allow_null': True},
            'BuyerName': {'allow_null': True},
            'SaleAmount': {'allow_null': True},
            'SaleDeed': {'allow_null': True},
            'BuyerKyc': {'allow_null': True},
            'PaymentProof': {'allow_null': True},
        }
    def validate(self, data):
        # Check duplicate broker + sale_status
        if self.instance is None:
            AssignBrokerId = data.get("AssignBrokerId")
            SaleStatus = data.get("SaleStatus")
            if SaleExecution.objects.filter(AssignBrokerId=AssignBrokerId, SaleStatus=SaleStatus).exists():
                raise serializers.ValidationError("Sale execution already exists for this broker with the same sale status.")
        return data



# # serializers.py
class RecoveryClosureSerializer(serializers.ModelSerializer):
    RecoveryMode = CaseInsensitiveChoiceField(choices=[
        ("sale", "Sale"),
        ("settlement", "Settlement"),
        ("write-off", "Write-Off")
    ])
    ClosureStatus = CaseInsensitiveChoiceField(choices=[
        ("closed", "Closed"),
        ("disposed", "Disposed"),
        ("returned", "Returned")
    ])
    class Meta:
        model = RecoveryClosure
        fields = '__all__'
        extra_kwargs = {
            'Sale': {'required': True},
            'RecoveredAmount': {'allow_null': True},
            'NodalApproval': {'allow_null': True},
            'RecoveryMode': {'allow_null': True},
            'ClosureStatus': {'allow_null': True},
            'AuditReport': {'allow_null': True},
        }
    def validate(self, data):
        if self.instance is None:
            Sale = data.get("Sale")
            ClosureStatus = data.get("ClosureStatus")
            if RecoveryClosure.objects.filter(Sale=Sale, ClosureStatus=ClosureStatus).exists():
                raise serializers.ValidationError("Recovery closure already exists for this sale with the same closure status.")
        return data


from rest_framework import serializers
from .models import (
    Collateral,
    RealEstateCollateral,
    VehicleCollateral,
    FinancialCollateral,
    CollateralDocuments,
    
)

class InventoryCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCollateral
        fields = ["Description", "Quantity", "StorageLocation"]

class MachineryCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineryCollateral
        fields = ["MachineType", "Manufacturer", "PurchaseYear"]

class OthersCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = OthersCollateral
        fields = ["Description", "SupportingDocuments"]

class RealEstateCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateCollateral
        exclude = ['CollateralId']


class VehicleCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCollateral
        exclude = ['CollateralId']


class FinancialCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialCollateral
        exclude = ['CollateralId']




# --- Document Serializer ---
from rest_framework import serializers
from .models import CollateralDocuments

class CollateralDocumentsSerializer(serializers.ModelSerializer):
    TitleDeedCopy = serializers.FileField(required=False)
    ValuationReport = serializers.FileField(required=False)
    InsuranceDocument = serializers.FileField(required=False)
    SitePhotos = serializers.FileField(required=False)

    class Meta:
        model = CollateralDocuments
        fields = [
            "id","TitleDeedCopy", "ValuationReport",
            "InsuranceDocument", "SitePhotos"
        ]

from InquiryLoanProcess.models import LoanApplication

class CollateralSerializer(serializers.ModelSerializer):
    RealEstate = RealEstateCollateralSerializer(required=False)
    Vehicle = VehicleCollateralSerializer(required=False)
    Financial = FinancialCollateralSerializer(required=False)
    CollateralType = CaseInsensitiveChoiceField(choices=Collateral.COLLATERAL_TYPES)
    CollateralStatus = CaseInsensitiveChoiceField(choices=Collateral.COLLATERAL_STATUS)
    LoanId = serializers.PrimaryKeyRelatedField(queryset=LoanApplication.objects.all())
    Inventory = InventoryCollateralSerializer(required=False)
    Machinery = MachineryCollateralSerializer(required=False)
    Others = OthersCollateralSerializer(required=False)
    Documents = CollateralDocumentsSerializer(required=False)  
    class Meta:
        model = Collateral
        fields = [
            "CollateralId","OwnerId","BranchId","DepartmentId", "LoanId","AssetId", "CollateralType", "CollateralStatus",
            "OwnerName", "OwnershipPercentage", "TitleDocNumber",
            "EncumbranceStatus", "LienHolderDetails", "CurrentValue",
            "ValuationDate", "ValuerRegNumber", "InsurancePolicyNo",
            "CollateralScore", "RiskFlag", "CreatedAt", "UpdatedAt",
            "RealEstate", "Vehicle", "Financial",
            "Inventory", "Machinery", "Others","Documents"
        ]
        read_only_fields = ["CollateralId", "RiskFlag", "CreatedAt", "UpdatedAt"]
        extra_kwargs = {
            'OwnerId':{'required' : True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'LoanId': {'required': True},
            'AssetId': {'required': True}, 
            'CollateralType': {'allow_null': True}, 
            'CollateralStatus': {'allow_null': True},
            'OwnerName': {'allow_null': True},
            'OwnershipPercentage': {'allow_null': True},
            'TitleDocNumber': {'allow_null': True},
            'EncumbranceStatus': {'allow_null': True},
            'LienHolderDetails': {'allow_null': True}, 
            'CurrentValue': {'allow_null': True},
            'ValuationDate': {'allow_null': True},
            'ValuerRegNumber': {'allow_null': True},
            'InsurancePolicyNo': {'allow_null': True},
            'CollateralScore': {'allow_null': True},
            'RiskFlag': {'allow_null': True}, 
            'CreatedAt': {'allow_null': True},
            'UpdatedAt': {'allow_null': True},
            'RealEstate': {'allow_null': True},
            'Vehicle': {'allow_null': True}, 
            'Financial': {'allow_null': True},
            'Inventory': {'allow_null': True}, 
            'Machinery': {'allow_null': True}, 
            'Others': {'allow_null': True},
            'Documents': {'allow_null': True},
        }
    def create(self, validated_data):
        real_estate_data = validated_data.pop('RealEstate', None)
        vehicle_data = validated_data.pop('Vehicle', None)
        financial_data = validated_data.pop('Financial', None)
        inventory_data = validated_data.pop('Inventory', None)
        machinery_data = validated_data.pop('Machinery', None)
        others_data = validated_data.pop('Others', None)

        collateral = Collateral.objects.create(**validated_data)

        if real_estate_data:
            RealEstateCollateral.objects.create(CollateralId=collateral, **real_estate_data)
        if vehicle_data:
            VehicleCollateral.objects.create(CollateralId=collateral, **vehicle_data)
        if financial_data:
            FinancialCollateral.objects.create(CollateralId=collateral, **financial_data)
        if inventory_data:
            InventoryCollateral.objects.create(CollateralId=collateral, **inventory_data)
        if machinery_data:
            MachineryCollateral.objects.create(CollateralId=collateral, **machinery_data)
        if others_data:
            OthersCollateral.objects.create(CollateralId=collateral, **others_data)

        return collateral
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not Collateral.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Collateral.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Collateral.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value

    def validate_LoanId(self, value):
        # value is a LoanApplication object
        if self.instance and self.instance.LoanId != value:
            raise serializers.ValidationError("This LoanId does not belong to the record being updated.")
        return value


    def update(self, instance, validated_data):
        nested_serializers = {
            'RealEstate': RealEstateCollateralSerializer,
            'Vehicle': VehicleCollateralSerializer,
            'Financial': FinancialCollateralSerializer,
        }

        for nested_field, serializer_class in nested_serializers.items():
            nested_data = validated_data.pop(nested_field, None)
            if nested_data:
                nested_instance = getattr(instance, nested_field, None)
                if nested_instance:
                    serializer = serializer_class(instance=nested_instance, data=nested_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    serializer_class().create({'CollateralId': instance, **nested_data})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

            
class CollateralUpdateSerializer(serializers.ModelSerializer):
    RealEstate = RealEstateCollateralSerializer(required=False)
    Vehicle = VehicleCollateralSerializer(required=False)
    Financial = FinancialCollateralSerializer(required=False)
    Inventory = InventoryCollateralSerializer(required=False)
    Machinery = MachineryCollateralSerializer(required=False)
    Others = OthersCollateralSerializer(required=False)
    Documents = CollateralDocumentsSerializer(required=False)

    class Meta:
        model = Collateral
        fields = [
            "CollateralId", "OwnerId", "BranchId", "DepartmentId", "LoanId", "AssetId","CollateralType", "CollateralStatus",
            "OwnerName", "OwnershipPercentage", "TitleDocNumber", "EncumbranceStatus", "LienHolderDetails", 
            "CurrentValue", "ValuationDate", "ValuerRegNumber", "InsurancePolicyNo", "CollateralScore",
            "RealEstate", "Vehicle", "Financial", "Inventory", "Machinery", "Others", "Documents"
        ]
        read_only_fields = ["CollateralId", "OwnerId", "BranchId", "DepartmentId", "LoanId","AssetId", "CreatedAt", "UpdatedAt"]
        extra_kwargs = {
            'OwnerId':{'required' : True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'LoanId': {'required': True},
            'AssetId': {'required': True}, 
            'CollateralType': {'allow_null': True}, 
            'CollateralStatus': {'allow_null': True},
            'OwnerName': {'allow_null': True},
            'OwnershipPercentage': {'allow_null': True},
            'TitleDocNumber': {'allow_null': True},
            'EncumbranceStatus': {'allow_null': True},
            'LienHolderDetails': {'allow_null': True}, 
            'CurrentValue': {'allow_null': True},
            'ValuationDate': {'allow_null': True},
            'ValuerRegNumber': {'allow_null': True},
            'InsurancePolicyNo': {'allow_null': True},
            'CollateralScore': {'allow_null': True},
            'RiskFlag': {'allow_null': True}, 
            'CreatedAt': {'allow_null': True},
            'UpdatedAt': {'allow_null': True},
            'RealEstate': {'allow_null': True},
            'Vehicle': {'allow_null': True}, 
            'Financial': {'allow_null': True},
            'Inventory': {'allow_null': True}, 
            'Machinery': {'allow_null': True}, 
            'Others': {'allow_null': True},
            'Documents': {'allow_null': True},
        }
    def validate_OwnerId(self, value):
        if self.instance is None:
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            if not Collateral.objects.filter(pk=self.instance.pk, OwnerId=value.id).exists():
                raise serializers.ValidationError("This OwnerId does not belong to the record being updated.")
        return value

    def validate_BranchId(self, value):
        if self.instance is None:
            if not Branch.objects.filter(BranchId=value.BranchId).exists():
                raise serializers.ValidationError("Branch with this ID does not exist.")
        else:
            if not Collateral.objects.filter(pk=self.instance.pk, BranchId=value.BranchId).exists():
                raise serializers.ValidationError("This BranchId does not belong to the record being updated.")
        return value

    def validate_DepartmentId(self, value):
        if self.instance is None:
            if not Department.objects.filter(DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("Department with this ID does not exist.")
        else:
            if not Collateral.objects.filter(pk=self.instance.pk, DepartmentId=value.DepartmentId).exists():
                raise serializers.ValidationError("This DepartmentId does not belong to the record being updated.")
        return value

    def validate_LoanId(self, value):
        if self.instance and self.instance.LoanId != value:
            raise serializers.ValidationError("This LoanId does not belong to the record being updated.")
        return value
    def update(self, instance, validated_data):
        # Handle nested updates
        nested_data = {
            'RealEstate': (RealEstateCollateral, validated_data.pop('RealEstate', None)),
            'Vehicle': (VehicleCollateral, validated_data.pop('Vehicle', None)),
            'Financial': (FinancialCollateral, validated_data.pop('Financial', None)),
            'Inventory': (InventoryCollateral, validated_data.pop('Inventory', None)),
            'Machinery': (MachineryCollateral, validated_data.pop('Machinery', None)),
            'Others': (OthersCollateral, validated_data.pop('Others', None))
        }

        for field_name, (model_class, data) in nested_data.items():
            if data:
                nested_instance = getattr(instance, field_name, None)
                if nested_instance:
                    for attr, value in data.items():
                        setattr(nested_instance, attr, value)
                    nested_instance.save()
                else:
                    model_class.objects.create(CollateralId=instance, **data)

        # Handle document updates
        document_data = validated_data.pop('Documents', None)
        if document_data:
            doc_instance = instance.Documents
            if doc_instance:
                for attr, value in document_data.items():
                    if value:  # Only update if new file is provided
                        setattr(doc_instance, attr, value)
                doc_instance.save()
            else:
                document_data['CollateralId_id'] = instance.CollateralId
                CollateralDocuments.objects.create(**document_data)

        # Update main collateral fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class LoanProductMasterSerializer(serializers.ModelSerializer):
    ProductCategory = CaseInsensitiveChoiceField(choices=PRODUCT_CATEGORIES)

    class Meta:
        model = LoanProductMaster
        fields = '__all__'
        read_only_fields = ['CreatedBy','CreatedAt']
        extra_kwargs = {
            'OwnerId':{'required':True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'ProductName': {'allow_null': True},
            'ProductCode': {'allow_null': True},
            'ProductCategory': {'allow_null': True},
            'ActiveStatus': {'allow_null': True},
            'Description': {'allow_null': True},
        }

    def validate(self, data):
        if self.instance:
            # Update case: check for duplicate ProductCode (excluding current)
            if LoanProductMaster.objects.exclude(ProductId=self.instance.ProductId).filter(ProductCode=data.get("ProductCode")).exists():
                raise serializers.ValidationError({"ProductCode": "ProductCode must be unique."})
        else:
            # Create case: check for duplicate ProductCode
            if LoanProductMaster.objects.filter(ProductCode=data.get("ProductCode")).exists():
                raise serializers.ValidationError({"ProductCode": "ProductCode must be unique."})

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

class InterestConfigSerializer(serializers.ModelSerializer):
    InterestType = CaseInsensitiveChoiceField(choices=INTEREST_TYPES)
    InterestBasis = CaseInsensitiveChoiceField(choices=INTEREST_BASIS)

    class Meta:
        model = InterestConfiguration
        fields = '__all__'
        extra_kwargs = {
            'ProductId': {'required': True},
            'InterestType': {'allow_null': True},
            'BaseInterestRate': {'allow_null': True},
            'MaxInterestRate': {'allow_null': True},
            'InterestBasis': {'allow_null': True},
            'InterestFormula': {'allow_null': True}
        }
    def validate(self, data):
        if data.get('InterestType') == 'Custom' and not data.get('InterestFormula'):
            raise serializers.ValidationError({
                "InterestFormula": "Required when InterestType is 'Custom'."
            })
        return data


class ChargeSerializer(serializers.ModelSerializer):
    ChargeType = CaseInsensitiveChoiceField(choices=CHARGE_TYPE)
    class Meta:
        model = Charge
        fields = '__all__'
        extra_kwargs = {
            'ProductId': {'required': True},
            'ChargeType' : {'allow_null': True},
            'ChargeValue': {'allow_null': True},
            'MinAmount' : {'allow_null': True},
            'MaxAmount': {'allow_null': True},
            'ChargeName' : {'allow_null': True},
        }
    def validate(self, data):
        # Avoid duplicate ChargeName for same ProductId
        if Charge.objects.filter(
            ProductId=data['ProductId'], 
            ChargeName__iexact=data['ChargeName']
        ).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Charge with this name already exists for this product.")
        return data

class ToggleField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str):
            value = data.lower()
            if value in ['yes', 'true', '1']:
                return True
            elif value in ['no', 'false', '0']:
                return False
        elif isinstance(data, bool):
            return data
        raise serializers.ValidationError("Invalid toggle value")

    def to_representation(self, value):
        return 'Yes' if value else 'No'


class PenaltySerializer(serializers.ModelSerializer):
    ForeclosureAllowed = ToggleField()

    class Meta:
        model = Penalty
        fields = [
            'id', 'ProductId', 'LatePaymentFee', 'BounceCharge',
            'ForeclosureAllowed', 'ForeclosureLockin', 'ForeclosureFee'
        ]
        extra_kwargs = {
            'ProductId': {'required': True},
            'LatePaymentFee' : {'allow_null': True},
            'BounceCharge': {'allow_null': True},
            'ForeclosureAllowed' : {'allow_null': True},
            'ForeclosureLockin': {'allow_null': True},
            'ForeclosureFee' : {'allow_null': True},
        }
    def validate(self, data):
        # Prevent duplicate Penalty for the same product
        if self.instance is None:
            if Penalty.objects.filter(ProductId=data.get('ProductId')).exists():
                raise serializers.ValidationError("Penalty already exists for this ProductId.")
        return data
    def to_internal_value(self, data):
        # Enforce strict fields
        allowed = set(self.fields.keys())
        extra = set(data.keys()) - allowed
        if extra:
            raise serializers.ValidationError({field: "Unexpected field" for field in extra})
        return super().to_internal_value(data)




from rest_framework import serializers
from .models import TenureAmount

class TenureAmountSerializer(serializers.ModelSerializer):
    EMI_CalculationBasis = CaseInsensitiveChoiceField(choices=EMI_CALC_BASIS)

    class Meta:
        model = TenureAmount
        fields = '__all__'
        extra_kwargs = {
            'ProductId': {'required': True},
            'MinTenureMonths' : {'allow_null': True},
            'MaxTenureMonths': {'allow_null': True},
            'MinLoanAmount' : {'allow_null': True},
            'MaxLoanAmount': {'allow_null': True},
            'AllowedRepaymentModes' : {'allow_null': True},
            'EMI_CalculationBasis': {'allow_null': True},
            'EMI_Formula': {'allow_null': True},
        }
    def validate(self, data):
        product_id = data.get("ProductId")
        if TenureAmount.objects.filter(ProductId=product_id).exists():
            raise serializers.ValidationError({"ProductId": "tenure amount with this ProductId already exists."})
        return data

class BusinessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessRule
        fields = [
            'id',
            'ProductId',
            'CO_ApplicantRequired',
            'GuarantorRequired',
            'EligibilityRule',
            'DocumentsRequired',
        ]
        extra_kwargs = {
            'ProductId': {'required': True},
            'CO_ApplicantRequired': {'allow_null': True},
            'GuarantorRequired': {'allow_null': True},
            'EligibilityRule': {'allow_null': True},
            'DocumentsRequired': {'allow_null': True},
        }

    def validate(self, data):
        # Prevent duplicate entries for ProductId on create
        if self.instance is None:
            if BusinessRule.objects.filter(ProductId=data.get('ProductId')).exists():
                raise serializers.ValidationError("Business Rule already exists for this ProductId.")
        return data
    def to_internal_value(self, data):
        # Enforce strict fields
        allowed = set(self.fields.keys())
        extra = set(data.keys()) - allowed
        if extra:
            raise serializers.ValidationError({field: "Unexpected field" for field in extra})
        return super().to_internal_value(data)



class UDFMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UDFMapping
        fields = ['id', 'ProductId', 'UDF_Name', 'ShowIn', 'UsedIn_EMI']
        extra_kwargs = {
            'ProductId': {'required': True},
            'UDF_Name': {'allow_null': True},
            'ShowIn': {'allow_null': True},
            'UsedIn_EMI': {'allow_null': True}
        }
    def validate(self, data):
        # Prevent duplicates: UDF_Name + ProductId
        if self.instance is None:
            if UDFMapping.objects.filter(ProductId=data['ProductId'], UDF_Name__iexact=data['UDF_Name']).exists():
                raise serializers.ValidationError("UDF with this name already exists for the given Product.")
        return data
    def to_internal_value(self, data):
        # Enforce strict fields
        allowed = set(self.fields.keys())
        extra = set(data.keys()) - allowed
        if extra:
            raise serializers.ValidationError({field: "Unexpected field" for field in extra})
        return super().to_internal_value(data)




class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code']

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name', 'code', 'symbol']
