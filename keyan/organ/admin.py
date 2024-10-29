from django.contrib import admin
from .models import Org, Participant,Outsider,Department,Team,Employee,Student

from import_export.admin import ImportExportModelAdmin

# Register your models here.


class OrgAdmin(ImportExportModelAdmin):

    class Meta:
        model = Org


class OutsiderAdmin(ImportExportModelAdmin):

    class Meta:
        model = Outsider


class DepartmentAdmin(ImportExportModelAdmin):

    class Meta:
        model = Department


class TeamAdmin(ImportExportModelAdmin):

    class Meta:
        model = Team


class EmployeeAdmin(ImportExportModelAdmin):
    # 定制哪些字段需要展示

    class Meta:
        model = Employee


class OrgAdmin(ImportExportModelAdmin):

    search_fields = ['name']

    list_display = ('id', 'name')

    class Meta:
        model = Org


admin.site.register(Org, OrgAdmin)
admin.site.register(Outsider, OutsiderAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student)
