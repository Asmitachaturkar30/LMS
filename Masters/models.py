from django.db import models
from django.core.validators import (
    RegexValidator, MinValueValidator, MaxValueValidator,
    MinLengthValidator, FileExtensionValidator, ValidationError
)
from datetime import datetime
from CiLoanCore.encryption import DataEncryptor


class Source(models.Model):
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    SourceId = models.AutoField(primary_key=True)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    Name = models.CharField(max_length=500)
    Code = models.CharField(max_length=500)
    CreateBy = models.CharField(max_length=50)
    UpdateBy = models.CharField(max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['Name']

    class Meta:
        db_table = 'd_Source'

    def save(self, *args, **kwargs):
        """Auto-generate search hashes before saving"""
        if self.Name:
            import hashlib
            original_name = DataEncryptor.decrypt_data(self.Name) if self.pk else self.Name
            self.NameHash = hashlib.sha256(original_name.encode()).hexdigest()
        
        if self.Code:
            original_code = DataEncryptor.decrypt_data(self.Code) if self.pk else self.Code
            self.CodeHash = hashlib.sha256(original_code.encode()).hexdigest()
        
        super().save(*args, **kwargs)

    def __str__(self):
        try:
            return DataEncryptor.decrypt_data(self.Name)
        except:
            return "Encrypted Source"
#------------------------------------------------------------------------------

class Rating(models.Model):
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    RateId = models.AutoField(primary_key=True)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    Name = models.CharField(max_length=100)
    Code = models.CharField(max_length=100)
    CreateBy = models.CharField(max_length=50)
    UpdateBy = models.CharField(max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'd_Ratings'

#------------------------------------------------------------------------------

class Branch(models.Model):
    BranchId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    Code = models.CharField(max_length=100)
    Address = models.CharField(max_length=255)
    City = models.CharField(max_length=100)
    State = models.CharField(max_length=100)
    Country = models.CharField(max_length=100)
    # Mobile = models.BigIntegerField() 
    # Email = models.EmailField(max_length=500, unique=True)
    Mobile = models.CharField(max_length=500)  # Changed to CharField for encrypted data
    Email = models.CharField(max_length=500)
    CreateBy = models.CharField(max_length=50)
    UpdateBy = models.CharField(max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'd_Branch'

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

#------------------------------------------------------------------------------

class Department(models.Model):
    DepartmentId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    Name = models.CharField(max_length=100)
    Code = models.CharField(max_length=100)
    # Mobile = models.BigIntegerField(null=True, blank=True)
    # Email = models.EmailField(max_length=150, unique=True, null=True, blank=True)
    Mobile = models.CharField(max_length=500)  # Changed to CharField for encrypted data
    Email = models.CharField(max_length=500)
    Create_by = models.CharField(max_length=50, null=True, blank=True)
    Update_by = models.CharField(max_length=50, null=True, blank=True)
    Created_at = models.DateTimeField(auto_now_add=True)
    Last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'd_Department'

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
#------------------------------------------------------------------------------

class Designation(models.Model):
    DesignationId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    Name = models.CharField(max_length=100)
    Code = models.CharField(max_length=100)
    CreateBy = models.CharField(max_length=50)
    UpdateBy = models.CharField(max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'd_Designation'

#------------------------------------------------------------------------------

class Products(models.Model):
    TERM_CHOICES = [
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year'),
    ]
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    Name = models.CharField(max_length=100)
    Code = models.CharField(max_length=50, unique=True)
    InterestRate = models.DecimalField(max_digits=5, decimal_places=2)
    Term = models.CharField(max_length=10, choices=TERM_CHOICES)
    LatePenalties = models.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        db_table = 'd_Products'

#------------------------------------------------------------------------------


class Broker(models.Model):
    # Broker Identification
    BrokerId =models.AutoField(primary_key=True)  # Primary key
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    LenderAssignedCode = models.CharField(max_length=20, unique=True)  # Lender broker code
    BrokerName = models.CharField(max_length=255)  # Name of broker or firm
    BrokerType = models.CharField(max_length=50)  # Individual/Agency/Firm
    ContactPerson = models.CharField(max_length=255, blank=True, null=True)  # Contact person for firm
    BrokerCategory = models.CharField(max_length=50)  # Retail/Commercial/Special Assets

    # Contact Details
    PhoneNumber = models.CharField(max_length=10)  # 10-digit phone number
    AltPhoneNumber = models.CharField(max_length=10, blank=True, null=True)  # Alternate contact
    Email = models.EmailField()  # Broker email address
    Address = models.TextField()  # Full address
    City = models.CharField(max_length=100)  # City
    State = models.CharField(max_length=100)  # State
    Pincode = models.CharField(max_length=6)  # Pincode
    AreaOfOperation = models.JSONField(default=list)  # List of zones/districts

    # KYC Compliance
    PanNumber = models.CharField(max_length=10)  # PAN number
    GST_Number = models.CharField(max_length=15, blank=True, null=True)  # GSTIN
    AadhaarNumber = models.CharField(max_length=12, blank=True, null=True)  # Aadhaar number
    IncorporationCert = models.FileField(upload_to='kyc_docs/', blank=True, null=True)  # Certificate of incorporation
    MSME_Certificate = models.FileField(upload_to='kyc_docs/', blank=True, null=True)  # MSME certificate
    KycStatus = models.CharField(max_length=20, default='Pending')  # KYC Status

    # Bank Details
    BankName = models.CharField(max_length=100)  # Bank name
    AccountNumber = models.CharField(max_length=20)  # Bank account number
    AccountHolderName = models.CharField(max_length=100)  # Name on account
    IFSC_Code = models.CharField(max_length=11)  # IFSC code
    UPI_Id = models.CharField(max_length=50, blank=True, null=True)  # UPI ID

    # Example: make agreement fields optional
    AgreementStartDate = models.DateField(blank=True, null=True)
    AgreementEndDate = models.DateField(blank=True, null=True)
    CommissionRate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    CommissionType = models.CharField(max_length=20, blank=True, null=True)
    SignedAgreement = models.FileField(upload_to='agreements/', blank=True, null=True)
    TermsAndConditions = models.TextField(blank=True, null=True)


    # Status Audit
    Status = models.BooleanField(default=True)  # Active/Inactive
    Blacklisted = models.BooleanField(default=False)  # If blacklisted
    LastAuditDate = models.DateField(blank=True, null=True)  # Last audit date
    Rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)  # Rating out of 5

    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table ='Broker'


class Customer(models.Model):
    # Core Customer Information
    CustomerId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User', on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, db_column='loan_id')
    InquiryId = models.ForeignKey(
        'InquiryLoanProcess.NewInquiry', on_delete=models.SET_NULL, db_column='InquiryId',null=True,blank=True,related_name='customers_Inquiry')
    FirstName = models.CharField(max_length=50)
    MiddleName = models.CharField(max_length=50, blank=True, null=True)
    LastName = models.CharField(max_length=50)
    DateOfBirth = models.DateField()
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    Gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    SALUTATION_CHOICES = [
        ('mr', 'Mr'),
        ('mrs', 'Mrs'),
        ('ms', 'Ms'),
        ('dr', 'Dr'),
    ]
    Salutation = models.CharField(max_length=10, choices=SALUTATION_CHOICES, blank=True, null=True)

    CareOf = models.CharField(max_length=100, blank=True, null=True)
    
    RELATION_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('spouse', 'Spouse'),
    ]
    RelationToCareOf = models.CharField(max_length=10, choices=RELATION_CHOICES, blank=True, null=True)

    # Contact & Address
    Mobile = models.CharField(max_length=15)
    AlternateMobile = models.CharField(max_length=15, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    
    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('hindi', 'Hindi'),
        ('regional', 'Regional'),
    ]
    PreferredLanguage = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, blank=True, null=True)

    # Address Fields
    SameAsPermanent = models.BooleanField(default=False)
    AddressLine1 = models.CharField(max_length=100)
    AddressLine2 = models.CharField(max_length=100, blank=True, null=True)
    City = models.CharField(max_length=50)
    State = models.CharField(max_length=50)
    Pincode = models.CharField(max_length=6)
    Landmark = models.CharField(max_length=100, blank=True, null=True)

    # Employment & Income
    EMPLOYMENT_CHOICES = [
        ('salaried', 'Salaried'),
        ('self-employed', 'Self-Employed'),
        ('business', 'Business'),
        ('retired', 'Retired'),
    ]
    EmploymentType = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES)
    MonthlyIncome = models.DecimalField(max_digits=10, decimal_places=2)
    CompanyName = models.CharField(max_length=100, blank=True, null=True)
    OfficeAddress = models.TextField(blank=True, null=True)

    # Bank Details
    BankName = models.CharField(max_length=100)
    AccountNumber = models.CharField(max_length=18)
    IFSC_Code = models.CharField(max_length=11)
    
    ACCOUNT_TYPE_CHOICES = [
        ('savings', 'Savings'),
        ('current', 'Current'),
        ('nre', 'NRE'),
        ('nro', 'NRO'),
    ]
    AccountType = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)

    # KYC Documents
    AadhaarNumber = models.CharField(max_length=12)
    PanNumber = models.CharField(max_length=10)
    AadhaarFront = models.FileField(upload_to='kyc_docs/')
    PanCardCopy = models.FileField(upload_to='kyc_docs/')
    CustomerPhoto = models.ImageField(upload_to='kyc_photos/')

    # Residence Info
    RESIDENCE_TYPE_CHOICES = [
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('leased', 'Leased'),
    ]
    ResidenceType = models.CharField(max_length=20, choices=RESIDENCE_TYPE_CHOICES, blank=True, null=True)
    ElectricityBill = models.FileField(upload_to='kyc_docs/', blank=True, null=True)

    # System Fields
    CreatedBy = models.CharField(max_length=50, blank=True, null=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)
    
    KYC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    KycStatus = models.CharField(max_length=10, choices=KYC_STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'customer'

    def __str__(self):
        return f"{self.CustomerId} - {self.FirstName} {self.LastName}"





CURRENT_YEAR = datetime.now().year
CURRENT_DATE = datetime.now().date()

# def validate_manufacture_year(value):
#     if value < 1990 or value > CURRENT_YEAR + 1:
#         raise ValidationError(f'Manufacture year must be between 1990 and {CURRENT_YEAR + 1}.')

from django.db import models

class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [('new', 'New'), ('used', 'Used')]
    FUEL_TYPE_CHOICES = [('petrol', 'Petrol'), ('diesel', 'Diesel'), ('electric', 'Electric')]
    INSURANCE_TYPE_CHOICES = [('comprehensive', 'Comprehensive'), ('third party', 'Third Party')]
    HP_STATUS_CHOICES = [('hypothecated', 'Hypothecated'), ('non-hypothecated', 'Non-Hypothecated')]
    RC_STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    
    VehicleType = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    RegistrationNumber = models.CharField(max_length=20, unique=True)
    OwnerName = models.CharField(max_length=100)
    ManufactureYear = models.IntegerField()
    RegistrationDate = models.DateField()
    Make = models.CharField(max_length=100)
    Model = models.CharField(max_length=100)
    Variant = models.CharField(max_length=100)
    FuelType = models.CharField(max_length=10, choices=FUEL_TYPE_CHOICES)
    EngineNumber = models.CharField(max_length=50, unique=True)
    ChassisNumber = models.CharField(max_length=50, unique=True)
    VehicleColor = models.CharField(max_length=50)
    RC_ExpiryDate = models.DateField()
    InvoiceAmount = models.DecimalField(max_digits=12, decimal_places=2)
    OnRoadPrice = models.DecimalField(max_digits=12, decimal_places=2)
    MarginMoney = models.DecimalField(max_digits=12, decimal_places=2)
    DealerName = models.CharField(max_length=100)
    DealerPan = models.CharField(max_length=10)
    InsuranceType = models.CharField(max_length=20, choices=INSURANCE_TYPE_CHOICES)
    InsuranceCompany = models.CharField(max_length=100)
    InsuranceNumber = models.CharField(max_length=50)
    InsuranceExpiry = models.DateField()
    IDV_Value = models.DecimalField(max_digits=12, decimal_places=2)
    HP_Status = models.CharField(max_length=20, choices=HP_STATUS_CHOICES)
    RC_Status = models.CharField(max_length=20, choices=RC_STATUS_CHOICES)
    LastVerifiedBy = models.CharField(max_length=100)
    LastVerifiedAt = models.DateTimeField(auto_now_add=True)

    # File fields
    RC_Copy = models.FileField(upload_to='vehicle_docs/', null=True, blank=True)
    InsuranceCopy = models.FileField(upload_to='vehicle_docs/', null=True, blank=True)
    InvoiceCopy = models.FileField(upload_to='vehicle_docs/', null=True, blank=True)
    FitnessCertificate = models.FileField(upload_to='vehicle_docs/', null=True, blank=True)

    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Vehicle'


    def clean(self):
        from django.core.exceptions import ValidationError

        if self.RegistrationDate < datetime(self.ManufactureYear, 1, 1).date():
            raise ValidationError("Registration date must be on or after the manufacture year start.")

        if self.RegistrationDate > datetime.now().date():
            raise ValidationError("Registration date cannot be in the future.")

        if self.RC_ExpiryDate < self.RegistrationDate:
            raise ValidationError("RC expiry date must be after registration date.")

        if self.MarginMoney and self.MarginMoney > 0.3 * self.OnRoadPrice:
            raise ValidationError("Margin money cannot exceed 30% of on-road price.")

        if self.IDV_Value > 0.9 * self.OnRoadPrice:
            raise ValidationError("IDV value cannot exceed 90% of on-road price.")

        if self.InsuranceExpiry < datetime.now().date():
            raise ValidationError("Insurance expiry must be in the future.")


# #---------------------------------------------------

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class InitiateSeizure(models.Model):
    Id = models.AutoField(primary_key=True)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication',on_delete=models.CASCADE,db_column='loan_id')
    SeizureReason = models.CharField(max_length=50, choices=[
        ("default", "Default"),
        ("fraud", "Fraud"),
        ("voluntary surrender", "Voluntary Surrender")
    ])
    InitiatedBy = models.ForeignKey('LoginAuth.User', on_delete=models.CASCADE)
    InitiatedDate = models.DateField(auto_now_add=True)
    LegalOrderCopy = models.FileField(upload_to='seizure/legal_orders/', max_length=255)
    BorrowerNotice = models.FileField(upload_to='seizure/notices/', max_length=255)
    Remarks = models.TextField(blank=True, max_length=500)

    def __str__(self):
        return f"Seizure for Loan {self.LoanId}"


    class Meta:
        db_table = 'InitiateSeizure'

#-------------------------------------------------------------------------

class AssignAgent(models.Model):
    Id = models.AutoField(primary_key=True)
    Seizure = models.ForeignKey(InitiateSeizure, on_delete=models.CASCADE)
    AssignmentDate = models.DateField()
    AgentAuthorization = models.FileField(upload_to='agent/authorizations/')
    ScheduledVisit = models.DateTimeField(blank=True, null=True)
    GPS_Location = models.CharField(max_length=100, blank=True, null=True)
    SitePhotosPre = models.ManyToManyField('SitePhoto', blank=True)
    def __str__(self):
        return f"Assignment for {self.AgentId} on {self.AssignmentDate}"
    class Meta:
        db_table = 'AssignAgent'
#-------------------------------------------------------------------------

class SitePhoto(models.Model):
    Image = models.ImageField(upload_to='agent/site_photos/')
    Timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Photo at {self.Timestamp}"
    class Meta:
        db_table = 'SitePhoto'

#-------------------------------------------------------------------------
class SeizureExecution(models.Model):
    Id = models.AutoField(primary_key=True)
    AssignAgentId = models.ForeignKey(AssignAgent, on_delete=models.CASCADE)
    ExecutionDate = models.DateField()
    Outcome = models.CharField(max_length=20, choices=[
        ("seized", "Seized"),
        ("failed", "Failed"),
        ("settled", "Settled")
    ])
    AssetType = models.CharField(max_length=50, blank=True, null=True)
    AssetDescription = models.TextField(blank=True, null=True)
    AssetPhotos = models.ManyToManyField('AssetPhoto', blank=True)
    PoliceFIR_Copy = models.FileField(upload_to='execution/police_firs/', blank=True, null=True)
    WitnessProof = models.FileField(upload_to='execution/witness_proofs/', blank=True, null=True)
    AssetLocation = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        db_table = 'SeizureExecution'   

class AssetPhoto(models.Model):
    Image = models.ImageField(upload_to='execution/asset_photos/')
    Timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'AssetPhoto'

#-------------------------------------------------------------------------
class AssignBroker(models.Model):
    Id = models.AutoField(primary_key=True)
    AssetId = models.ForeignKey(SeizureExecution, on_delete=models.CASCADE)
    BrokerId = models.ForeignKey(Broker, on_delete=models.CASCADE)
    BrokerAgreement = models.FileField(upload_to='broker/agreements/')
    AssignedDate = models.DateField()
    ExpectedSaleDate = models.DateField(blank=True, null=True)
    AssetVideo = models.FileField(upload_to='broker/asset_videos/', blank=True, null=True)
    BrokerCommission = models.DecimalField(max_digits=10, decimal_places=2)
    CommissionType = models.CharField(max_length=20, choices=[
        ("Percentage", "Percentage"),
        ("Fixed", "Fixed")
    ])
    class Meta:
        db_table = 'AssignBroker'
#-------------------------------------------------------------------------

class SaleExecution(models.Model):
    Id = models.AutoField(primary_key=True)
    AssignBrokerId = models.ForeignKey(AssignBroker, on_delete=models.CASCADE)
    SaleStatus = models.CharField(max_length=30, choices=[
        ("sold", "Sold"),
        ("returned", "Returned"),
        ("offer pending", "Offer Pending")
    ])
    SaleDate = models.DateField(blank=True, null=True)
    BuyerName = models.CharField(max_length=255, blank=True, null=True)
    SaleAmount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    SaleDeed = models.FileField(upload_to='sale/sale_deeds/', blank=True, null=True)
    BuyerKyc = models.FileField(upload_to='sale/buyer_kyc/', blank=True, null=True)
    PaymentProof = models.FileField(upload_to='sale/payment_proofs/', blank=True, null=True)

    class Meta:
        db_table = 'SaleExecution'

#-------------------------------------------------------------------------
class RecoveryClosure(models.Model):
    Id = models.AutoField(primary_key=True)
    Sale = models.ForeignKey(SaleExecution, on_delete=models.CASCADE)
    RecoveredAmount = models.DecimalField(max_digits=12, decimal_places=2)
    NodalApproval = models.FileField(upload_to='closure/nodal_approvals/')
    RecoveryMode = models.CharField(max_length=30, choices=[
        ("sale", "Sale"),
        ("settlement", "Settlement"),
        ("write-off", "Write-Off")
    ])
    ClosureStatus = models.CharField(max_length=30, choices=[
        ("closed", "Closed"),
        ("disposed", "Disposed"),
        ("returned", "Returned")
    ])
    AuditReport = models.FileField(upload_to='closure/audit_reports/', blank=True, null=True)
    class Meta:
        db_table = 'RecoveryClosure'

#-------------------------------------------------------------------------

class Collateral(models.Model):
    COLLATERAL_TYPES = [
        ("real estate", "Real Estate"),
        ("vehicle", "Vehicle"),
        ("financial", "Financial"),
        ("inventory", "Inventory"),
        ("machinery", "Machinery"),
        ("others", "Others"),
    ]
    COLLATERAL_STATUS = [
        ("active", "Active"),
        ("seized", "Seized"),
        ("liquidated", "Liquidated"),
        ("released", "Released"),
        ("in-process", "In-Process"),
    ]

    CollateralId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE)
    AssetId = models.ManyToManyField('SeizureExecution', db_table='collateral_asset_link')  
    CollateralType = models.CharField(max_length=20, choices=COLLATERAL_TYPES)
    CollateralStatus = models.CharField(max_length=20, choices=COLLATERAL_STATUS)

    OwnerName = models.CharField(max_length=100)
    OwnershipPercentage = models.DecimalField(max_digits=5, decimal_places=2)
    TitleDocNumber = models.CharField(
        max_length=30,
    )
    EncumbranceStatus = models.BooleanField()
    LienHolderDetails = models.JSONField(null=True, blank=True)

    CurrentValue = models.DecimalField(max_digits=12, decimal_places=2)
    ValuationDate = models.DateField()
    ValuerRegNumber = models.CharField(
        max_length=20,
    )
    InsurancePolicyNo = models.CharField(max_length=30, null=True, blank=True)

    CollateralScore = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    RiskFlag = models.BooleanField(default=False)

    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.RiskFlag = self.CollateralScore >= 8
        super().save(*args, **kwargs)

    class Meta:
        db_table = "collateral_master"

