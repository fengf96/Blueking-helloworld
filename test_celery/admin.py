# -*- coding: utf-8 -*-
from django.contrib import admin
from test_celery.models import Peroid_task_record, Timing_task_record


admin.site.register(Peroid_task_record)
admin.site.register(Timing_task_record)
