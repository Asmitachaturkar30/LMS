from django.db import models
from django.contrib.postgres.fields import JSONField


class CompanyProfile(models.Model):
    # --- General Information ---
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    CompanyName = models.CharField(max_length=255)
    AddressLine1 = models.CharField(max_length=255)
    AddressLine2 = models.CharField(max_length=255, blank=True, null=True)
    City = models.CharField(max_length=100)
    State = models.CharField(max_length=100)
    MobileNumber = models.CharField(max_length=20)
    Email = models.EmailField()
    CountryId = models.ForeignKey('Masters.Country', on_delete=models.SET_NULL, null=True, db_column='CountryId')
    CurrencyId = models.ForeignKey('Masters.Currency', on_delete=models.SET_NULL, null=True, db_column='CurrencyId')

    Logo = models.ImageField(upload_to='companyProfile/logo/', blank=True, null=True)
    UserProfileImage = models.ImageField(upload_to='company/profile/', blank=True, null=True)

    # --- Terms and Conditions ---
    TermsAndConditions = models.TextField(blank=True, null=True)
    CurrentPassword = models.CharField(max_length=128, blank=True, null=True)
    NewPassword = models.CharField(max_length=128, blank=True, null=True)
    ConfirmPassword = models.CharField(max_length=128, blank=True, null=True)

    # CreatedBy = models.CharField(max_length=150)
    UpdatedBy = models.CharField(max_length=150, blank=True, null=True)

    # --- Meta ---
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CompanyProfile'

