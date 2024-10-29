from django.contrib import admin

from .models import Project, Participantion,ProjectDoc
from import_export.admin import ImportExportModelAdmin

class ProjectAdmin(ImportExportModelAdmin):

    class Meta:
        model = Project

admin.site.register(Project,ProjectAdmin)
# admin.site.register(ProjectDoc)
admin.site.register(Participantion)

# Register your models here.
admin.site.site_header = '科研项目管理系统'
admin.site.site_title = '科研项目管理系统管理'
admin.site.index_title = '欢迎使用科研项目管理系统管理界面'