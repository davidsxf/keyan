from django.contrib import admin
from .models import Project, ProjectParticipation

class ProjectParticipationInline(admin.TabularInline):
    model = ProjectParticipation
    extra = 1
    raw_id_fields = ('staff',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'project_type', 'lead_organ', 'manager', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'project_type', 'lead_organ')
    search_fields = ('name', 'code', 'description')
    raw_id_fields = ('manager', 'lead_organ')
    filter_horizontal = ('partner_organs',)
    inlines = [ProjectParticipationInline]
    date_hierarchy = 'start_date'

@admin.register(ProjectParticipation)
class ProjectParticipationAdmin(admin.ModelAdmin):
    list_display = ('project', 'staff', 'role', 'start_date', 'end_date', 'is_active', 'workload')
    list_filter = ('role', 'is_active', 'project', 'staff__department')
    search_fields = ('project__name', 'staff__name', 'responsibility')
    raw_id_fields = ('project', 'staff', 'created_by')
    date_hierarchy = 'start_date'

# 设置管理界面的标题
admin.site.site_header = '横向项目管理系统'
admin.site.site_title = '横向项目管理系统管理'
admin.site.index_title = '欢迎使用横向项目管理系统管理界面'