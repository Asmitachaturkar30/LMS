from django.db import models


class AuditLogs(models.Model):
    AUDIT_MODULE_CHOICES = [
        ('loan', 'Loan'),
        ('repayment', 'Repayment'),
        ('disbursement', 'Disbursement'),
        # Add more modules as needed
    ]

    AUDIT_ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    Module = models.CharField(max_length=50, choices=AUDIT_MODULE_CHOICES)
    ActionPerformed = models.CharField(max_length=10, choices=AUDIT_ACTION_CHOICES)
    UserID = models.CharField(max_length=150,blank=True,null=True)
    OldValue = models.JSONField(null=True, blank=True)
    NewValue = models.JSONField(null=True, blank=True)
    CreateBy = models.CharField(max_length=50, null=True, blank=True)
    UpdateBy = models.CharField(max_length=50, null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'AuditLogs'

    def __str__(self):
        return f"{self.module} - {self.action_performed} by {self.user}"