#-------------------------------------------------------------------------
class RealEstateCollateral(models.Model):
    CollateralId = models.OneToOneField(Collateral, on_delete=models.CASCADE, related_name="RealEstate")
    Latitude = models.DecimalField(max_digits=9, decimal_places=6)
    Longitude = models.DecimalField(max_digits=9, decimal_places=6)
    BuildingType = models.CharField(max_length=50)
    AreaSqft = models.DecimalField(max_digits=10, decimal_places=2)
    FireSafetyCert = models.BooleanField(default=False)

    class Meta:
        db_table = "RealEstateCollateral"

#-------------------------------------------------------------------------
class VehicleCollateral(models.Model):
    CollateralId = models.OneToOneField(Collateral, on_delete=models.CASCADE, related_name="Vehicle")
    VehicleRC_Number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$')]
    )
    EngineNumber = models.CharField(max_length=30)
    ChassisNumber = models.CharField(max_length=30)
    NCT_Status = models.CharField(
        max_length=20,
        choices=[("Pass", "Pass"), ("Fail", "Fail"), ("Not Applicable", "Not Applicable")]
    )

    class Meta:
        db_table = "VehicleCollateral"
#-------------------------------------------------------------------------

class FinancialCollateral(models.Model):
    CollateralId = models.OneToOneField(Collateral, on_delete=models.CASCADE, related_name="Financial")
    InstrumentType = models.CharField(max_length=50)
    Instrument_ISIN = models.CharField(max_length=20)
    InstitutionName = models.CharField(max_length=100)
    MaturityDate = models.DateField()
    HaircutPercentage = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = "FinancialCollateral"

