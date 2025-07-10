#am_urls.py
from django.urls import path
from .ApprovalMatrix import ApprovalMatrixViewSet, ApprovalsViewSet

approval_matrix_list = ApprovalMatrixViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
approval_matrix_detail = ApprovalMatrixViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
approval_matrix_add_approver = ApprovalMatrixViewSet.as_view({
    'post': 'add_approver'
})
approval_matrix_remove_approver = ApprovalMatrixViewSet.as_view({
    'delete': 'remove_approver'
})

approvals_list = ApprovalsViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
approvals_detail = ApprovalsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    # Approval Matrix
    path('approval-matrix/', approval_matrix_list, name='approval-matrix-list'),
    path('approval-matrix/<str:pk>/', approval_matrix_detail, name='approval-matrix-detail'),
    path('approval-matrix/<str:pk>/add_approver/', approval_matrix_add_approver, name='approval-matrix-add-approver'),
    path('approval-matrix/<str:pk>/remove_approver/', approval_matrix_remove_approver, name='approval-matrix-remove-approver'),

    # Approvals
    path('approvals/', approvals_list, name='approvals-list'),
    path('approvals/<int:pk>/', approvals_detail, name='approvals-detail'),
]