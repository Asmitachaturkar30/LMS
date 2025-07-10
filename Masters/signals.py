# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Branch, Department
# from django.contrib.auth import get_user_model

# User = get_user_model()

# @receiver(post_save, sender=User)
# def create_default_branch_and_department_for_admin(sender, instance, created, **kwargs):
#     if created and instance.role == 'admin':
#         # Step 1: Create Branch
#         branch, _ = Branch.objects.get_or_create(
#             email=f'{instance.username}@branch.com',
#             defaults={
#                 'name': f'{instance.username} Branch',
#                 'code': f'BR-{instance.id}',
#                 'address': 'Admin Default Address',
#                 'city': 'Admin City',
#                 'state': 'Admin State',
#                 'country': 'Admin Country',
#                 'mobile': 9999999999,
#                 'createBy': instance.username,
#                 'updateBy': instance.username,
#             }
#         )

#         # Step 2: Create Department with the new branch
#         Department.objects.get_or_create(
#             branchId=branch,
#             email=f'{instance.username}@department.com',
#             defaults={
#                 'name': 'Admin Main Department',
#                 'code': f'DEP-{instance.id}',
#                 'mobile': 9999999999,
#                 'create_by': instance.username,
#                 'update_by': instance.username,
#             }
#         )
