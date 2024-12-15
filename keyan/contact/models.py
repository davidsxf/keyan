from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from organ.models import Organ
from project.models import Project

class ContractType(models.Model):
    """合同类型"""
    name = models.CharField('类型名称', max_length=50)
    code = models.CharField('类型编码', max_length=20, unique=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '合同类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Contract(models.Model):
    """合同"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待审核'),
        ('active', '生效中'),
        ('completed', '已完成'),
        ('terminated', '已终止'),
    ]

    contract_number = models.CharField('合同编号', max_length=50, unique=True)
    title = models.CharField('合同标题', max_length=200)
    contract_type = models.ForeignKey(ContractType, on_delete=models.PROTECT, verbose_name='合同类型')
    
    # 关联项目
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name='关联项目')
    
    # 合同双方
    party_a = models.ForeignKey(Organ, on_delete=models.PROTECT, verbose_name='甲方', related_name='party_a_contracts')
    party_b = models.ForeignKey(Organ, on_delete=models.PROTECT, verbose_name='乙方', related_name='party_b_contracts')
    
    amount = models.DecimalField('合同金额', max_digits=12, decimal_places=2)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    
    content = models.TextField('合同内容', blank=True)
    attachment = models.FileField('附件', upload_to='contracts/', blank=True)
    
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    responsible_person = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='负责人')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    remarks = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '合同'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contract_number} - {self.title}"

class ContractEvent(models.Model):
    """合同事件记录"""
    EVENT_TYPES = [
        ('create', '创建'),
        ('update', '更新'),
        ('review', '审核'),
        ('complete', '完成'),
        ('terminate', '终止'),
    ]

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='合同')
    event_type = models.CharField('事件类型', max_length=20, choices=EVENT_TYPES)
    description = models.TextField('描述')
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='操作人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '合同事件'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contract.contract_number} - {self.get_event_type_display()}"
