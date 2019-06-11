# -*- coding: utf-8 -*-
from django.conf.urls import patterns


urlpatterns = patterns(
    'test_celery.views',
    (r'^$', 'index'),
    # =========================================================================
    # 定时任务
    # =========================================================================
    (r'^timing_task/$', 'timing_task'),
    (r'^excute_task/$', 'excute_task'),
    (r'^poll_task/$', 'poll_task'),
    # =========================================================================
    # 周期任务
    # =========================================================================
    (r'^periodic_task/$', 'periodic_task'),
    (r'^get_periodic_tasks/$', 'get_periodic_tasks'),
    (r'^periodic_task_edit/(?P<task_id>\d+)/', 'periodic_task_edit'),
    (r'^check_peroid_task/$', 'check_peroid_task'),
    (r'^save_task/$', 'save_task'),
    (r'^del_peroid_task/$', 'del_peroid_task'),
    # 周期任务 执行记录
    (r'^periodic_task_record/(?P<task_id>\d+)/$', 'periodic_task_record'),
    (r'^get_records/$', 'get_records'),
)