#-------------------------------------------------------------------------
class CollateralDocuments(models.Model):
    CollateralId = models.OneToOneField(Collateral, on_delete=models.CASCADE, related_name="Documents")
    TitleDeedCopy = models.FileField(upload_to='collateral_docs/')
    ValuationReport = models.FileField(upload_to='collateral_docs/')
    InsuranceDocument = models.FileField(upload_to='collateral_docs/')
    SitePhotos = models.FileField(upload_to='collateral_docs/')

    class Meta:
        db_table = "CollateralDocuments"

class InventoryCollateral(models.Model):
    CollateralId = models.OneToOneField('Collateral', on_delete=models.CASCADE, related_name='Inventory')
    Description = models.TextField()
    Quantity = models.PositiveIntegerField()
    StorageLocation = models.CharField(max_length=255)

    class Meta:
        db_table = "inventory_collateral"


class MachineryCollateral(models.Model):
    CollateralId = models.OneToOneField('Collateral', on_delete=models.CASCADE, related_name='Machinery')
    MachineType = models.CharField(max_length=100)
    Manufacturer = models.CharField(max_length=100)
    PurchaseYear = models.PositiveIntegerField()

    class Meta:
        db_table = "machinery_collateral"


class OthersCollateral(models.Model):
    CollateralId = models.OneToOneField('Collateral', on_delete=models.CASCADE, related_name='Others')
    Description = models.TextField()
    SupportingDocuments = models.FileField(upload_to='collateral_docs/SupportingDocuments')

    class Meta:
        db_table = "others_collateral"


    
