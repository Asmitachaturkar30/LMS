from django.db import models
from django.conf import settings

class FollowUp(models.Model):
    InquiryId = models.ForeignKey(
        'InquiryLoanProcess.NewInquiry', on_delete=models.CASCADE, db_column='InquiryId')
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, db_column='loan_id')
    CustomerId = models.ForeignKey(
        'Masters.Customer',
        on_delete=models.CASCADE,
        db_column='Customer_Id',
        related_name='followUp_id')
    Name = models.CharField(max_length=150)
    Date = models.DateField(auto_now_add=True)
    Time = models.TimeField(auto_now_add=True)

    TYPE_CHOICES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('visit', 'Visit'),
        ('other', 'Other'),
    ]
    Type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    Subject = models.CharField(max_length=255)
    Description = models.TextField()
    AssignedTo = models.CharField(max_length=50, null=True, blank=True)
    CreateBy = models.CharField(max_length=50, null=True, blank=True)
    UpdateBy = models.CharField(max_length=50, null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'FollowUp'


class inquiryAction(models.Model):
    ACTION_CHOICES = [
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('assign', 'Assign'),
        ('add follow-up', 'Add Follow-up'),
        ('note', 'Note'),
        ('special note', 'Special Note'),
        ('verification', 'Verification'),
        ('checklist', 'Checklist'),
    ]
    Action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    InquiryId = models.ForeignKey(
        'InquiryLoanProcess.NewInquiry', on_delete=models.CASCADE, db_column='Inquiry_id')
    CreateBy = models.CharField(max_length=50, null=True, blank=True)
    UpdateBy = models.CharField(max_length=50, null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inquiryAction'


class Assign(models.Model):
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    InquiryId = models.ForeignKey(
        'InquiryLoanProcess.NewInquiry', on_delete=models.CASCADE, db_column='Inquiry_id')
    Users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    CreateBy = models.CharField(max_length=50, null=True, blank=True, db_column='CreateBy')
    UpdateBy = models.CharField(max_length=50, null=True, blank=True, db_column='UpdateBy')
    CreatedAt = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')
    LastUpdatedAt = models.DateTimeField(auto_now=True, db_column='LastUpdatedAt')

    class Meta:
        db_table = 'Assign'



class InquiryNote(models.Model):  # Capitalize class name (Python convention)
    InquiryId = models.ForeignKey(
        'InquiryLoanProcess.NewInquiry', on_delete=models.CASCADE, db_column='InquiryId')
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    Description = models.TextField()
    AssignedTo = models.CharField(max_length=50, null=True)
    CreateBy = models.CharField(max_length=50, null=True, blank=True, db_column='CreateBy')
    UpdateBy = models.CharField(max_length=50, null=True, blank=True, db_column='UpdateBy')
    CreatedAt = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')
    LastUpdatedAt = models.DateTimeField(auto_now=True, db_column='LastUpdatedAt')

    class Meta:
        db_table = 'inquiryNote'



class SpecialNote(models.Model):
    InquiryId = models.ForeignKey(
        'InquiryLoanProcess.NewInquiry', on_delete=models.CASCADE, db_column='Inquiry_id')
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    Description = models.TextField()
    AssignedTo = models.CharField(max_length=50,null=True)
    CreateBy = models.CharField(max_length=50, null=True, blank=True)
    UpdateBy = models.CharField(max_length=50, null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SpecialNote'




class Verification(models.Model):
    VERIFICATION_MODE_CHOICES = [
        ('on_site', 'On site Visit'),
        ('online', 'Online'),
    ]

    STATUS_CHOICES = [
        ('passed', 'Passed'),
        ('rejected', 'Rejected'),
        ('hold', 'Hold'),
    ]

    InquiryId = models.ForeignKey(
        'InquiryLoanProcess.NewInquiry', on_delete=models.CASCADE, db_column='InquiryId')
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    VerificationMode = models.CharField(max_length=20, choices=VERIFICATION_MODE_CHOICES)
    AssignTo = models.CharField(max_length=150)
    Remark = models.TextField(blank=True, null=True)
    VerificationStatus = models.CharField(max_length=20, choices=STATUS_CHOICES)
    VerificationDate = models.DateField(auto_now_add=True)
    CreateBy = models.CharField(max_length=50, null=True, blank=True)
    UpdateBy = models.CharField(max_length=50, null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Verification {self.id} - {self.NewInquiry_id}"


    class Meta:
        db_table = 'Verification'




# models.py
from django.db import models
# from django.contrib.auth.models import User

class DocumentUpload(models.Model):
    # Foreign keys to your existing models
    CustomerId = models.ForeignKey('Masters.Customer', on_delete=models.CASCADE, null=True, blank=True)
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, null=True, blank=True)
    InquiryId = models.ForeignKey('InquiryLoanProcess.NewInquiry', on_delete=models.CASCADE, null=True, blank=True)
    
    # File upload fields
    Worker = models.CharField(max_length=255, blank=True)
    
    # Metadata fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_uploads'
        
    def __str__(self):
        return f"DocumentUpload {self.id} - {self.title}"

class DocumentFile(models.Model):
    document_upload = models.ForeignKey(DocumentUpload, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_files'
        
    def __str__(self):
        return f"{self.original_filename} - {self.document_upload.id}"

