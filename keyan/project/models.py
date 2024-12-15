from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from organ.models import Organ, Staff

class Project(models.Model):
    PROJECT_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('suspended', '已暂停'),
        ('terminated', '已终止')
    ]
    
    STATUS_CHOICES = PROJECT_STATUS_CHOICES
    
    PROJECT_TYPES = [
        ('research', '研究项目'),
        ('development', '开发项目'),
        ('consulting', '咨询项目'),
        ('service', '服务项目'),
        ('other', '其他项目')
    ]

    name = models.CharField('项目名称', max_length=200)
    code = models.CharField('项目编号', max_length=50, unique=True)
    project_type = models.CharField('项目类型', max_length=20, choices=PROJECT_TYPES, default='research')
    description = models.TextField('项目描述', blank=True)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    budget = models.DecimalField('预算金额', max_digits=12, decimal_places=2, default=0)
    status = models.CharField('项目状态', max_length=20, choices=PROJECT_STATUS_CHOICES, default='draft')
    lead_organ = models.ForeignKey(Organ, on_delete=models.PROTECT, related_name='lead_projects', verbose_name='主导单位')
    partner_organs = models.ManyToManyField(Organ, related_name='partner_projects', blank=True, verbose_name='合作单位')
    manager = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name='managed_projects', verbose_name='项目负责人')
    participants = models.ManyToManyField(Staff, through='ProjectParticipation', related_name='participated_projects', verbose_name='项目成员')
    team_members = models.ManyToManyField(User, related_name='team_projects', blank=True, verbose_name='团队成员')
    remarks = models.TextField('备注', blank=True)
    is_archived = models.BooleanField('是否归档', default=False)
    archived_at = models.DateTimeField('归档时间', null=True, blank=True)
    archived_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='project_archived_projects', verbose_name='归档人')
    archive_reason = models.TextField('归档原因', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True,
                                 related_name='project_created_projects', verbose_name='创建人')

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def archive(self, user, reason=''):
        """归档项目"""
        self.is_archived = True
        self.archived_at = timezone.now()
        self.archived_by = user
        self.archive_reason = reason
        self.save()

    def unarchive(self):
        """取消归档"""
        self.is_archived = False
        self.archived_at = None
        self.archived_by = None
        self.archive_reason = ''
        self.save()

class ProjectParticipation(models.Model):
    ROLE_CHOICES = [
        ('manager', '项目负责人'),
        ('leader', '课题负责人'),
        ('member', '项目成员'),
        ('consultant', '顾问专家'),
        ('support', '支持人员')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name='人员')
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期', null=True, blank=True)
    workload = models.DecimalField('工作量（人月）', max_digits=5, decimal_places=2, null=True, blank=True)
    responsibility = models.TextField('工作职责', blank=True)
    performance = models.TextField('工作表现', blank=True)
    is_active = models.BooleanField('是否在项目中', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True,
                                 verbose_name='创建人')

    class Meta:
        verbose_name = '项目参与'
        verbose_name_plural = verbose_name
        unique_together = ['project', 'staff']

    def __str__(self):
        return f'{self.project.name} - {self.staff.name} ({self.get_role_display()})'
