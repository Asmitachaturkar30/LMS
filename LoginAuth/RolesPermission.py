# views.py (full updated with module + permissions handling during Role creation)

import uuid
import io
import csv
import pandas as pd
from django.utils import timezone
from django.http import HttpResponse
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

# Serializers

class ModulePermissionInputSerializer(serializers.Serializer):
    module_id = serializers.UUIDField()
    actions = serializers.ListField(child=serializers.ChoiceField(choices=ACTION_CHOICES))

class ModuleRoleSerializer(serializers.ModelSerializer):
    role_id = serializers.UUIDField()
    assigned_date = serializers.DateTimeField()
    assigned_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ModuleRole
        fields = ['role_id', 'assigned_date', 'assigned_by']

    def validate_role_id(self, value):
        if not Role.objects.filter(role_id=value).exists():
            raise serializers.ValidationError("Role does not exist.")
        return value

class ModuleSerializer(serializers.ModelSerializer):
    roles = ModuleRoleSerializer(many=True, required=False, source='modulerole_set')

    # Read-only: shows the username (not editable dropdowns)
    createdByName = serializers.CharField(source='create_by.username', read_only=True)
    updatedByName = serializers.CharField(source='update_by.username', read_only=True)

    class Meta:
        model = Modules
        fields = [
            'module_id', 'module_name', 'description',
            'created_at', 'last_updated_at',
            'create_by', 'update_by',
            'createdByName', 'updatedByName',
            'roles'
        ]
        read_only_fields = ['created_at', 'last_updated_at', 'createdByName', 'updatedByName']


class RolePermissionSerializer(serializers.ModelSerializer):
    permission_id = serializers.UUIDField()
    assigned_date = serializers.DateTimeField()
    assigned_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = RolePermission
        fields = ['permission_id', 'assigned_date', 'assigned_by']

    def validate_permission_id(self, value):
        if not Permission.objects.filter(permission_id=value).exists():
            raise serializers.ValidationError("Permission does not exist.")
        return value