# Enums/Choices
PRODUCT_CATEGORIES = [
    ('housing', 'Housing'),
    ('auto', 'Auto'),
    ('personal', 'Personal'),
]

INTEREST_TYPES = [
    ('fixed', 'Fixed'),
    ('reducing', 'Reducing'),
    ('custom', 'Custom'),
]

INTEREST_BASIS = [
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('annual', 'Annual'),
]

CHARGE_TYPE = [
    ('fixed', 'Fixed'),
    ('percentage', '%'),
]

EMI_CALC_BASIS = [
    ('standard', 'Standard'),
    ('custom', 'Custom'),
]

REPAYMENT_MODES = [
    ('ecs', 'ECS'),
    ('nach', 'NACH'),
]

TOGGLE_CHOICES = [
    (True, 'Yes'),
    (False, 'No'),
]


# Core ProductId    Configuration
class LoanProductMaster(models.Model):
    ProductId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    ProductName = models.CharField(max_length=255)
    ProductCode = models.CharField(max_length=50, unique=True)
    ProductCategory = models.CharField(max_length=50, choices=PRODUCT_CATEGORIES)
    ActiveStatus = models.BooleanField(default=True)
    Description = models.TextField(blank=True, null=True)
    CreatedBy = models.CharField(max_length=100)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "LoanProductMaster"


