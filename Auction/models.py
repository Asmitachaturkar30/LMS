from django.db import models
# Create your models here.

class AuctionSetup(models.Model):
    AuctionId = models.AutoField(primary_key=True)
    LoanId = models.ForeignKey('InquiryLoanProcess.LoanApplication',on_delete=models.CASCADE,db_column='loan_id')
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    SeizureOrderCopy = models.FileField(upload_to='seizure_orders/')
    AuctionType = models.CharField(max_length=20, choices=[('online', 'Online'), ('offline', 'Offline'), ('broker-mediated', 'broker-mediated')])
    ReservePrice = models.DecimalField(max_digits=12, decimal_places=2)
    PlatformUrl = models.URLField(blank=True, null=True)  # Required only if auction_type == 'Online'

    #AssetValuation 
    AssetType = models.CharField(max_length=100)
    ValuationReport = models.FileField(upload_to='valuation_reports/')
    AssetPhotos = models.ImageField(upload_to='asset_photos/')
    InsurancePolicy = models.FileField(upload_to='insurance_policies/', blank=True, null=True)
    #BidManagement 
    BidderPanCard = models.FileField(upload_to='bid_docs/')
    BidderAadhaar = models.FileField(upload_to='bid_docs/')
    EMD_Receipt = models.FileField(upload_to='bid_docs/')
    BidDeclarationForm = models.FileField(upload_to='bid_docs/')
    #PostAuctionSettlement
    SaleDeed = models.FileField(upload_to='post_auction/')
    BuyerKycPackage = models.FileField(upload_to='post_auction/')
    PaymentProof = models.FileField(upload_to='post_auction/payment_proof/')
    HandoverReport = models.FileField(upload_to='post_auction/handover_report/')

    #ComplianceAudit
    RBI_AuctionReport = models.FileField(upload_to='compliance/rbi_auction_report/')
    AuditTrailLog = models.FileField(upload_to='compliance/')
    TDS_Certificate = models.FileField(upload_to='compliance/tds_certificate/', blank=True, null=True)


    def __str__(self):
        return str(self.auction_id)
    class Meta:
        db_table = 'AuctionSetup'
