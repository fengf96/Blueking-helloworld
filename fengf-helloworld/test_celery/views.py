# -*- coding: utf-8 -*-
import time
import datetime
import json
from django.http import HttpResponseRedirect
from settings import SITE_URL

from common.mymako import render_mako_context, render_json
from common.log import logger

from test_celery.models import Peroid_task_record, Timing_task_record
from test_celery.utils import get_peroid_task_detail
from djcelery.models import PeriodicTask
# 兼容用户不使用 celery的情况
from common.celery_task import add_peroid_task, edit_peroid_task_by_id, del_peroid_task_by_id
from test_celery.utils import send_msg


# ===============================================================================
# 周期性任务的路径
TASK = 'test_celery.utils.add'
# ===============================================================================


def index(request):
    """
    首页展示
    """
    return HttpResponseRedirect(SITE_URL + 'test_celery/periodic_task/')


def timing_task(request):
    """
    定时任务
    """
    return render_mako_context(request, '/test_celery/timing_task.html')


def excute_task(request):
    """
    @summary: 执行任务
    @note: 调用celery任务方法:
                task.delay(arg1, arg2, kwarg1='x', kwarg2='y')
                task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
                delay(): 简便方法，类似调用普通函数
                apply_async(): 设置celery的额外执行选项时必须使用该方法，如定时（eta）等
                      详见 ：http://celery.readthedocs.org/en/latest/userguide/calling.html
    """
    username = request.user.username
    params = request.POST.get('params', {})
    try:
        params = json.loads(params)
        msg_param = params.get('send_msg', {})
    except:
        msg = u"参数解析出错"
        logger.error(msg)
        result = {'result': False, 'message': msg}
        return render_json(result)
    # 定时参数
    is_schedule = params.get('is_schedule', {})
    do_schedule = is_schedule.get('do_schedule', 0)
    schedule_time = is_schedule.get('schedule_time', '') if do_schedule else ''
    schedule_timestamp = ''
    # 定时时间格式化
    if schedule_time:
        try:
            schedule_timestamp = time.mktime(
                time.strptime(schedule_time, '%Y-%m-%d %H:%M'))
            schedule_time = datetime.datetime.strptime(
                schedule_time, '%Y-%m-%d %H:%M')
        except Exception, e:
            msg = u"定时时间(%s)格式错误:%s" % (schedule_time, e)
            logger.error(msg)
            return render_json({'result': False, 'message': msg})
    # 任务执行参数
    title = u"蓝鲸APP样例——后台任务"
    msg_param['schedule_time'] = schedule_time
    # 写入数据库
    try:
        timing_record = Timing_task_record(username=username, title=title, content=msg_param.get('message', ''),
                                           create_time=datetime.datetime.now(), is_excuted=0)
        timing_record.save()
    except Exception, e:
        logger.error(u"创建定时任务记录出错：%s" % e)
        return render_json({'result': False, 'message': u"创建定时任务失败！"})

    # 执行 celery 任务
    if schedule_time:
        # 后台定时执行
        send_msg.apply_async(args=[timing_record.id],
                             kwargs=msg_param, eta=schedule_time)
    else:
        # 后台任务
        send_msg.delay(timing_record.id, **msg_param)
    return render_json({'result': True, 'message': schedule_timestamp, 'record_id': timing_record.id})


def poll_task(request):
    """
    @summary: 轮询定时任务
    """
    try:
        record_id = request.GET.get('record_id', '')
        record = Timing_task_record.objects.get(id=record_id)
        if record.is_excuted == 0:
            result = {'result': 2, 'message': u"未执行定时任务"}
        else:
            result = {'result': 1, 'title': record.title,
                      'content': record.content}
    except Exception, e:
        logger.error(u"轮询定时任务状态出错：%s" % e)
        result = {'result': 0, 'message': u"轮询定时任务状态出错"}
    return render_json(result)


def periodic_task(request):
    """
    周期任务首页
    """
    return render_mako_context(request, '/test_celery/periodic_task.html')


def get_periodic_tasks(request):
    """
    查询所有周期任务
    """
    # 每页记录数
    record_num = int(request.GET.get('pageSize'))
    # 页码
    page_index = int(request.GET.get('page'))
    # 分片起始位置
    start = (page_index - 1) * record_num
    # 分片结束位置
    end = start + record_num
    peroid_tasks = PeriodicTask.objects.filter(task=TASK)
    total = peroid_tasks.count()
    task_set = peroid_tasks[start:end]
    data_list = []
    for task in task_set:
        data_list.append({
            'id': task.id,
            'task': task.task,
            'args': task.args,
            'kwargs': task.kwargs,
            'crontab': str(task.crontab)
        })
    data = {'data_list': data_list, 'total': total}
    return render_json({'result': True, 'data': data})


