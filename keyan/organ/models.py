from django.db import models
from django.contrib.auth.models import User

class Organ(models.Model):
    """机构/单位"""
    ORGAN_TYPES = [
        ('university', '高校'),
        ('enterprise', '企业'),
        ('research', '横向院所'),
        ('government', '政府机构'),
        ('other', '其他'),
    ]
    
    name = models.CharField('机构名称', max_length=100)
    code = models.CharField('机构代码', max_length=50, unique=True)
    organ_type = models.CharField('机构类型', max_length=50, choices=ORGAN_TYPES)
    address = models.CharField('地址', max_length=200, blank=True)
    contact_person = models.CharField('联系人', max_length=50, blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    email = models.EmailField('邮箱', blank=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '机构'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name

class Department(models.Model):
    """部门"""
    name = models.CharField('部门名称', max_length=100)
    code = models.CharField('部门代码', max_length=50)
    organ = models.ForeignKey(Organ, on_delete=models.CASCADE, verbose_name='所属机构', related_name='departments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='上级部门', 
                              related_name='children', null=True, blank=True)
    director = models.ForeignKey('Staff', on_delete=models.SET_NULL, verbose_name='部门主管',
                                related_name='directing_departments', null=True, blank=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = verbose_name
        ordering = ['organ', 'code']
        unique_together = ['organ', 'code']

    def __str__(self):
        return f"{self.organ.name} - {self.name}"

class Team(models.Model):
    """团队"""
    name = models.CharField('团队名称', max_length=100)
    code = models.CharField('团队代码', max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属部门', 
                                 related_name='teams')
    leader = models.ForeignKey('Staff', on_delete=models.SET_NULL, verbose_name='团队负责人',
                              related_name='leading_teams', null=True, blank=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '团队'
        verbose_name_plural = verbose_name
        ordering = ['department', 'code']
        unique_together = ['department', 'code']

    def __str__(self):
        return f"{self.department.name} - {self.name}"

class Staff(models.Model):
    """人员"""
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
    ]
    
    TITLE_CHOICES = [
        ('professor', '教授'),
        ('associate_professor', '副教授'),
        ('lecturer', '讲师'),
        ('assistant', '助教'),
        ('researcher', '研究员'),
        ('engineer', '工程师'),
        ('other', '其他'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户账号')
    organ = models.ForeignKey(Organ, on_delete=models.CASCADE, verbose_name='所属机构')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, verbose_name='所属部门',
                                null=True, blank=True, related_name='staff')
    teams = models.ManyToManyField(Team, verbose_name='所属团队', related_name='members', blank=True)
    
    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES)
    title = models.CharField('职称', max_length=50, choices=TITLE_CHOICES, blank=True)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    email = models.EmailField('邮箱', blank=True)
    
    entry_date = models.DateField('入职日期', null=True, blank=True)
    leave_date = models.DateField('离职日期', null=True, blank=True)
    is_active = models.BooleanField('在职状态', default=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '人员'
        verbose_name_plural = verbose_name
        ordering = ['organ', 'name']

    def __str__(self):
        return self.name

    @property
    def username(self):
        return self.user.username if self.user else self.name