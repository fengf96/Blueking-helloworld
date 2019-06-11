# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models


class Person(models.Model):
    english_name = models.CharField(u"英文名", max_length=64, blank=False)
    chinese_name = models.CharField(u"中文名", max_length=64)
    city = models.CharField(u"所在城市", max_length=64)
    birthday = models.DateTimeField(u"出生日期", default=datetime.now)
    age = models.IntegerField(u"年龄")
    email = models.EmailField(u"邮件", null=True, blank=True)
    tel = models.CharField(u"电话", max_length=64, null=True)
    blog = models.CharField(u"博客", max_length=256, null=True)

    def __unicode__(self):
        return self.english_name


class Book(models.Model):
    title = models.CharField(u"书名", max_length=128)
    author = models.ForeignKey(Person, verbose_name=u"作者")
    publication_date = models.DateTimeField(u"出版日期", default=datetime.now)
    price = models.IntegerField(u"价格")

    def __unicode__(self):
        return self.title