# Interest Configuration
class InterestConfiguration(models.Model):
    ProductId = models.OneToOneField(LoanProductMaster, on_delete=models.CASCADE, related_name='interest_config')
    InterestType = models.CharField(max_length=20, choices=INTEREST_TYPES)
    BaseInterestRate = models.DecimalField(max_digits=5, decimal_places=2)
    MaxInterestRate = models.DecimalField(max_digits=5, decimal_places=2)
    InterestBasis = models.CharField(max_length=20, choices=INTEREST_BASIS)
    InterestFormula = models.TextField(blank=True, null=True)  # Required only if interest_type = Custom
    class Meta:
        db_table = "InterestConfiguration"


# Charges & Fees
class Charge(models.Model):
    ProductId = models.ForeignKey(LoanProductMaster, on_delete=models.CASCADE, related_name='charges')
    ChargeType = models.CharField(max_length=20, choices=CHARGE_TYPE)
    ChargeValue = models.DecimalField(max_digits=10, decimal_places=2)
    MinAmount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    MaxAmount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ChargeName = models.CharField(max_length=100)  # e.g., Processing Fee, Late Fee
    class Meta:
        db_table = "LoanProduct_Charge"



class Penalty(models.Model):
    ProductId = models.OneToOneField(LoanProductMaster, on_delete=models.CASCADE, related_name='penalty_config')
    LatePaymentFee = models.DecimalField(max_digits=10, decimal_places=2)
    BounceCharge = models.DecimalField(max_digits=10, decimal_places=2)
    ForeclosureAllowed = models.BooleanField(choices=TOGGLE_CHOICES)
    ForeclosureLockin = models.IntegerField(blank=True, null=True)
    ForeclosureFee = models.TextField(blank=True, null=True)  # Formula or plain fee
    class Meta:
        db_table = "Product_Penalty"
