
from django.db import models
from django.utils import timezone



class AadhaarVerificationLog(models.Model):
    aadhaar_number = models.CharField(max_length=12, unique=True)  # one record per Aadhaar
    request_count = models.IntegerField(default=0)                 # track how many times verified
    request_time = models.DateTimeField(auto_now=True)             # last request time
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    
    def __str__(self):
        return f"Aadhaar: {self.aadhaar_number} at {self.request_time} - Success: {self.success}"





class PANVerificationLog(models.Model):
    pan_number = models.CharField(max_length=10, unique=True)
    request_count = models.IntegerField(default=0)
    last_request_time = models.DateTimeField(auto_now=True)
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return self.pan_number




class DrivingLicenseVerificationLog(models.Model):
    license_number = models.CharField(max_length=20, unique=True)
    dob = models.DateField()
    request_count = models.IntegerField(default=1)
    last_request_time = models.DateTimeField(auto_now=True)
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.license_number} ({self.dob})"


class VoterIDVerificationLog(models.Model):
    voter_id_number = models.CharField(max_length=20, unique=True)
    request_count = models.IntegerField(default=1)
    last_request_time = models.DateTimeField(auto_now=True)
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return self.voter_id_number



class BankVerificationLog(models.Model):
    id_number = models.CharField(max_length=30)
    ifsc = models.CharField(max_length=20)
    ifsc_details = models.BooleanField(default=True)
    request_count = models.IntegerField(default=1)
    last_request_time = models.DateTimeField(auto_now=True)
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id_number} - {self.ifsc} - Success: {self.success}"


class ElectricityBillVerificationLog(models.Model):
    id_number = models.CharField(max_length=20)
    operator_code = models.CharField(max_length=10)
    request_count = models.IntegerField(default=0)
    last_request_time = models.DateTimeField(auto_now=True)
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id_number} ({self.operator_code}) - {self.last_request_time} - Success: {self.success}"


# models.py

class ITRVerificationLog(models.Model):
    client_id = models.CharField(max_length=100, unique=True)
    request_count = models.IntegerField(default=0)
    request_time = models.DateTimeField(auto_now=True)
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"ITR Client ID: {self.client_id} at {self.request_time} - Success: {self.success}"




class ITRComplianceLog(models.Model):
    pan_number = models.CharField(max_length=10, unique=True)
    request_count = models.IntegerField(default=0)
    request_time = models.DateTimeField(auto_now=True)
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"PAN: {self.pan_number} at {self.request_time} - Success: {self.success}"



class CreditReportCIBILLog(models.Model):
    mobile = models.CharField(max_length=15)
    request_count = models.IntegerField(default=1)
    last_request_time = models.DateTimeField(auto_now=True)
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mobile} - {self.pan} - {self.success}"




class CreditReportCIBILPDFLog(models.Model):
    mobile = models.CharField(max_length=15)
    request_count = models.IntegerField(default=1)
    last_request_time = models.DateTimeField(auto_now=True)
    response_status = models.IntegerField()
    response_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mobile} - {self.success}"


class DigiLockerLog(models.Model):
    full_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    user_email = models.EmailField()
    request_time = models.DateTimeField()
    response_status = models.IntegerField()
    response_message = models.TextField()
    success = models.BooleanField()




# your_app/models.py
from django.db import models
from django.utils import timezone
from Masters.models import *
from InquiryLoanProcess.models import *

from django.db import models
from Masters.models import Customer
from InquiryLoanProcess.models import NewInquiry, LoanApplication


# kyc_services/models.py

class KYCLog(models.Model):
    LOG_TYPE_CHOICES = [
        ('digilocker_initialize', 'DigiLocker Initialize'),
        ('digilocker_list', 'DigiLocker List'),
        ('aadhaar_verify', 'Aadhaar Verify'),
        ('pan_verify', 'PAN Verify'),
    ]
    log_type = models.CharField(max_length=50, choices=LOG_TYPE_CHOICES)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    loan = models.ForeignKey(LoanApplication, null=True, blank=True, on_delete=models.SET_NULL)
    inquiry = models.ForeignKey(NewInquiry, null=True, blank=True, on_delete=models.SET_NULL)

    kyc_service = models.CharField(max_length=100, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    token = models.TextField()
    payload = models.JSONField()
    response = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kyc_log"
