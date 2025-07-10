from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, role='user'):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password, role='admin')
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('user', 'User'),
)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')  
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class loginLogs(models.Model):
    ipAddress = models.GenericIPAddressField()
    email = models.EmailField()  # Add to link to the user/email
    createdAt = models.DateTimeField(auto_now_add=True)
    lastUpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loginLogs'

class OTPRequest(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f'OTP for {self.email} - {self.otp}'

class ModuleTable(models.Model):
    module_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_by = models.CharField(max_length=50, null=True, blank=True)
    update_by = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ModuleTable'

class ModuleLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ModuleLogs'

#----------------------------------------- Role Permissions ---------------------------

User = get_user_model()

# Enums for Choices
STATUS_CHOICES = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)
ACTION_CHOICES = (
    ('View', 'View'),  # Renamed 'Inquiry' to 'View' for clarity
    ('Create', 'Create'),
    ('Update', 'Update'),
    ('Delete', 'Delete'),
    ('Change Owner', 'Change Owner'),
    ('KYC', 'KYC'),
    ('Bulk Delete', 'Bulk Delete'),
    ('Import', 'Import'),
    ('Export', 'Export'),
    ('Approve', 'Approve'),
    ('Reject', 'Reject'),
    ('Initiate', 'Initiate'),
    ('Configure', 'Configure'),
)

# Models
class Modules(models.Model):
    module_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=500, blank=True)
    create_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="create_by_user")
    update_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="updated_by_user")
    # These are actual DB columns now
    createdByName = models.CharField(max_length=255, blank=True, null=True)
    updatedByName = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    roles = models.ManyToManyField('Role', through='ModuleRole')

    class Meta:
        db_table = 'Modules'
        ordering = ['module_name']

    def clean(self):
        if len(self.module_name.strip()) == 0:
            raise ValidationError({'module_name': 'Module name cannot be empty.'})
    def save(self, *args, **kwargs):
        # Auto-populate username fields
        if self.create_by:
            self.createdByName = self.create_by.username
        if self.update_by:
            self.updatedByName = self.update_by.username
        super().save(*args, **kwargs)


class ModuleRole(models.Model):
    module = models.ForeignKey(Modules, on_delete=models.CASCADE)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(default=timezone.now)
    assigned_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="assign_by_user")

    class Meta:
        unique_together = ('module', 'role')
        ordering = ['assigned_date']


class Role(models.Model):
    role_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    create_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="role_create_by_user")
    update_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="role_updated_by_user")
    # These are actual DB columns now
    createdByName = models.CharField(max_length=255, blank=True, null=True)
    updatedByName = models.CharField(max_length=255, blank=True, null=True)

    permissions = models.ManyToManyField('Permission', through='RolePermission')

    def clean(self):
        if len(self.role_name.strip()) == 0:
            raise ValidationError({'role_name': 'Role name cannot be empty.'})
    def save(self, *args, **kwargs):
        # Auto-populate username fields
        if self.create_by:
            self.createdByName = self.create_by.username
        if self.update_by:
            self.updatedByName = self.update_by.username
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_at']


class Permission(models.Model):
    permission_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    permission_name = models.CharField(max_length=50)
    module = models.ForeignKey(Modules, on_delete=models.PROTECT)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    create_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="permission_create_by_user")
    update_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="permission_updated_by_user")
    # These are actual DB columns now
    createdByName = models.CharField(max_length=255, blank=True, null=True)
    updatedByName = models.CharField(max_length=255, blank=True, null=True)

    def clean(self):
        if len(self.permission_name.strip()) == 0:
            raise ValidationError({'permission_name': 'Permission name cannot be empty.'})
        if self.module.module_name == 'Cross-Module' and self.action not in ['Change Owner', 'KYC', 'Export', 'View']:
            raise ValidationError({'action': 'Cross-Module actions limited to Change Owner, KYC, Export, View.'})
    def save(self, *args, **kwargs):
        # Auto-populate username fields
        if self.create_by:
            self.createdByName = self.create_by.username
        if self.update_by:
            self.updatedByName = self.update_by.username
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_at']
        unique_together = ('module', 'action')  # Ensure unique module-action pairs

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(default=timezone.now)
    assigned_by = models.ForeignKey(User,on_delete=models.CASCADE)
    class Meta:
        unique_together = ('role', 'permission')
        ordering = ['assigned_date']

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(default=timezone.now)
    assigned_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="userRole_assigned_by")

    class Meta:
        unique_together = ('user', 'role')
        ordering = ['assigned_date']