#-------------------------------------------------------------------------

# Tenure & Amount
class TenureAmount(models.Model):
    ProductId = models.OneToOneField(LoanProductMaster, on_delete=models.CASCADE, related_name='tenure_amount')
    MinTenureMonths = models.IntegerField()
    MaxTenureMonths = models.IntegerField()
    MinLoanAmount = models.DecimalField(max_digits=12, decimal_places=2)
    MaxLoanAmount = models.DecimalField(max_digits=12, decimal_places=2)
    AllowedRepaymentModes = models.JSONField()  # ["ECS", "NACH"]
    EMI_CalculationBasis = models.CharField(max_length=20, choices=EMI_CALC_BASIS)
    EMI_Formula = models.TextField(blank=True, null=True)  # Required if basis = Custom
    class Meta:
        db_table="LoanProduct_TenureAmount"
#-------------------------------------------------------------------------

# Business Rules
class BusinessRule(models.Model):
    ProductId = models.OneToOneField(LoanProductMaster, on_delete=models.CASCADE, related_name='business_rule')
    CO_ApplicantRequired = models.BooleanField(default=False)
    GuarantorRequired = models.BooleanField(default=False)
    EligibilityRule = models.TextField(blank=True, null=True)
    DocumentsRequired = models.JSONField()  # ["PAN", "Aadhaar", "Salary Slip"]
    class Meta:
        db_table="LoanProduct_BusinessRule"
