# apps/departments/admin.py
from django.contrib import admin
from .models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_leads')
    search_fields = ('name', 'lead__username')
    autocomplete_fields = ['lead', 'members']

    def get_leads(self, obj):
        return ", ".join([str(u) for u in obj.lead.all()])
    get_leads.short_description = 'Leads'