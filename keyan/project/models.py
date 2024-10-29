from django.db import models
from organ.models import Outsider, Org, Employee, Student, Participant
import datetime
# Create your models here.


def year_choices():
    return [(r, r) for r in range(1984, datetime.date.today().year+1)]


def current_year():
    return datetime.date.today().year


def project_directory_path(instance, filename):
    # 文件上传到MEDIA_ROOT/user_<id>/<filename>目录中
    return 'project_{0}/{1}'.format(instance.project.id, filename)

PROJECT_TYPE = (
    ("Ministerial", "部级科研项目"),
    ("System Position", "国家现代农业产业技术体系岗位专家"),
    ("National KeyRD", "国家重点研发计划课题"),
    ("NSFC General ", "国家自然科学基金（面上项目）"),
    ("National Subtopic", "其他国家级项目（子课题）"),
    ("Provincial", "省级科研项目"),
    ("City", "市级科研项目"),
    ("Academy", "院级科研项目"),
    ("Institute", "所级基本科研业务费专项项目"),
    ("Other", "其他项目计划"),

)

PRPJECT_STATUS = (
    ("Ongoing", "在研"),
    ("Conclusion", "结题"),
)


class Project(models.Model):
    num = models.CharField('项目编号',max_length=100,blank=True, null=True)
    finance_num = models.CharField('财务编号',max_length=100,blank=True, null=True)
    name = models.CharField('项目名称',max_length=100,unique=True)
    project_type = models.CharField('项目类别',max_length=30,choices=PROJECT_TYPE,blank=True, null=True)
    sign_date = models.DateField('签约日期',default=datetime.date.today,blank=True, null=True)
    start_date = models.DateField('开始日期',default=datetime.date.today,blank=True, null=True)
    end_date = models.DateField('计划结项日期',blank=True, null=True)
    authorize_units = models.ForeignKey(Org,verbose_name='委托单位',on_delete=models.SET_NULL,blank=True,null=True)
    source = models.CharField('资金来源',max_length=100,blank=True, null=True)
    director = models.ForeignKey(Employee,verbose_name='项目负责人',blank=True, null=True,on_delete=models.SET_NULL,related_name='directors')
    contract_fund = models.DecimalField('合同经费(万元)',max_digits=7, decimal_places=2,default=0)
    # support_fund = models.DecimalField('配套经费(万元)',max_digits=7, decimal_places=2)
    # out_fund = models.DecimalField('外拨经费(万元)',max_digits=7, decimal_places=2)
    # itself_fund = models.DecimalField('自筹经费(万元)',max_digits=7, decimal_places=2)
    # year = models.IntegerField('年度',default=current_year)
    participant = models.ManyToManyField(Participant,verbose_name='项目参与人',through='Participantion',related_name='participants')
    enter_year = models.IntegerField('登记年度',default=current_year,blank=True, null=True)
    enter_info = models.CharField('登记情况',max_length=50,blank=True, null=True)
    end_info = models.CharField('结项情况',max_length=50,blank=True, null=True)
    doc_transfer = models.CharField('档案移交情况',max_length=50,blank=True, null=True)
    context = models.TextField('备注',blank=True, null=True)


    achievement_info = models.CharField('成果简介',max_length=50,blank=True, null=True)
    
    status = models.CharField('项目状态',max_length=10,choices=PRPJECT_STATUS,default='Ongoing',blank=True, null=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'


class Participantion(models.Model):

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name='项目')

    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name='项目参与人')
    order = models.IntegerField('项目参与顺序', default=0)

    def __str__(self):
        return "项目： {}, 项目参与人： {},项目参与顺序： {}".format(self.project.name, self.participant.name, self.order)

    class Meta:
        verbose_name = '项目参与'
        verbose_name_plural = '项目参与'
        unique_together = [['project', 'participant']]


class ProjectDoc(models.Model):
    path = models.FileField(upload_to=project_directory_path,verbose_name='文件')
    info = models.CharField('文件信息',max_length=255)
    project = models.ForeignKey(Project,on_delete=models.DO_NOTHING,verbose_name="文件所属项目")


    def __str__(self):
        return self.path

    class Meta:
        verbose_name='项目文档'
        verbose_name_plural='项目文档'