#-------------------------------------------------------------------------

# UDF Mapping
class UDFMapping(models.Model):
    ProductId = models.ForeignKey(LoanProductMaster, on_delete=models.CASCADE, related_name='udf_mappings')
    UDF_Name = models.CharField(max_length=100)
    ShowIn = models.JSONField()  # ["Inquiry", "Application", "KYC"]
    UsedIn_EMI = models.BooleanField(default=False)
    class Meta:
        db_table="LoanProduct_UDFMapping"

#-------------------------------------------------------------------------


class Country(models.Model):
    code = models.CharField(max_length=5, unique=True)  # ISO country code like 'IN', 'US'
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'Country'
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return f"{self.name} ({self.code})"



class Currency(models.Model):
    code = models.CharField(max_length=5, unique=True)  # ISO currency code like 'INR', 'USD'
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    decimal_places = models.IntegerField(default=2)

    class Meta:
        db_table = 'Currency'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return f"{self.code} - {self.name}"





class LoanMasterstable(models.Model):
    customer_id = models.ForeignKey('Masters.Customer', on_delete=models.CASCADE)
    inquiry_id = models.ForeignKey('InquiryLoanProcess.NewInquiry', on_delete=models.CASCADE)
    loan_id = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE)
    owner_id = models.ForeignKey('LoginAuth.User', on_delete=models.CASCADE)
    disbursement_id = models.ForeignKey('DisSetSystem.Disbursement', on_delete=models.CASCADE)
    closure_id = models.ForeignKey('DisSetSystem.LoanClosure', on_delete=models.CASCADE)
    foreclosure_id = models.ForeignKey('DisSetSystem.LoanForeclosure', on_delete=models.CASCADE)
    renewal_id = models.ForeignKey('DisSetSystem.LoanRenewal', on_delete=models.CASCADE)
    collateral_id = models.ForeignKey('Masters.Collateral', on_delete=models.CASCADE)
    seizure_id = models.ForeignKey('Masters.InitiateSeizure', on_delete=models.CASCADE)
    auction_id = models.ForeignKey('Auction.AuctionSetup', on_delete=models.CASCADE)
    broker_id = models.ForeignKey('Masters.Broker', on_delete=models.CASCADE)
    CustomField = models.JSONField()
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'LoanMasterstable'



