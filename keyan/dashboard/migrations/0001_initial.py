# Generated by Django 5.1.2 on 2024-12-15 11:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='项目名称')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='项目编号')),
                ('description', models.TextField(blank=True, verbose_name='项目描述')),
                ('start_date', models.DateField(verbose_name='开始日期')),
                ('end_date', models.DateField(verbose_name='结束日期')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('in_progress', '进行中'), ('completed', '已完成'), ('suspended', '已暂停'), ('terminated', '已终止')], default='draft', max_length=20, verbose_name='项目状态')),
                ('is_archived', models.BooleanField(default=False, verbose_name='是否归档')),
                ('archived_at', models.DateTimeField(blank=True, null=True, verbose_name='归档时间')),
                ('archive_reason', models.TextField(blank=True, verbose_name='归档原因')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('archived_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archived_projects', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '项目',
                'verbose_name_plural': '项目',
                'ordering': ['-created_at'],
            },
        ),
    ]
