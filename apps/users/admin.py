from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'employee_id', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        ('HR Information', {'fields': ('role', 'employee_id', 'phone', 'address', 'date_of_birth', 'hire_date')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('HR Information', {'fields': ('role', 'employee_id', 'phone', 'address', 'date_of_birth', 'hire_date')}),
    )
