from django.contrib import admin
from .models import Holiday, VacationRequest, CompensatoryDay

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name',)

@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'duration', 'return_date', 'status', 'deduction_done')
    list_filter = ('status', 'deduction_done', 'start_date')
    search_fields = ('employee__name',)
    ordering = ('-start_date',)

@admin.register(CompensatoryDay)
class CompensatoryDayAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'used', 'used_date', 'note')
    list_filter = ('used', 'date')
    search_fields = ('employee__name',)
    ordering = ('-date',)
