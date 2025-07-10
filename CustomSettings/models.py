from django.db import models

FIELD_TYPE_CHOICES = [
    ('dropdown', 'Dropdown'),
    ('checkbox', 'Checkbox'),
    ('input_text', 'Input Text'),
    ('text_area', 'Text Area'),
    ('radio_button', 'Radio Button'),
    ('date', 'Date'),
    ('enum', 'Enum'),
    ('time', 'Time'),
    ('file_upload', 'File Upload'),
    ('img_upload', 'Img Upload'),
    ('video_upload', 'Video Upload'),
]

class CustomSetting(models.Model):
    ModuleId = models.ForeignKey(
        'LoginAuth.ModuleTable', on_delete=models.CASCADE, db_column='moduleId'
    )
    OwnerId = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    BranchId = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE, db_column='BranchId')
    DepartmentId = models.ForeignKey('Masters.Department', on_delete=models.CASCADE, db_column='DepartmentId')
    UDF_ID = models.CharField(max_length=100)
    FieldLabelName = models.CharField(max_length=255)
    IsMandatory = models.BooleanField(default=False)
    Type = models.CharField(max_length=50, choices=FIELD_TYPE_CHOICES)
    IsVisible = models.BooleanField(default=True)
    CreateBy = models.CharField(max_length=50, null=True, blank=True)
    UpdateBy = models.CharField(max_length=50, null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custom_setting'
        unique_together = ('ModuleId', 'UDF_ID', 'FieldLabelName')

    def __str__(self):
        return f"{self.ModuleId} - {self.UDF_ID} - {self.FieldLabelName}"
