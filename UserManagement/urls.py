# UserManagement/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('createUser/', createUser, name='user-create'),
    path('updateUser/<int:pk>/', updateUser, name='user-update'),
    path('deleteUser/<int:pk>/', deleteUser, name='user-delete'),
    path('getUserById/<int:pk>/', getUserById, name='user-detail'),
    path('viewAllUser/', viewAllUser, name='user-list'),
]
