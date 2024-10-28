from django.db import models

# Create your models here.


class Researcher(models.Model):
    PERSON_TYPE = (
        ("ZB", "在编"),
        ("LP", "临聘"),
        ("XS", "学生"),
        ("SW", "所外"),

    )

    name = models.CharField('姓名', max_length=20)
    phone = models.CharField('电话', max_length=20, blank=True,null=True)
    person_type = models.CharField('人员类型', max_length=2, choices=PERSON_TYPE)
    organ = models.ForeignKey(
        'Org',related_name='organ_participant', verbose_name='所属机构', null=True, on_delete=models.SET_NULL)
    department = models.ForeignKey(
        'Department', related_name='department_participant', verbose_name='所属部门', null=True, on_delete=models.SET_NULL)
    team = models.ForeignKey('Team', related_name='team_participant', verbose_name='所属团队',
                             null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.name)
    
    
    class Meta:
        verbose_name='项目人员'
        verbose_name_plural='项目人员'

class Org(models.Model):

    name = models.CharField(u"机构名称", max_length=100, unique=True)
    description = models.TextField(verbose_name="描述", blank=True, null=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name='机构'
        verbose_name_plural='机构'

class Department(models.Model):
    name = models.CharField(max_length=30,verbose_name="名称",null=True)
    org = models.ForeignKey(Org, verbose_name='所属机构', null=True, on_delete=models.SET_NULL)

    director = models.OneToOneField('Researcher', related_name='director_department', verbose_name='部门负责人', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name='部门'
        verbose_name_plural='部门'