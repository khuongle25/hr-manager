from django.contrib import admin
from .models import LeaveType, LeaveRequest, LeaveBalance

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_days_per_year')
    search_fields = ('name',)

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'department', 'leave_type', 'start_date', 'end_date',
        'status', 'approver', 'created_at'
    )
    list_filter = ('status', 'leave_type', 'department', 'created_at')
    search_fields = ('employee__username', 'employee__email', 'reason')
    date_hierarchy = 'start_date'
    autocomplete_fields = ['employee', 'department', 'leave_type', 'approver']

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'balance')
    search_fields = ('employee__username', 'leave_type__name')
    list_filter = ('leave_type',)