class RoleSerializer(serializers.ModelSerializer):
    # Write-only field for incoming data
    modules_permissions = ModulePermissionInputSerializer(many=True, write_only=True)

    # Read-only computed field for output
    modules_permissions_response = serializers.SerializerMethodField(read_only=True)
    # Read-only: shows the username (not editable dropdowns)
    createdByName = serializers.CharField(source='create_by.username', read_only=True)
    updatedByName = serializers.CharField(source='update_by.username', read_only=True)

    class Meta:
        model = Role
        fields = [
            'role_id', 'role_name', 'description', 'status',
            'created_at', 'last_updated_at', 'create_by', 'update_by','createdByName', 'updatedByName',
            'modules_permissions', 'modules_permissions_response'
        ]
        read_only_fields = ['created_at', 'last_updated_at']

    def create(self, validated_data):
        modules_permissions = validated_data.pop('modules_permissions', [])
        role = Role.objects.create(**validated_data)

        for mp in modules_permissions:
            module_id = mp['module_id']
            actions = mp['actions']
            module = Modules.objects.get(module_id=module_id)

            ModuleRole.objects.get_or_create(
                role=role,
                module=module,
                defaults={
                    'assigned_by': validated_data.get('create_by'),
                    'assigned_date': timezone.now()
                }
            )

            for action in actions:
                create_by_user = validated_data.get('create_by')
                permission, _ = Permission.objects.get_or_create(
                    module=module,
                    action=action,
                    defaults={
                        'permission_id': uuid.uuid4(),
                        'permission_name': f"{module.module_name} - {action}",
                        'description': f"{action} access to {module.module_name}",
                        'status': 'Active',
                        'create_by': validated_data.get('create_by'),
                        'update_by': validated_data.get('create_by'),
                        'createdByName': create_by_user.username if create_by_user else '',
                        'updatedByName': create_by_user.username if create_by_user else ''
                    }
                )

                RolePermission.objects.get_or_create(
                    role=role,
                    permission=permission,
                    defaults={
                        'assigned_by': validated_data.get('create_by'),
                        'assigned_date': timezone.now()
                    }
                )

        AuditLog.objects.create(
            module='Role',
            action='Create',
            user_id=str(validated_data.get('create_by', 'system')),
            details={'role_id': str(role.role_id)}
        )
        return role

    def update(self, instance, validated_data):
        modules_permissions_data = validated_data.pop('modules_permissions', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.permissions.clear()
        instance.modulerole_set.all().delete()

        for entry in modules_permissions_data:
            module = Modules.objects.get(module_id=entry['module_id'])

            ModuleRole.objects.get_or_create(
                role=instance,
                module=module,
                defaults={'assigned_by': validated_data.get('update_by')}
            )

            for action in entry['actions']:
                create_by_user = validated_data.get('create_by')
                permission, _ = Permission.objects.get_or_create(
                    module=module,
                    action=action,
                    defaults={
                        'permission_id': uuid.uuid4(),
                        'permission_name': f"{module.module_name} - {action}",
                        'description': f"{action} access to {module.module_name}",
                        'status': 'Active',
                        'create_by': validated_data.get('create_by'),
                        'update_by': validated_data.get('create_by'),
                        'createdByName': create_by_user.username if create_by_user else '',
                        'updatedByName': create_by_user.username if create_by_user else ''
                    }
                )

                RolePermission.objects.get_or_create(
                    role=instance,
                    permission=permission,
                    defaults={
                        'assigned_by': validated_data.get('create_by'),
                        'assigned_date': timezone.now()
                    }
                )

        self._log_audit('Roles', 'Update', validated_data.get('update_by', instance.create_by), {'role_id': str(instance.role_id)})
        return instance

    def get_modules_permissions_response(self, obj):
        """
        Build the custom response format: list of {module_id, actions[]}
        """
        permissions = Permission.objects.filter(rolepermission__role=obj).select_related('module')
        module_map = {}
        for perm in permissions:
            mod_id = str(perm.module.module_id)
            if mod_id not in module_map:
                module_map[mod_id] = {
                    'module_id': mod_id,
                    'actions': []
                }
            module_map[mod_id]['actions'].append(perm.action)
        return list(module_map.values())

    def _log_audit(self, module, action, user_id, details):
        AuditLog.objects.create(module=module, action=action, user_id=user_id or 'system', details=details)


class PermissionSerializer(serializers.ModelSerializer):
    # Read-only: shows the username (not editable dropdowns)
    createdByName = serializers.CharField(source='create_by.username', read_only=True)
    updatedByName = serializers.CharField(source='update_by.username', read_only=True)

    class Meta:
        model = Permission
        fields = '__all__'

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        AuditLog.objects.create(
            module='Role',
            action='Delete',
            user_id=str(request.user.id),
            details={'role_id': str(instance.role_id)}
        )
        return super().destroy(request, *args, **kwargs)

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Modules.objects.all()
    serializer_class = ModuleSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    @action(detail=False, methods=['post'])
    def import_permissions(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                module = Modules.objects.get(module_name=row['module'])

                # Get user and username
                user = request.user
                username = user.username if user else ''

                Permission.objects.update_or_create(
                    module=module,
                    action=row['action'],
                    defaults={
                        'permission_name': row['permission_name'],
                        'description': row.get('description', ''),
                        'status': row.get('status', 'Active'),
                        'create_by': user,
                        'update_by': user,
                        'createdByName': username,
                        'updatedByName': username
                    }
                )

            return Response({'message': 'Permissions imported successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'])
    def export_permissions(self, request):
        permissions = Permission.objects.all().select_related('module')
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['permission_id', 'permission_name', 'module', 'action', 'description', 'status'])
        writer.writeheader()
        for perm in permissions:
            writer.writerow({
                'permission_id': perm.permission_id,
                'permission_name': perm.permission_name,
                'module': perm.module.module_name,
                'action': perm.action,
                'description': perm.description,
                'status': perm.status
            })
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="permissions.csv"'
        return response