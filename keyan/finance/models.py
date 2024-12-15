from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from project.models import Project

class Budget(models.Model):
    """项目预算"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目',
                              related_name='project_budgets')
    total_amount = models.DecimalField('总预算', max_digits=12, decimal_places=2)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # 预算分配
    equipment_amount = models.DecimalField('设备费', max_digits=12, decimal_places=2, default=0)
    material_amount = models.DecimalField('材料费', max_digits=12, decimal_places=2, default=0)
    test_amount = models.DecimalField('测试化验加工费', max_digits=12, decimal_places=2, default=0)
    fuel_amount = models.DecimalField('燃料动力费', max_digits=12, decimal_places=2, default=0)
    travel_amount = models.DecimalField('差旅费', max_digits=12, decimal_places=2, default=0)
    conference_amount = models.DecimalField('会议费', max_digits=12, decimal_places=2, default=0)
    international_amount = models.DecimalField('国际合作交流费', max_digits=12, decimal_places=2, default=0)
    labor_amount = models.DecimalField('劳务费', max_digits=12, decimal_places=2, default=0)
    expert_amount = models.DecimalField('专家咨询费', max_digits=12, decimal_places=2, default=0)
    other_amount = models.DecimalField('其他费用', max_digits=12, decimal_places=2, default=0)
    indirect_amount = models.DecimalField('间接费用', max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                 verbose_name='创建人', related_name='created_budgets')
    
    class Meta:
        verbose_name = '项目预算'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - 预算"
    
    def get_used_amount(self):
        """获取已使用金额"""
        return sum(expense.amount for expense in self.expense_set.filter(status='approved'))
    get_used_amount.short_description = '已使用金额'
    
    def get_remaining_amount(self):
        """获取剩余金额"""
        return self.total_amount - self.get_used_amount()
    get_remaining_amount.short_description = '剩余金额'

class Income(models.Model):
    """项目收入"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
    ]
    
    CATEGORY_CHOICES = [
        ('funding', '项目拨款'),
        ('supplement', '追加经费'),
        ('other', '其他收入'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目')
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2)
    date = models.DateField('���入日期')
    category = models.CharField('收入类型', max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField('说明')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    attachment = models.FileField('附件', upload_to='finance/income/', blank=True)
    remarks = models.TextField('备注', blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                 verbose_name='创建人', related_name='created_incomes')
    
    class Meta:
        verbose_name = '项目收入'
        verbose_name_plural = verbose_name
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.project.name} - {self.get_category_display()} - {self.amount}"

class Expense(models.Model):
    """项目支出"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('cancelled', '已取消'),
    ]
    
    CATEGORY_CHOICES = [
        ('outfund', '外拨经费'),
        ('overall', '所统筹'),
        ('other', '其他支出'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目')
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, verbose_name='预算')
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2)
    date = models.DateField('支出日期')
    category = models.CharField('支出类型', max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField('说明')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    payee = models.CharField('收款人', max_length=100)
    bank_account = models.CharField('银行账号', max_length=50, blank=True)
    bank_name = models.CharField('开户行', max_length=100, blank=True)
    
    invoice_number = models.CharField('发票号', max_length=50, blank=True)
    invoice_date = models.DateField('发票日期', null=True, blank=True)
    attachment = models.FileField('附件', upload_to='finance/expense/', blank=True)
    
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                verbose_name='审批人', related_name='approved_expenses')
    approve_date = models.DateTimeField('审批时间', null=True, blank=True)
    approve_remarks = models.TextField('审批意见', blank=True)
    
    remarks = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                 verbose_name='创建人', related_name='created_expenses')
    
    class Meta:
        verbose_name = '项目支出'
        verbose_name_plural = verbose_name
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.project.name} - {self.get_category_display()} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if self.status == 'approved' and not self.approve_date:
            self.approve_date = timezone.now()
        super().save(*args, **kwargs)
