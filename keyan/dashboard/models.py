from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    PROJECT_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('suspended', '已暂停'),
        ('terminated', '已终止')
    ]

    name = models.CharField('项目名称', max_length=200)
    code = models.CharField('项目编号', max_length=50, unique=True)
    description = models.TextField('项目描述', blank=True)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    status = models.CharField('项目状态', max_length=20, choices=PROJECT_STATUS_CHOICES, default='draft')
    is_archived = models.BooleanField('是否归档', default=False)
    archived_at = models.DateTimeField('归档时间', null=True, blank=True)
    archived_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='dashboard_archived_projects', verbose_name='归档人')
    archive_reason = models.TextField('归档原因', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, 
                                 related_name='dashboard_created_projects', verbose_name='创建人')

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