class LoanEMiCalculator(models.Model):
    loanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, verbose_name="LoanID")
    METHOD_CHOICES = [
        ('custom', 'Custom'),
        ('flat', 'Flat'),
        ('reducing', 'Reducing'),
        ('interest only','Interest Only'),
        ('ipp','IPP')
    ]
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    annualRate = models.DecimalField(max_digits=5, decimal_places=2)
    tenureMonths = models.PositiveIntegerField()
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    emi = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan #{self.id} - {self.principal} at {self.annual_rate}% for {self.tenure_months} months"

class LoanEMiSchedule(models.Model):
    EMiCalculator = models.ForeignKey(LoanEMiCalculator, on_delete=models.CASCADE, related_name='schedule')
    month = models.PositiveIntegerField()
    emi = models.DecimalField(max_digits=10, decimal_places=2)
    interest = models.DecimalField(max_digits=10, decimal_places=2)
    principal = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Loan #{self.loan.id} - Month {self.month}"




from django.db import models
import json

class LoanMasters(models.Model):
    Inquiry = models.JSONField(null=True, blank=True, default=None)
    LoanApplication = models.JSONField(null=True, blank=True, default=None)
    Disbursement = models.JSONField(null=True, blank=True, default=None)
    LoanClosure = models.JSONField(null=True, blank=True, default=None)
    LoanForeclosure = models.JSONField(null=True, blank=True, default=None)
    LoanRenewal = models.JSONField(null=True, blank=True, default=None)
    AuctionSetup = models.JSONField(null=True, blank=True, default=None)
    Customer = models.JSONField(null=True, blank=True, default=None)
    Broker = models.JSONField(null=True, blank=True, default=None)
    Collateral = models.JSONField(null=True, blank=True, default=None)
    InitiateSeizure = models.JSONField(null=True, blank=True, default=None)
    
    class Meta:
        verbose_name = "Loan Master"
        verbose_name_plural = "Loan Masters"

    def __str__(self):
        return f"LoanMaster {self.id}"