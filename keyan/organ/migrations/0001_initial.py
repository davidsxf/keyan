# Generated by Django 5.1.2 on 2024-11-21 04:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(verbose_name='序号')),
                ('name', models.CharField(max_length=30, null=True, verbose_name='名称')),
            ],
            options={
                'verbose_name': '部门',
                'verbose_name_plural': '部门',
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='姓名')),
                ('participant_type', models.CharField(choices=[('employee', '职工'), ('student', '学生'), ('outsider', '所外人员')], max_length=20, verbose_name='参与者类型')),
            ],
        ),
        migrations.CreateModel(
            name='Org',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='机构名称')),
                ('description', models.TextField(blank=True, null=True, verbose_name='描述')),
            ],
            options={
                'verbose_name': '机构',
                'verbose_name_plural': '机构',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('participant_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='organ.participant')),
                ('position', models.CharField(choices=[('Chief', '所长'), ('Secretary', '书记'), ('Assistant', '副所长'), ('Probationer', '主任'), ('Learner', '副主任'), ('Senior Experimentalist', '处长'), ('Experimentalist', '副处长'), ('Other', '--')], default='Other', max_length=50, verbose_name='职位')),
                ('phone', models.CharField(blank=True, max_length=32, null=True, verbose_name='手机号码')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='邮箱')),
                ('profession_rank', models.CharField(choices=[('Researcher', '研究员'), ('Associate Research', '副研究员'), ('Assistant', '助理研究员'), ('Probationer', '研究实习员'), ('Learner', '见习期'), ('Senior Experimentalist', '高级实验师'), ('Experimentalist', '实验师'), ('Engineer', '工程师'), ('Other', '--')], default='Other', max_length=50, verbose_name='职称')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='出生日期')),
                ('degree', models.CharField(choices=[('Ongoing', '博士'), ('Conclusion', '硕士'), ('Conclusion', '学士'), ('Other', '--')], default='Other', max_length=20, verbose_name='学位')),
                ('context', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('dept', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='organ.department', verbose_name='部门')),
            ],
            options={
                'verbose_name': '职工',
                'verbose_name_plural': '职工',
            },
            bases=('organ.participant',),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(null=True, verbose_name='序号')),
                ('name', models.CharField(max_length=30, verbose_name='名称')),
                ('description', models.TextField(null=True, verbose_name='描述')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='organ.department', verbose_name='部门')),
                ('director', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='led_teams', to='organ.employee', verbose_name='团队负责人')),
            ],
            options={
                'verbose_name': '团队',
                'verbose_name_plural': '团队',
            },
        ),
        migrations.AddField(
            model_name='employee',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='organ.team', verbose_name='团队'),
        ),
        migrations.AddField(
            model_name='department',
            name='director',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='organ.employee', verbose_name='部门负责人'),
        ),
        migrations.CreateModel(
            name='Outsider',
            fields=[
                ('participant_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='organ.participant')),
                ('sex', models.CharField(choices=[('M', '男'), ('F', '女')], default='M', max_length=4, verbose_name='性别')),
                ('phone', models.CharField(blank=True, max_length=32, null=True, verbose_name='手机号码')),
                ('email', models.EmailField(max_length=255, null=True, unique=True, verbose_name='邮箱')),
                ('profession_rank', models.CharField(choices=[('Researcher', '研究员'), ('Associate Research', '副研究员'), ('Assistant', '助理研究员'), ('Probationer', '研究实习员'), ('Learner', '见习期'), ('Senior Experimentalist', '高级实验师'), ('Experimentalist', '实验师'), ('Engineer', '工程师'), ('Other', '--')], max_length=50, verbose_name='职称')),
                ('birthday', models.DateField(blank=True, null=True)),
                ('degree', models.CharField(choices=[('Ongoing', '博士'), ('Conclusion', '硕士'), ('Conclusion', '学士'), ('Other', '--')], max_length=20, verbose_name='学位')),
                ('org', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='organ.org', verbose_name='单位')),
            ],
            options={
                'verbose_name': '所外项目人员',
                'verbose_name_plural': '所外项目人员',
            },
            bases=('organ.participant',),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('participant_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='organ.participant')),
                ('num', models.IntegerField(verbose_name='学号')),
                ('teacher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='organ.employee', verbose_name='导师')),
            ],
            options={
                'verbose_name': '学生',
                'verbose_name_plural': '学生',
            },
            bases=('organ.participant',),
        ),
    ]
