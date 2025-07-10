from django.db import models
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator


class NewInquiry(models.Model):
    # Personal Information
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')

    Date = models.DateField("Date")  # Date of inquiry

    FirstName = models.CharField(
        "First Name",
        max_length=50,
        validators=[RegexValidator(r'^[a-zA-Z]+$', message="Only alphabets allowed")]
    )
    MiddleName = models.CharField("Middle Name", max_length=50, blank=True, null=True)
    LastName = models.CharField("Last Name", max_length=50)

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    Gender = models.CharField("Gender", max_length=6, choices=GENDER_CHOICES)

    MaritalStatus = models.CharField("Marital Status", max_length=30, blank=True)  # dynamic dropdown

    DateOfBirth = models.DateField("Date of Birth")

    PhoneNumber = models.CharField(
        "Phone Number",
        max_length=15,
        validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10 digit phone number")]
    )
    AlternatePhoneNumber = models.CharField(
        "Alternate Phone Number",
        max_length=15,
        validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10 digit phone number")],
        blank=True, null=True
    )

    EmailAddress = models.EmailField("Email Address", max_length=100)

    FathersMothersName = models.CharField("Father's/Mother's Name", max_length=100)

    # KYC Basics
    PANNumber = models.CharField(
        "PAN Number",
        max_length=10,
        validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]$', message="Invalid PAN format")]
    )
    AadhaarNumber = models.CharField(
        "Aadhaar Number",
        max_length=12,
        unique=True,
        validators=[RegexValidator(r'^\d{12}$', message="Aadhaar must be 12 digits")]
    )

    # Address Details
    AddressLine1 = models.CharField("Address Line 1", max_length=255)
    AddressLine2 = models.CharField("Address Line 2", max_length=255, blank=True, null=True)
    City = models.CharField("City", max_length=100)
    State = models.CharField("State", max_length=100)
    Pincode = models.CharField(
        "Pincode",
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', message="Pincode must be 6 digits")]
    )
    Country = models.CharField("Country", max_length=50, default="India")
    Landmark = models.CharField("Landmark", max_length=255, blank=True, null=True)

    AddressType = models.CharField("Address Type", max_length=50, blank=True)  # dynamic dropdown
    DurationAtAddress = models.PositiveIntegerField("Duration at Address", blank=True, null=True)

    # Inquiry Information
    LoanPurpose = models.CharField("Loan Purpose", max_length=100)
    LoanAmountRequested = models.DecimalField(
        "Loan Amount Requested",
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(1000.00)]
    )
    Source = models.CharField("Source", max_length=50, blank=True)

    FollowUpNotes = models.TextField("Follow-up Notes", blank=True, null=True)

    INQUIRY_STATUS_CHOICES = [
        ('open', 'Open'),
        ('converted', 'Converted'),
        ('dropped', 'Dropped'),
    ]
    InquiryStatus = models.CharField(
        "Inquiry Status", max_length=9,
        choices=INQUIRY_STATUS_CHOICES, default='Open'
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        # Validate age ≥ 18
        if self.DateOfBirth:
            today = date.today()
            age = today.year - self.Date_of_Birth.year - ((today.month, today.day) < (self.DateOfBirth.month, self.DateOfBirth.day))
            if age < 18:
                raise ValidationError({'Date_of_Birth': "Applicant must be at least 18 years old."})

    def __str__(self):
        return f"{self.FirstName} {self.LastName} ({self.Date})"

    class Meta:
        db_table = 'NewInquiry'

REPAYMENT_FREQUENCY_CHOICES = [
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('yearly', 'Yearly'),
]

class LoanApplication(models.Model):
    # Personal Information (copied from Inquiry)
    FirstName = models.CharField("First Name", max_length=50)
    MiddleName = models.CharField("Middle Name", max_length=50, blank=True, null=True)
    LastName = models.CharField("Last Name", max_length=50)
    Gender = models.CharField("Gender", max_length=6, choices=NewInquiry.GENDER_CHOICES)
    MaritalStatus = models.CharField("Marital Status", max_length=30, blank=True)
    DateOfBirth = models.DateField("Date of Birth")
    PhoneNumber = models.CharField("Phone Number", max_length=15)
    AlternatePhoneNumber = models.CharField("Alternate Phone Number", max_length=15, blank=True, null=True)
    EmailAddress = models.EmailField("Email Address", max_length=100)
    FathersMothersName = models.CharField("Father's/Mother's Name", max_length=100)

    # Address Details (copied from Inquiry)
    AddressLine1 = models.CharField("Address Line 1", max_length=255)
    AddressLine2 = models.CharField("Address Line 2", max_length=255, blank=True, null=True)
    City = models.CharField("City", max_length=100)
    State = models.CharField("State", max_length=100)
    Pincode = models.CharField("Pincode", max_length=6)
    Country = models.CharField("Country", max_length=50, default="India")
    Landmark = models.CharField("Landmark", max_length=255, blank=True, null=True)
    AddressType = models.CharField("Address Type", max_length=50, blank=True)
    DurationAtAddress = models.PositiveIntegerField("Duration at Address", blank=True, null=True)

    # Employment Details
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')  
    ProductId = models.ForeignKey('Masters.LoanProductMaster',on_delete=models.CASCADE)
    InquiryId = models.ForeignKey(
        NewInquiry,
        on_delete=models.CASCADE,
        db_column='InquiryId',
        related_name='loan_applications'
    )
    EmploymentType = models.CharField(
        "Employment Type",
        max_length=50,
        choices=[('salaried', 'salaried'), ('self-employed', 'Self-employed')]
    )
    Occupation = models.CharField("Occupation", max_length=100)
    CompanyName = models.CharField("Company Name", max_length=100, blank=True, null=True)  # required if salaried

    IndustryType = models.CharField("Industry Type", max_length=50, blank=True)  # dynamic dropdown

    WorkExperience = models.PositiveIntegerField("Work Experience", blank=True, null=True)  # in years
    EmployerDuration = models.PositiveIntegerField("Employer Duration", blank=True, null=True)  # in years

    OfficeAddress = models.CharField("Office Address", max_length=255, blank=True, null=True)
    OfficePhoneNumber = models.CharField(
        "Office Phone Number",
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10 digit phone number")]
    )

    MonthlyIncome = models.DecimalField(
        "Monthly Income",
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    AnnualIncome = models.DecimalField(
        "Annual Income",
        max_digits=12, decimal_places=2,
        editable=False,
        null=True,
        blank=True,
        help_text="Auto-calculated as 12 x Monthly Income"
    )

    # Banking Information
    BankName = models.CharField("Bank Name", max_length=100)
    BranchName = models.CharField("Branch Name", max_length=100, blank=True, null=True)

    AccountNumber = models.CharField(
        "Account Number",
        max_length=20,
        validators=[RegexValidator(r'^\d+$', message="Account number must be numeric")]
    )
    IFSC_Code = models.CharField(
        "IFSC Code",
        max_length=11,
        validators=[RegexValidator(r'^[A-Z]{4}0[A-Z0-9]{6}$', message="Invalid IFSC Code format")]
    )
    ACCOUNT_TYPE_CHOICES = [
        ('saving', 'Saving'),
        ('current', 'Current'),
    ]
    AccountType = models.CharField("Account Type", max_length=7, choices=ACCOUNT_TYPE_CHOICES)

    # Loan Details
    LoanAmount = models.DecimalField("Loan Amount",max_digits=12,decimal_places=2,validators=[MinValueValidator(1000.0)])
    RateOfInterest = models.DecimalField("Rate of Interest (%)",max_digits=5,decimal_places=2,validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    Frequency = models.CharField("Repayment Frequency",max_length=20,choices=REPAYMENT_FREQUENCY_CHOICES)
    
    LoanTenure = models.PositiveIntegerField("Loan Tenure")  # in months
    RepaymentMode = models.CharField(
        "Repayment Mode",
        max_length=50,
        choices=[('ecs', 'ECS'), ('online', 'Online'), ('cash', 'Cash')]
    )

    CoApplicant = models.BooleanField("Co-Applicant", default=False, blank=True)
    GuarantorRequired = models.BooleanField("Guarantor Required", default=False, blank=True)

    APPLICATION_STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('KYC Pending', 'KYC Pending'),
        ('Waiting for Approval', 'Waiting for Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Hold', 'Hold'),
        ('Disbursement Pending', 'Disbursement Pending'),
        ('Disbursement Completed', 'Disbursement Completed'),
        ('Disbursement in Progress', 'Disbursement in Progress'),
    ]
    ApplicationStatus = models.CharField(
        max_length=50,
        choices=APPLICATION_STATUS_CHOICES,
        default='Draft'
    )

    LOAN_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
    ]
    LoanStatus = models.CharField(
        max_length=20,
        choices=LOAN_STATUS_CHOICES,
        default='Active'
    )

    # Guarantor Details
    GuarantorName = models.CharField("Guarantor Name", max_length=100, blank=True, null=True)
    GuarantorMobile = models.CharField(
        "Guarantor Mobile",
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10 digit phone number")]
    )
    GuarantorEmail = models.EmailField("Guarantor Email", max_length=100, blank=True, null=True)
    GuarantorAddress = models.CharField("Guarantor Address", max_length=255, blank=True, null=True)

    GuarantorPANNumber = models.CharField(
        "Guarantor PAN Number",
        max_length=10,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]$', message="Invalid PAN format")]
    )
    GuarantorAadhaarNumber = models.CharField(
        "Guarantor Aadhaar Number",
        max_length=12,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{12}$', message="Aadhaar must be 12 digits")]
    )

    GuarantorPANCardCopy = models.FileField("Guarantor PAN Card Copy", upload_to='guarantor_docs/pan/', blank=True, null=True)
    GuarantorAadhaarCardCopy = models.FileField("Guarantor Aadhaar Card Copy", upload_to='guarantor_docs/aadhaar/', blank=True, null=True)
    GuarantorBankStatement = models.FileField("Guarantor Bank Statement", upload_to='guarantor_docs/bank_statement/', blank=True, null=True)

    ExistingLoans = models.BooleanField("Existing Loans", default=False, blank=True)
    EMI_AmountExisting = models.DecimalField(
        "EMI Amount (Existing)",
        max_digits=12, decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)]
    )
    # InquiryLoanProcess/models.py

    DISBURSEMENT_TYPE_CHOICES = [
        ('Full', 'Full'),
        ('Partial', 'Partial'),
    ]

    DISBURSEMENT_MODE_CHOICES = [
        ('NEFT', 'NEFT'),
        ('Cheque', 'Cheque'),
        ('UPI', 'UPI'),
    ]

    DISBURSEMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    DisbursementType = models.CharField(
        max_length=10,
        choices=DISBURSEMENT_TYPE_CHOICES,
        blank=True,
        null=True
    )

    DisbursementMode = models.CharField(
        max_length=50,
        choices=DISBURSEMENT_MODE_CHOICES,
        blank=True,
        null=True
    )

    DisbursementDate = models.DateTimeField(
        blank=True,
        null=True
    )

    DisbursementStatus = models.CharField(
        max_length=10,
        choices=DISBURSEMENT_STATUS_CHOICES,
        default='Pending'
    )

    DisbursementNotes = models.TextField(
        blank=True,
        null=True
    )
    MoreAttachmentFile = models.FileField(
        upload_to='loan_attachments/', 
        blank=True, 
        null=True
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        # Company Name required if salaried
        if self.EmploymentType == 'Salaried' and not self.CompanyName:
            raise ValidationError({'CompanyName': "Company Name is required for salaried applicants."})

        # Guarantor details required if guarantor is required
        if self.GuarantorRequired:
            required_fields = ['GuarantorName', 'GuarantorMobile', 'GuarantorAddress', 'GuarantorPANNumber', 'GuarantorAadhaarNumber',
                               'GuarantorPANCardCopy', 'GuarantorAadhaarCardCopy', 'GuarantorBankStatement']
            missing = [field for field in required_fields if not getattr(self, field)]
            if missing:
                raise ValidationError({field: f"{field.replace('_', ' ')} is required when guarantor is required." for field in missing})

        # EMI Amount required if existing loans is True
        if self.ExistingLoans and (self.EMI_AmountExisting is None):
            raise ValidationError({'EMI_AmountExisting': "EMI Amount (Existing) is required if there are existing loans."})

    def save(self, *args, **kwargs):
        # Auto calculate Annual Income = 12 x Monthly Income
        if self.MonthlyIncome is not None:
            self.AnnualIncome = self.MonthlyIncome * 12
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan Application - {self.Occupation} ({self.EmploymentType})"


    class Meta:
        db_table = 'LoanApplication'


class LoanApplicationAttachment(models.Model):
    Loan = models.ForeignKey('LoanApplication', on_delete=models.CASCADE, related_name='attachments')
    File = models.FileField(upload_to='loan_attachments/')
    UploadedAt = models.DateTimeField(auto_now_add=True)



class Full_KYC(models.Model):
    DOCUMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    # Document Uploads
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    PANCard = models.FileField(upload_to='kyc_docs/pan/', null=True, blank=False)
    AadhaarCard = models.FileField(upload_to='kyc_docs/aadhaar/', null=True, blank=False)
    SalarySlips = models.FileField(upload_to='kyc_docs/salary_slips/', null=True, blank=True, help_text='Required if salaried')
    BankStatement = models.FileField(upload_to='kyc_docs/bank_statements/', null=True, blank=False)
    ItrDocs = models.FileField(upload_to='kyc_docs/itr/', null=True, blank=True, help_text='Required if self-employed')
    OtherIncomeProof = models.FileField(upload_to='kyc_docs/other_income/', null=True, blank=True)
    # Additional Documents
    DrivingLicense = models.FileField(upload_to='kyc_docs/driving_license/', null=True, blank=True)
    VoterId = models.FileField(upload_to='kyc_docs/voter_id/', null=True, blank=True)
    ElectricityBill = models.FileField(upload_to='kyc_docs/electricity_bill/', null=True, blank=True)
    ITRCompliance = models.FileField(upload_to='kyc_docs/itr_compliance/', null=True, blank=True)
    ReportCibil = models.FileField(upload_to='kyc_docs/credit_report/', null=True, blank=True)
    Digilocker = models.FileField(upload_to='kyc_docs/digilocker/', null=True, blank=True)

    # Document Status Fields
    PANStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    AadhaarStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    SalarySlipsStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    BankStatementStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    ItrDocsStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    OtherIncomeProofStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    DrivingLicenseStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    VoterIdStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    ElectricityBillStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    ITRComplianceStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    ReportCibilStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    DigilockerStatus = models.CharField(max_length=10, choices=DOCUMENT_STATUS_CHOICES, default='pending')

    # KYC Status Enum
    KYC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    KYCStatus = models.CharField(max_length=10, choices=KYC_STATUS_CHOICES, default='Pending')

    CreateBy = models.CharField(max_length=50)
    UpdateBy = models.CharField(max_length=50)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Full KYC - {self.id}"

    class Meta:
        db_table = 'Full_KYC'

#-------------------------------------------------------------------------------------------
class ApprovalInfo(models.Model):
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    ApprovedAmount = models.DecimalField(max_digits=12, decimal_places=2)  # Required In ₹
    ApprovalStatus = models.CharField(max_length=10, choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('hold', 'Hold')], default='Hold')
    ApprovalRemarks = models.TextField(blank=True, null=True)  # Internal notes (Optional)
    CreateBy = models.CharField(max_length=50,blank=True, null=True)
    UpdateBy = models.CharField(max_length=50,blank=True, null=True)  
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ApprovalInfo'

