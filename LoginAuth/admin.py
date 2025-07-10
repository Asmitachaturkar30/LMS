from django.contrib import admin
from .models import Modules,Role,Permission

@admin.register(Modules)
class ModulesAdmin(admin.ModelAdmin):
    readonly_fields = ['createdByName', 'updatedByName']  # Make them readonly in admin
    list_display = ['module_name', 'createdByName', 'updatedByName']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    readonly_fields = ['createdByName', 'updatedByName']



@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    readonly_fields = ['createdByName', 'updatedByName']
