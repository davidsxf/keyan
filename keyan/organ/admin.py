from django.contrib import admin
from .models import Organ, Department, Team, Staff

@admin.register(Organ)
class OrganAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'organ_type', 'contact_person', 'contact_phone')
    list_filter = ('organ_type',)
    search_fields = ('name', 'code', 'contact_person')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'organ', 'parent', 'director')
    list_filter = ('organ',)
    search_fields = ('name', 'code')
    raw_id_fields = ('parent', 'director')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'leader')
    list_filter = ('department__organ', 'department')
    search_fields = ('name', 'code')
    raw_id_fields = ('leader',)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'organ', 'department', 'title', 'phone', 'email', 'is_active']
    list_filter = ['organ', 'department', 'title', 'is_active']
    search_fields = ['name', 'phone', 'email']
    filter_horizontal = ['teams']
    raw_id_fields = ['user', 'organ', 'department']