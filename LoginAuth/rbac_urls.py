from django.urls import path
from .RolesPermission import (
    ModuleViewSet,
    RoleViewSet,
    PermissionViewSet,
    # UserRoleViewSet
)

module_list = ModuleViewSet.as_view({'get': 'list', 'post': 'create'})
module_detail = ModuleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
module_add_role = ModuleViewSet.as_view({'post': 'add_role'})
module_remove_role = ModuleViewSet.as_view({'delete': 'remove_role'})

role_list = RoleViewSet.as_view({'get': 'list', 'post': 'create'})
role_detail = RoleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
role_add_permission = RoleViewSet.as_view({'post': 'add_permission'})
role_remove_permission = RoleViewSet.as_view({'delete': 'remove_permission'})
role_user_permissions = RoleViewSet.as_view({'get': 'user_modules_permissions'})

permission_list = PermissionViewSet.as_view({'get': 'list', 'post': 'create'})
permission_detail = PermissionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
permission_import = PermissionViewSet.as_view({'post': 'import_permissions'})
permission_export = PermissionViewSet.as_view({'get': 'export_permissions'})

# userrole_list = UserRoleViewSet.as_view({'get': 'list', 'post': 'create'})
# userrole_detail = UserRoleViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    # Modules
    path('modules/', module_list, name='module-list'),
    path('modules/<uuid:pk>/', module_detail, name='module-detail'),
    path('modules/<uuid:pk>/add_role/', module_add_role, name='module-add-role'),
    path('modules/<uuid:pk>/remove_role/', module_remove_role, name='module-remove-role'),

    # Roles
    path('roles/', role_list, name='role-list'),
    path('roles/<uuid:pk>/', role_detail, name='role-detail'),
    path('roles/<uuid:pk>/add_permission/', role_add_permission, name='role-add-permission'),
    path('roles/<uuid:pk>/remove_permission/', role_remove_permission, name='role-remove-permission'),
    path('roles/user_modules_permissions/', role_user_permissions, name='role-user-modules-permissions'),

    # Permissions
    path('permissions/', permission_list, name='permission-list'),
    path('permissions/<uuid:pk>/', permission_detail, name='permission-detail'),
    path('permissions/import_permissions/', permission_import, name='permission-import'),
    path('permissions/export_permissions/', permission_export, name='permission-export'),

    # # User Roles
    # path('userroles/', userrole_list, name='userrole-list'),
    # path('userroles/<int:pk>/', userrole_detail, name='userrole-detail'),
]