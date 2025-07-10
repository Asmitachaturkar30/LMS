from django.urls import path
from .views import (
    createAuditLog, updateAuditLog, deleteAuditLog,
    getAuditLog, getAllAuditLogs
)

urlpatterns = [
    path('createAuditLog/', createAuditLog),
    path('updateAuditLog/<int:pk>/', updateAuditLog),
    path('deleteAuditLog/<int:pk>/', deleteAuditLog),
    path('getAuditLog/<int:pk>/', getAuditLog),
    path('getAllAuditLogs/', getAllAuditLogs),
]
