from django.contrib import admin
from .models import Budget, Income, Expense

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('project', 'total_amount', 'get_used_amount', 'get_remaining_amount', 'created_by', 'created_at')
    list_filter = ('project__status', 'created_at')
    search_fields = ('project__name', 'project__code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('project', 'total_amount', 'created_by')
        }),
        ('预算分配', {
            'fields': (
                'equipment_amount', 'material_amount', 'test_amount',
                'fuel_amount', 'travel_amount', 'conference_amount',
                'international_amount', 'labor_amount', 'expert_amount',
                'other_amount', 'indirect_amount'
            )
        }),
        ('其他信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount', 'category', 'date', 'status', 'created_by')
    list_filter = ('status', 'category', 'date')
    search_fields = ('project__name', 'project__code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('project', 'amount', 'date', 'category', 'status')
        }),
        ('详细信息', {
            'fields': ('description', 'attachment', 'remarks')
        }),
        ('其他信息', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount', 'category', 'date', 'status', 'payee', 'created_by')
    list_filter = ('status', 'category', 'date')
    search_fields = ('project__name', 'project__code', 'description', 'payee')
    readonly_fields = ('created_at', 'updated_at', 'approve_date')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('project', 'budget', 'amount', 'date', 'category', 'status')
        }),
        ('支付信息', {
            'fields': ('payee', 'bank_account', 'bank_name')
        }),
        ('发票信息', {
            'fields': ('invoice_number', 'invoice_date', 'attachment')
        }),
        ('审批信息', {
            'fields': ('approver', 'approve_date', 'approve_remarks')
        }),
        ('其他信息', {
            'fields': ('description', 'remarks', 'created_by', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时
            obj.created_by = request.user
        if obj.status == 'approved' and not obj.approver:
            obj.approver = request.user
        super().save_model(request, obj, form, change)