#-------------------------------------------------------------------------------------------
class DisbursementInfo(models.Model):
    # application = models.ForeignKey('LoanApplicationDetails', on_delete=models.CASCADE)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    DisbursementType = models.CharField(max_length=20, choices=[('full', 'Full'),
                                                                 ('partial', 'Partial')], default='Full')  # ENUM: Full / Partial

    DisbursementMode = models.CharField(max_length=50, choices=[('neft', 'NEFT'), 
                                                                 ('cheque', 'Cheque'),
                                                                 ('upi', 'UPI')])  # VARCHAR(50): NEFT / Cheque / UPI
    DisbursementDate = models.DateTimeField()
    DisbursementStatus = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='Pending')
    Notes = models.TextField(blank=True, null=True)  # Optional
    CreateBy = models.CharField(max_length=50)
    UpdateBy = models.CharField(max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'DisbursementInfo'
#-------------------------------------------------------------------------------------------

class EMISetup(models.Model):
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, db_column='loan_id')
    EMI_Amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    StartDate = models.DateField(null=True, blank=True)
    TotalTenure = models.IntegerField(null=True, blank=True)
    RemainingEMIS = models.IntegerField(null=True, blank=True)
    PaidEMIS = models.IntegerField(null=True, blank=True)
    AutoDebitEnabled = models.BooleanField(default=False)
    CreateBy = models.CharField(max_length=50, null=True, blank=True)
    UpdateBy = models.CharField(max_length=50, null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'EMISetup'
#-------------------------------------------------------------------------------------------

class Penalty(models.Model):
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    BouncedCharges = models.DecimalField(max_digits=12, decimal_places=2)
    LatePaymentPenalty = models.DecimalField(max_digits=12, decimal_places=2)
    PenaltyStatus = models.CharField(max_length=20, choices=[('unpaid', 'Unpaid'), ('paid', 'Paid')], default='Unpaid')
    CreateBy = models.CharField(max_length=50)
    UpdateBy = models.CharField(max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'Penalty'

#-------------------------------------------------------------------------------------------
class Foreclosure(models.Model):
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    Requested = models.BooleanField(default=False)
    Penalty = models.DecimalField(max_digits=12, decimal_places=2)
    Status = models.CharField(max_length=30)
    CreateBy = models.CharField(max_length=50)
    UpdateBy = models.CharField(max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'Foreclosure'

#-------------------------------------------------------------------------------------------


