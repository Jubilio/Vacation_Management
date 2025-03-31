from django.contrib import admin
from .models import Employee, AuditLog

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract_date', 'position', 'department', 'accumulated_vacation_days')
    list_filter = ('department', 'position')
    search_fields = ('name', 'department')
    ordering = ('name',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'object_id')
    list_filter = ('user', 'action')
    search_fields = ('user', 'model_name', 'changes')
    ordering = ('-timestamp',)