def periodic_task_edit(request, task_id):
    """
    启动、编辑任务页面，显示任务详情
    @todo: 通过task_id获取任务
    """
    task_info = get_peroid_task_detail(task_id)
    # 解析任务参数
    task_args = task_info.get('task_args', [])
    # 解析任务参数
    try:
        task_args = json.loads(task_args)
        task_args1 = task_args[0]
        task_args2 = task_args[1] if len(task_args) > 1 else 0
    except:
        task_args1 = 0
        task_args2 = 0
    task_info['task_args1'] = task_args1
    task_info['task_args2'] = task_args2
    return render_mako_context(request, '/test_celery/periodic_task_edit.html', task_info)


def check_peroid_task(requets):
    """
    检查任务参数是否已存在（相同任务，相同参数的周期任务只允许有一条记录）
    相同任务，相同参数、不同调度策略的任务可以通过crontab策略的配置合并为一个任务
    """
    task = requets.POST.get('task', TASK)
    task_args_old = requets.POST.get('task_args_old', '[]')
    task_args1 = requets.POST.get('task_args1', '')
    task_args2 = requets.POST.get('task_args2', '')
    flag = False
    message = ''
    # 任务参数
    try:
        task_args1 = int(task_args1)
        task_args2 = int(task_args2)
        task_args_list = [task_args1, task_args2]
        task_args = json.dumps(task_args_list)
    except:
        logger.error(u"解析任务参数出错, task_args1;%s, task_args2;%s" %
                     (task_args1, task_args2))
    else:
        # 参数未改变，则不用检查
        if task_args_old == task_args:
            flag = True
        else:
            count = PeriodicTask.objects.filter(
                task=task, args=task_args).count()
            if count == 0:
                flag = True
    if not flag:
        message = "任务名为：%s\n任务参数为：X:%s,Y:%s\n的周期任务已存在！" % (
            task, task_args1, task_args2)
    return render_json({'result': flag, 'message': message})


def save_task(request):
    """
    创建/编辑周期性任务 并 运行
    """
    periodic_task_id = request.POST.get('periodic_task_id', '0')
    params = request.POST.get('params', {})
    try:
        params = json.loads(params)
        add_param = params.get('add_task', {})
    except:
        msg = u"参数解析出错"
        logger.error(msg)
        result = {'result': False, 'message': msg}
        return render_json(result)
    task_args1 = add_param.get('task_args1', '0')
    task_args2 = add_param.get('task_args2', '0')
    # 任务参数
    try:
        task_args1 = int(task_args1)
        task_args2 = int(task_args2)
        task_args_list = [task_args1, task_args2]
        task_args = json.dumps(task_args_list)
    except:
        task_args = '[0,0]'
        logger.error(u"解析任务参数出错")
    #  周期参数
    minute = add_param.get('minute', '*')
    hour = add_param.get('hour', '*')
    day_of_week = add_param.get('day_of_week', '*')
    day_of_month = add_param.get('day_of_month', '*')
    month_of_year = add_param.get('month_of_year', '*')
    # 创建周期任务时，任务名必须唯一
    now = int(time.time())
    task_name = "%s_%s" % (TASK, now)
    if periodic_task_id == '0':
        # 创建任务并运行
        res, msg = add_peroid_task(TASK, task_name, minute, hour,
                                   day_of_week, day_of_month,
                                   month_of_year, task_args)
    else:
        # 修改任务
        res, msg = edit_peroid_task_by_id(periodic_task_id, minute, hour,
                                          day_of_week, day_of_month,
                                          month_of_year, task_args)
    return render_json({'result': res, 'message': msg})


def del_peroid_task(request):
    """
    删除周期性任务
    """
    task_id = request.POST.get('id')
    res, msg = del_peroid_task_by_id(task_id)
    if res:
        msg = u"任务删除成功"
    return render_json({'result': res, 'message': msg})


def periodic_task_record(request, task_id):
    """
    显示周期性任务执行记录页面
    """
    #  查询周期任务的信息
    task_info = get_peroid_task_detail(task_id)
    return render_mako_context(request, '/test_celery/periodic_task_record.html', task_info)


def get_records(request):
    """
    获取周期性任务执行记录
    @todo: 查找指定任务的执行记录
    """
    periodic_task_id = request.GET.get('periodic_task_id', '')
    # 每页记录数
    record_num = int(request.GET.get('pageSize'))
    # 页码
    page_index = int(request.GET.get('page'))
    # 分片起始位置
    start = (page_index - 1) * record_num
    # 分片结束位置
    end = start + record_num
    peroid_tasks = Peroid_task_record.objects.all()
    if periodic_task_id:
        peroid_tasks = peroid_tasks.filter(periodic_task_id=periodic_task_id)
    total = peroid_tasks.count()
    task_set = peroid_tasks[start:end]
    data_list = []
    for task in task_set:
        data_list.append({
            'id': task.id,
            'excute_time': task.excute_time.strftime('%Y-%m-%d %H:%M:%S') if task.excute_time else '--',
            'excute_result': task.excute_result,
            'excute_param': task.excute_param
        })
    data = {'data_list': data_list, 'total': total}
    return render_json({'result': True, 'data': data})