class AuditLog(models.Model):
    module = models.CharField(max_length=100)
    action = models.CharField(max_length=50)
    user_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.JSONField()

    class Meta:
        ordering = ['-timestamp']


#------------------------------  ApprocalMatrix ------------------

STATUS_CHOICES = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)
APPROVAL_STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
)

# Models (keep only one definition of each)
class ApprovalMatrix(models.Model): 
    matrix_id = models.CharField(max_length=100, primary_key=True, unique=True)
    module = models.ForeignKey('Modules', on_delete=models.CASCADE)
    matrix_name = models.CharField(max_length=100)
    approval_on_submit = models.BooleanField(default=False)
    levels = models.IntegerField()
    status = models.CharField(max_length=20, choices=(
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ), default='Active')
    autoEscalation_status = models.CharField(max_length=20, choices=(
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ), default='Active')
    created_date = models.DateTimeField(auto_now_add=True)
    autoEscalation = models.IntegerField(null=True, blank=True, help_text="Number of times to auto escalate if pending")
    onRejection = models.CharField(
        max_length=20,
        choices=(
            ('escalate', 'Escalate'),
            ('terminate', 'Terminate'),
        ),
        default='terminate'
    )
    created_by = models.ForeignKey('User', on_delete=models.CASCADE)
    # createdByName = models.CharField(max_length=255, blank=True, null=True)
    def clean(self):
        if not self.matrix_name.strip():
            raise ValidationError({'matrix_name': 'Matrix name cannot be empty.'})
        if not (1 <= self.levels <= 10):
            raise ValidationError({'levels': 'Levels must be between 1 and 10.'})

    class Meta:
        db_table = 'approval_matrix'
        indexes = [models.Index(fields=['module', 'status'])]
        constraints = [
            models.CheckConstraint(check=models.Q(levels__gte=1) & models.Q(levels__lte=5), name='levels_range')
        ]

class MatrixApprovers(models.Model):
    matrix_id = models.ForeignKey(ApprovalMatrix, on_delete=models.CASCADE, related_name='approvers')
    level = models.IntegerField()
    user_id = models.ForeignKey('User', on_delete=models.CASCADE, related_name="approver")
    UserByName = models.CharField(max_length=255, blank=True, null=True)
    # createdByName = models.CharField(max_length=255, blank=True, null=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey('User', on_delete=models.CASCADE)
    # assignedByName = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'matrix_approvers'
        unique_together = ('matrix_id', 'level')
        indexes = [models.Index(fields=['matrix_id'])]
        constraints = [
            models.CheckConstraint(check=models.Q(level__gte=1), name='level_positive')
        ]


class Approvals(models.Model):
    record_id = models.CharField(max_length=20)
    module = models.ForeignKey(Modules, on_delete=models.CASCADE)
    matrix_id = models.ForeignKey(ApprovalMatrix, on_delete=models.CASCADE)
    level = models.IntegerField()
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='Pending')
    approver_user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    # assignedByName = models.CharField(max_length=255, blank=True, null=True)

    action_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'approvals'
        unique_together = ('record_id', 'module', 'level')
        indexes = [models.Index(fields=['record_id', 'module'])]
        constraints = [
            models.CheckConstraint(check=models.Q(level__gte=1), name='approval_level_positive')
        ]