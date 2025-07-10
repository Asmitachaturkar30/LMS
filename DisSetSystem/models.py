from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
from django.core.validators import MinValueValidator


class Disbursement(models.Model):
    DisbursementId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    Loan = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, verbose_name="LoanID")
    DisbursementDate = models.DateField("Disbursement Date", default=timezone.now)
    DisbursedAmount = models.DecimalField("Disbursed Amount", max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    MODE_CHOICES = [
        ('bank transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
    ]
    ModeOfTransfer = models.CharField("Mode of Transfer", max_length=20, choices=MODE_CHOICES)
    BankAccountNumber = models.CharField("Bank Account Number", max_length=20, blank=True, null=True)
    ChequeNumber = models.CharField("Cheque Number", max_length=20, blank=True, null=True)
    Remarks = models.TextField("Remarks", blank=True, null=True)
    CreateBy = models.CharField("CreateBy",max_length=50)
    UpdateBy = models.CharField("UpdateBy",max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)


    def clean(self):
        from django.core.exceptions import ValidationError
        # Conditional required fields based on mode_of_transfer
        if self.mode_of_transfer == 'Bank Transfer' and not self.bank_account_number:
            raise ValidationError({'bank_account_number': "Bank Account Number is required for Bank Transfer."})
        if self.mode_of_transfer == 'Cheque' and not self.cheque_number:
            raise ValidationError({'cheque_number': "Cheque Number is required for Cheque mode."})

    def __str__(self):
        return f"Disbursement {self.disbursement_id} - Loan {self.loan.id}"
    class Meta:
        db_table = 'Disbursement'

#============================= RepaymentSchedule  ================================

class RepaymentSchedule(models.Model):
    ScheduleId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, verbose_name="Loan ID")
    EMIAmount = models.DecimalField("EMI Amount", max_digits=10, decimal_places=2)
    DueDate = models.DateField("Due Date")
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    Status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES)
    PaidDate = models.DateField("Paid Date", blank=True, null=True)
    CreateBy = models.CharField("CreateBy",max_length=50)
    UpdateBy = models.CharField("UpdateBy",max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Repayment Schedule {self.ScheduleId} - Loan {self.Loan.id}"

    class Meta:
        db_table = 'RepaymentSchedule'

    def __str__(self):
        return f"Schedule {self.ScheduleId} for Loan {self.LoanId}"

    def save(self, *args, **kwargs):
        if self.Status == 'paid' and not self.PaidDate:
            from django.utils import timezone
            self.PaidDate = timezone.now().date()
        elif self.Status != 'paid':
            self.PaidDate = None
        super().save(*args, **kwargs)


class PaymentCollection(models.Model):
    CollectionId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, verbose_name="Loan ID")
    EMIId = models.ForeignKey('InquiryLoanProcess.EMISetup', on_delete=models.CASCADE, verbose_name="EMI ID")  
    CollectedAmount = models.DecimalField("Collected Amount", max_digits=10, decimal_places=2)
    PaymentDate = models.DateField("Payment Date")
    
    MODE_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('bank transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
    ]
    Mode = models.CharField("Mode", max_length=20, choices=MODE_CHOICES)
    ReceivedBy = models.TextField("Received By", blank=True, null=True)
    
    CreateBy = models.CharField("CreateBy", max_length=50)
    UpdateBy = models.CharField("UpdateBy", max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment Collection {self.CollectionId} - Loan {self.LoanId_id}"

    class Meta:
        db_table = 'PaymentCollection'



class LoanClosure(models.Model):
    ClosureId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, verbose_name="Loan ID")
    ClosureDate = models.DateField("Closure Date")
    CLOSURE_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('foreclosure', 'Foreclosure'),
        ('write-Off', 'Write-Off'),
    ]
    ClosureType = models.CharField("Closure Type", max_length=15, choices=CLOSURE_TYPE_CHOICES)
    Reason = models.TextField("Reason", blank=True, null=True)
    FinalPayment = models.DecimalField("Final Payment", max_digits=10, decimal_places=2, blank=True, null=True)

    CreateBy = models.CharField("CreateBy",max_length=50)
    UpdateBy = models.CharField("UpdateBy",max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.ClosureType in ['Foreclosure', 'WriteOff'] and not self.reason:
            raise ValidationError({'reason': "Reason is required for Write-Off or Foreclosure."})

    def __str__(self):
        return f"Loan Closure {self.ClosureId} - Loan {self.Loan.Id}"

    class Meta:
        db_table = 'LoanClosure'


class LoanForeclosure(models.Model):
    ForeclosureId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    Loan = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, verbose_name="Loan ID")
    RequestDate = models.DateField("Request Date")
    PenaltyAmount = models.DecimalField("Penalty Amount", max_digits=10, decimal_places=2, blank=True, null=True)
    FinalPayment = models.DecimalField("Final Payment", max_digits=10, decimal_places=2)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('closed', 'Closed'),
    ]
    Status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES)

    CreateBy = models.CharField("CreateBy", max_length=50)
    UpdateBy = models.CharField("UpdateBy", max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan Foreclosure {self.ForeclosureId} - Loan {self.Loan.id}"

    class Meta:
        db_table = 'LoanForeclosure'



class LoanRenewal(models.Model):
    RenewalId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    OldLoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, verbose_name="Old Loan ID")
    NewTenure = models.PositiveIntegerField("New Tenure")  # months
    NewInterestRate = models.DecimalField("New Interest Rate", max_digits=5, decimal_places=2, blank=True, null=True)
    Reason = models.TextField("Reason")
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    ApprovalStatus = models.CharField("Approval Status", max_length=10, choices=APPROVAL_STATUS_CHOICES)

    CreateBy = models.CharField("CreateBy",max_length=50)
    UpdateBy = models.CharField("UpdateBy",max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Loan Renewal {self.RenewalId} - Old Loan {self.OldLoan.id}"

    class Meta:
        db_table = 'LoanRenewal'



class AutoSquareOffReconciliation(models.Model):
    AdjustmentId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    loanId = models.ForeignKey('InquiryLoanProcess.LoanApplication', on_delete=models.CASCADE, verbose_name="LoanID")
    OverpaidAmount = models.DecimalField("Overpaid Amount", max_digits=10, decimal_places=2, blank=True, null=True)
    UnderpaidAmount = models.DecimalField("Underpaid Amount", max_digits=10, decimal_places=2, blank=True, null=True)
    AdjustmentDate = models.DateField("Adjustment Date", blank=True, null=True)
    Remarks = models.TextField("Remarks", blank=True, null=True)
    CreateBy = models.CharField("CreateBy",max_length=50)
    UpdateBy = models.CharField("UpdateBy",max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Adjustment {self.AdjustmentId} - Loan {self.loanId.id}"

    class Meta:
        db_table = 'AutoSquareOff'


class EMICollectionAdjustment(models.Model):
    PaymentId = models.AutoField(primary_key=True)
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    EMIId = models.ForeignKey('InquiryLoanProcess.EMISetup', on_delete=models.CASCADE, verbose_name="EMI ID",related_name='emi_collection_adjustments'
    )
    PaymentDate = models.DateField("Payment Date")
    AmountPaid = models.DecimalField("Amount Paid", max_digits=10, decimal_places=2)
    
    MODE_CHOICES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
    ]
    Mode = models.CharField("Mode", max_length=10, choices=MODE_CHOICES)
    
    ForwardedEMIId = models.ForeignKey(
        'RepaymentSchedule',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Forwarded EMI ID",
        related_name='forwarded_emi_collection_adjustments'
    )
    BouncingCharges = models.DecimalField(
        "Bouncing Charges",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    CreateBy = models.CharField("CreateBy", max_length=50)
    UpdateBy = models.CharField("UpdateBy", max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if hasattr(self.EMIId, 'EMIAmount') and self.AmountPaid > self.EMIId.EMIAmount:
            raise ValidationError({'AmountPaid': "Amount Paid cannot exceed EMI amount."})

    def __str__(self):
        return f"EMI Payment {self.PaymentId} - EMI {self.EMIId.ScheduleId}"

    class Meta:
        db_table = 'EMICollectionAdjustment'
