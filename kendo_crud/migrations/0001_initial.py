# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='\u4e66\u540d')),
                ('publication_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u51fa\u7248\u65e5\u671f')),
                ('price', models.IntegerField(verbose_name='\u4ef7\u683c')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('english_name', models.CharField(max_length=64, verbose_name='\u82f1\u6587\u540d')),
                ('chinese_name', models.CharField(max_length=64, verbose_name='\u4e2d\u6587\u540d')),
                ('city', models.CharField(max_length=64, verbose_name='\u6240\u5728\u57ce\u5e02')),
                ('birthday', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u51fa\u751f\u65e5\u671f')),
                ('age', models.IntegerField(verbose_name='\u5e74\u9f84')),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='\u90ae\u4ef6', blank=True)),
                ('tel', models.CharField(max_length=64, null=True, verbose_name='\u7535\u8bdd')),
                ('blog', models.CharField(max_length=256, null=True, verbose_name='\u535a\u5ba2')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.ForeignKey(verbose_name='\u4f5c\u8005', to='kendo_crud.Person'),
        ),
    ]
