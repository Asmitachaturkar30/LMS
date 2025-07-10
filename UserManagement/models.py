from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('blocked', 'Blocked'),
]

class UserManagement(models.Model):
    Username = models.ForeignKey('LoginAuth.User',on_delete=models.CASCADE)
    Name = models.CharField(max_length=255) 
    Email = models.EmailField(unique=True)
    MobileNumber = models.CharField(max_length=15, unique=True)
    Branch = models.ForeignKey('Masters.Branch', on_delete=models.CASCADE,db_column='BranchId')
    Department = models.ForeignKey('Masters.Department', on_delete=models.CASCADE,db_column='DepartmentId')
    Designation = models.ForeignKey('Masters.Designation', on_delete=models.CASCADE,db_column='DesignationId')
    Role = models.CharField(max_length=100)
    ReportingManager = models.CharField(max_length=50)
    Password = models.CharField(max_length=255)
    CreateBy = models.CharField(max_length=50)
    UpdateBy = models.CharField(max_length=50)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    LastUpdatedAt = models.DateTimeField(auto_now=True)
    Status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.Username


    class Meta:
        db_table = 'UserManagement'