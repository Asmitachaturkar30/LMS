from venv import logger
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import uuid
import json
from .models import ApprovalMatrix, MatrixApprovers, Approvals, AuditLog, Modules,User

# ==================================Serializers========================================
class MatrixApproversSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    assigned_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = MatrixApprovers
        fields = ['level', 'user_id', 'assigned_date', 'assigned_by']
        read_only_fields = ['assigned_date']

    def validate(self, data):
        matrix_id = self.context.get('matrix_id')
        if matrix_id:
            try:
                matrix = ApprovalMatrix.objects.get(matrix_id=matrix_id)
                if data.get('level') > matrix.levels:
                    raise serializers.ValidationError(
                        {'level': f'Level exceeds matrix levels ({matrix.levels}).'}
                    )
            except ApprovalMatrix.DoesNotExist:
                raise serializers.ValidationError(
                    {'matrix_id': 'Approval matrix not found.'}
                )
        return data

class ApprovalMatrixSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Modules.objects.all())
    approvers = MatrixApproversSerializer(many=True, required=False)
    created_by = serializers.HiddenField(  # Changed this line
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = ApprovalMatrix
        fields = [
            'matrix_id', 'module', 'matrix_name', 'approval_on_submit', 
            'levels', 'status','autoEscalation_status', 'created_date', 'created_by', 'approvers',
            'autoEscalation', 'onRejection',
        ]
        read_only_fields = ['matrix_id', 'created_date']

    def validate_matrix_name(self, value):
        if len(value) > 100:  # Match the model's max_length
            raise serializers.ValidationError(
                "Matrix name cannot be longer than 100 characters."
            )
        return value

    def create(self, validated_data):
        validated_data.pop('created_by', None)
        approvers_data = validated_data.pop('approvers', [])
        
        # Generate a guaranteed short ID (8 chars from UUID + prefix = 13 chars total)
        validated_data['matrix_id'] = f'MX{uuid.uuid4().hex[:8].upper()}'
        
        user = self.context['request'].user
        if user.is_anonymous:
            raise serializers.ValidationError(
                {"error": "Authentication required to create matrix."}
            )
        
        try:
            matrix = ApprovalMatrix.objects.create(
                **validated_data,
                created_by=user
            )
            
            for approver_data in approvers_data:
                MatrixApprovers.objects.create(
                    matrix_id=matrix,
                    level=approver_data['level'],
                    user_id=approver_data['user_id'],
                    assigned_by=approver_data.get('assigned_by', user)
                )

            self._log_audit(matrix.module, 'Create', user.id, {
                'matrix_id': matrix.matrix_id,
                'matrix_name': matrix.matrix_name[:50]  # Truncate if needed
            })
            return matrix
        except Exception as e:
            raise serializers.ValidationError(
                {"error": f"Failed to create matrix: {str(e)}"}
            )

    def update(self, instance, validated_data):
        approvers_data = validated_data.pop('approvers', None)
        instance = super().update(instance, validated_data)

        if approvers_data is not None:
            instance.approvers.all().delete()
            for approver_data in approvers_data:
                MatrixApprovers.objects.create(
                    matrix_id=instance,
                    level=approver_data['level'],
                    user_id=approver_data['user_id'],
                    assigned_by=approver_data.get('assigned_by', instance.created_by)
                )

        self._log_audit(instance.module, 'Update', instance.created_by.id, 
                       {'matrix_id': instance.matrix_id})
        return instance

    def _log_audit(self, module, action, user_id, details):
        try:
            # Ensure all string values are within limits
            safe_details = {
                k: str(v)[:100] if isinstance(v, (str, int, float)) else v 
                for k, v in details.items()
            }
            
            AuditLog.objects.create(
                module=str(module)[:100],
                action=str(action)[:50],
                user_id=str(user_id)[:100],
                details=safe_details
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")




class ApprovalsSerializer(serializers.ModelSerializer):
    module = serializers.UUIDField()

    class Meta:
        model = Approvals
        fields = ['record_id', 'module', 'matrix_id', 'level', 'status', 'approver_user_id', 'action_date']
        read_only_fields = ['action_date']

    def validate(self, data):
        module_id = data.get('module')
        if not Modules.objects.filter(module_id=module_id).exists():
            raise serializers.ValidationError({'module': 'Invalid module.'})

        if not ApprovalMatrix.objects.filter(matrix_id=data['matrix_id']).exists():
            raise serializers.ValidationError({'matrix_id': 'Matrix does not exist.'})

        matrix = ApprovalMatrix.objects.get(matrix_id=data['matrix_id'])
        if data['level'] > matrix.levels:
            raise serializers.ValidationError({'level': f'Level exceeds matrix levels ({matrix.levels}).'})

        if not User.objects.filter(user_id=data['approver_user_id']).exists():
            raise serializers.ValidationError({'approver_user_id': 'User does not exist.'})

        return data

# ***********************************Views******************************************
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import *
from .serializers import *


class ApprovalMatrixViewSet(viewsets.ModelViewSet):
    queryset = ApprovalMatrix.objects.all().prefetch_related('approvers')
    serializer_class = ApprovalMatrixSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        module_id = self.request.query_params.get('module_id')
        status_val = self.request.query_params.get('status')
        if module_id:
            queryset = queryset.filter(module__module_id=module_id)
        if status_val:
            queryset = queryset.filter(status=status_val)
        return queryset

    @action(detail=True, methods=['post'])
    def add_approver(self, request, pk=None):
        matrix = self.get_object()
        serializer = MatrixApproversSerializer(
            data=request.data, 
            context={'matrix_id': pk, 'request': request}
        )
        if serializer.is_valid():
            serializer.save(matrix_id=matrix)
            self.get_serializer()._log_audit(
                matrix.module, 
                'Add Approver', 
                request.user.id, 
                {
                    'matrix_id': pk,
                    'level': serializer.validated_data['level']
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='remove_approver/')
    def remove_approver(self, request, pk=None):
        matrix = self.get_object()
        level = request.query_params.get('level')
        user_id = request.query_params.get('user_id')
        
        if not level or not user_id:
            return Response(
                {'error': 'Both level and user_id parameters are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            approver = MatrixApprovers.objects.get(
                matrix_id=pk, 
                level=level,
                user_id=user_id
            )
            approver.delete()
            self.get_serializer()._log_audit(
                matrix.module, 
                'Remove Approver', 
                request.user.id, 
                {
                    'matrix_id': pk,
                    'level': level,
                    'user_id': user_id
                }
            )
            return Response(
                {'message': 'Approver deleted successfully.'},
                status=status.HTTP_200_OK
                )
        except MatrixApprovers.DoesNotExist:
            return Response(
                {'error': 'Approver not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ApprovalsViewSet(viewsets.ModelViewSet):
    queryset = Approvals.objects.all()
    serializer_class = ApprovalsSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Approvals.objects.all()
        record_id = self.request.query_params.get('record_id')
        module_id = self.request.query_params.get('module_id')
        if record_id and module_id:
            queryset = queryset.filter(record_id=record_id, module__module_id=module_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(approver_user_id=self.request.user.user_id)
        self.get_serializer()._log_audit(
            module=serializer.validated_data['matrix_id'].module,
            action='Create',
            user_id=self.request.user.user_id,
            details={
                'record_id': serializer.validated_data['record_id'],
                'level': serializer.validated_data['level']
            }
        )

    def perform_update(self, serializer):
        serializer.save()
        self.get_serializer()._log_audit(
            module=serializer.validated_data['matrix_id'].module,
            action='Update',
            user_id=self.request.user.user_id,
            details={
                'record_id': serializer.validated_data['record_id'],
                'level': serializer.validated_data['level']
            }
        )

    def perform_destroy(self, instance):
        self.get_serializer(instance)._log_audit(
            module=instance.matrix_id.module,
            action='Delete',
            user_id=self.request.user.user_id,
            details={
                'record_id': instance.record_id,
                'level': instance.level
            }
        )
        instance.delete()