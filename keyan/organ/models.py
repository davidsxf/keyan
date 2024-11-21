from django.db import models

# Create your models here.


PROFESSION_RANK = (
    ("Researcher", "研究员"),
    ("Associate Research", "副研究员"),
    ("Assistant", "助理研究员"),
    ("Probationer", "研究实习员"),
    ("Learner", "见习期"),
    ("Senior Experimentalist", "高级实验师"),
    ("Experimentalist", "实验师"),
    ("Engineer", "工程师"),
    ("Other", "--"),

)

POSITION = (
    ("Chief", "所长"),
    ("Secretary", "书记"),
    ("Assistant", "副所长"),
    ("Probationer", "主任"),
    ("Learner", "副主任"),
    ("Senior Experimentalist", "处长"),
    ("Experimentalist", "副处长"),
    ("Other", "--"),

)


DEGREE = (
    ("Ongoing", "博士"),
    ("Conclusion", "硕士"),
    ("Conclusion", "学士"),
    ("Other", "--"),
)

SEX = (
    ("M", "男"),
    ("F", "女"),
    
    )


# 项目参与人类型
PARTICIPANT_TYPE = (
    ("employee", "职工"),
    ("student", "学生"),
    ("outsider", "所外人员"),
    

)
class Participant(models.Model):
    name = models.CharField('姓名', max_length=20)
    participant_type = models.CharField('参与者类型', max_length=20, choices=PARTICIPANT_TYPE)


    def __str__(self):
        return str(self.name)


class Org(models.Model):

    name = models.CharField(u"机构名称", max_length=100, unique=True)
    description = models.TextField(verbose_name="描述", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '机构'
        verbose_name_plural = '机构'

# Outsider 所外人员
class Outsider(Participant):

    # name_order = models.IntegerField(u"署名顺序")
    # name=models.CharField('姓名',max_length=20)
    sex = models.CharField('性别', choices=SEX, default='M', max_length=4)

    phone = models.CharField('手机号码', max_length=32, blank=True, null=True)
    email = models.EmailField('邮箱', max_length=255, unique=True, null=True)

    profession_rank = models.CharField(
        u'职称', max_length=50, choices=PROFESSION_RANK)
    birthday = models.DateField(null=True, blank=True)
    org = models.ForeignKey(Org, verbose_name='单位',
                            null=True, on_delete=models.SET_NULL)
    degree = models.CharField(u'学位', max_length=20, choices=DEGREE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '所外项目人员'
        verbose_name_plural = '所外项目人员'





class Department(models.Model):
    num = models.IntegerField(verbose_name='序号')
    name = models.CharField(max_length=30,verbose_name="名称",null=True)
    director = models.ForeignKey('Employee',verbose_name='部门负责人',null=True,blank=True,on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name='部门'
        verbose_name_plural='部门'
        
class Team(models.Model):
    num = models.IntegerField(verbose_name='序号',null=True)
    name = models.CharField(max_length=30,verbose_name="名称")
    department = models.ForeignKey(Department,verbose_name='部门', null=True,on_delete=models.SET_NULL)
    description = models.TextField(verbose_name="描述",null=True,blank=True)
    director = models.ForeignKey('Employee', verbose_name='团队负责人',
                                 null=True ,on_delete=models.SET_NULL, related_name='led_teams')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='团队'
        verbose_name_plural='团队'


class Employee(Participant):
    # num = models.IntegerField(verbose_name='序号',blank=True,null=True)
    # name = models.CharField(max_length=10,verbose_name="名称")
    position = models.CharField(u'职位',max_length=50,choices=POSITION,default='Other')
    dept = models.ForeignKey(
        Department, verbose_name='部门', null=True, on_delete=models.SET_NULL)
    team = models.ForeignKey(Team,verbose_name='团队',null=True, on_delete=models.SET_NULL)
    # department_leader = models.BooleanField(verbose_name='是否部门负责人', default=False)
    # team_leader = models.BooleanField(verbose_name='是否团队负责人', default=False) 
    phone = models.CharField('手机号码',max_length=32, blank=True, null=True)  
    email = models.EmailField('邮箱',max_length=255, blank=True,null=True)

    profession_rank = models.CharField(u'职称',max_length=50,choices=PROFESSION_RANK,default='Other')
    birthday = models.DateField(verbose_name='出生日期',null=True, blank=True)
    # org = models.ForeignKey(Org,verbose_name='单位',null=True, on_delete=models.SET_NULL)
    degree = models.CharField(u'学位',max_length=20,choices= DEGREE,default='Other')    
    context = models.TextField(verbose_name='备注',blank=True, null=True)


    def __str__(self):
        return self.name
      
    class Meta:
        verbose_name='职工'
        verbose_name_plural='职工'

class Student(Participant):
    num = models.IntegerField(verbose_name='学号')
    # name = models.CharField(max_length=10,verbose_name="名称")
    # department = models.ForeignKey(Department,verbose_name='部门',null=True, on_delete=models.SET_NULL)
    teacher = models.ForeignKey(Employee,verbose_name='导师',null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
      
    class Meta:
        verbose_name='学生'
        verbose_name_plural='学生'