# -*- coding: utf-8 -*-
import datetime
import json

from django.http import HttpResponse

from common.log import logger
from common.mymako import render_mako_context, render_json, render_mako_tostring_context
from kendo_crud.models import Person, Book


# ===============================================================================
# kendo grid样例
# ===============================================================================
def kendo_home(request):
    """
    grid首页
    """
    return render_mako_context(request, "/kendo_crud/kendo_index.html", {})


def get_part_by_name(request):
    part_name = request.GET.get('part_name')
    res = render_mako_tostring_context(request, '/kendo_crud/' + part_name, {})
    return render_json({'result': True, 'res': res})


# ===============================================================================
# 表单样例
# ===============================================================================
def form_sample(request):
    """
    表单样例
    """
    person_list = []                   # person信息列表
    person_all = Person.objects.all()  # 获取所有的person
    for _person in person_all:
        person_list.append({
            'city': _person.city,                 # person所在城市
            'chinese_name': _person.chinese_name  # person英文名
        })
    # autocomplete 、combobox、dropdownlist共用前台所需数据
    result = {'person_list': json.dumps(person_list)}
    return render_mako_context(request, 'kendo_crud/form_sample.part', result)


def form_validator(request):
    """
    表单验证样例
    """
    return render_mako_context(request, 'kendo_crud/form_validator.part')


def form_submit(request):
    """
    接收表单提交数据（可以对表单数据进行后台验证并保存到数据库）
    """
    try:
        # 获取表单数据（键值对）
        form_data = json.loads(request.POST.get('form_data'))
        # 记入数据库
        Person(
            english_name=form_data['english_name'],
            chinese_name=form_data['english_name'],
            birthday=form_data['birthday'],
            city=form_data['city'],
            age=form_data['age'],
            email=form_data['email'],
            tel=form_data['tel'],
            blog=form_data['blog'],
        ).save()
        result = {'result': True, 'msg': u"保存成功！"}
    except Exception, e:
        result = {'result': False, 'msg': u"保存失败！error：%s" % e}
    # 重定向到首页
    return render_json(result)


def autocomplete_filter_by_before(request):
    """
    ajax请求一次数据，前台进行过滤（autocomplete 、combobox、dropdownlist共用）
    """
    person_list = []
    person_all = Person.objects.all()
    for _person in person_all:
        person_list.append({
            'city': _person.city,
            'chinese_name':  _person.chinese_name,
            'english_name': _person.english_name
        })
    return HttpResponse(json.dumps(person_list))


def autocomplete_filter_by_background(request):
    """
    后台过滤数据（必须指定查询字段名（这是里是city））（autocomplete 、combobox、dropdownlist共用）
    """
    # 获取过滤参数
    # filter_logic = request.GET.get('filter[logic]', 'and')
    # 输入的内容
    filter_value = request.GET.get('filter[filters][0][value]', '')
    # 搜索方式
    filter_operator = request.GET.get(
        'filter[filters][0][operator]', ' startswith')
    # filter_field = request.GET.get('filter[filters][0][field]', '')
    # 忽略大小写（true为忽略）
    filter_ignoreCase = request.GET.get(
        'filter[filters][0][ignoreCase]', 'true')
    person_list = []
    # 根据过滤条件进行后台数据查询（如果指定了一种过滤模式可不是用下面判断，直接查询）
    if filter_ignoreCase == 'true' and filter_value:
        if filter_operator == 'startswith':
            person_all = Person.objects.filter(city__istartswith=filter_value)
        elif filter_operator == 'endswith':
            person_all = Person.objects.filter(city__iendswith=filter_value)
        elif filter_operator == 'contains':
            person_all = Person.objects.filter(city__icontains=filter_value)
    elif filter_ignoreCase == 'false' and filter_value:
        if filter_operator == 'startswith':
            person_all = Person.objects.filter(city__startswith=filter_value)
        elif filter_operator == 'endswith':
            person_all = Person.objects.filter(city__endswith=filter_value)
        elif filter_operator == 'contains':
            person_all = Person.objects.filter(city__contains=filter_value)
    else:
        # 没有过滤条件则查询所有person
        person_all = Person.objects.all()
    for _person in person_all:
        person_list.append({
            'city': _person.city,
            'chinese_name':  _person.chinese_name,
            'english_name': _person.english_name
        })
    return HttpResponse(json.dumps(person_list))


def combobox_cascading_filter(request):
    """
    combobox 级联（二级数据查询，自定义返回指定域数据，这里是english_name，匹配方式是"等于"）
    """
    # 获取上一级填写的数据
    filter_value = request.GET.get('filter[filters][0][value]', '')
    # 在关联域中查询对应的数据
    book_all = Book.objects.filter(author__english_name=filter_value)
    book_list = []
    for _book in book_all:
        book_list.append({'title': _book.title})
    # 没有数据时指定默认值
    if not book_list:
        book_list.append({'title': u"请选择..."})
    return HttpResponse(json.dumps(book_list))


def dropdownlist_cascading_filter(request):
    """
    dropdownlist 级联（二级数据查询，自定义返回指定域数据，这里是chinese_name，匹配方式是"等于"）
    """
    # 获取上一级填写的数据
    filter_value = request.GET.get('filter[filters][0][value]', '')
    # 在关联域中查询对应的数据
    book_all = Book.objects.filter(author__english_name=filter_value)
    book_list = []
    for _book in book_all:
        # 返回查询到的书籍名称
        book_list.append({'title': _book.title})
    return HttpResponse(json.dumps(book_list))


def name_is_exist(request):
    """
    自定义表单验证name是否已经存在
    """
    # 查询该english_name 对应的作家信息
    name = request.GET.get('name')
    person = Person.objects.filter(english_name=name)
    if person:
        result = {'is_exist': True}         # 存在返回True
    else:
        result = {'is_exist': False}        # 不存在返回False
    return render_json(result)


def headend_pagation(request):
    """
    @note : 前台分页
    @return 返回结果，json数据
            example: {
                        'result':True,
                        'data':{'data_list':data_list, # 数据列表
                                'total':total,  # 结果总数
                                }
                      }
    """
    all_person = Person.objects.all()
    data_list = []
    for person in all_person:
        data_list.append({
            'id': person.pk,
            'english_name': person.english_name,
            'chinese_name': person.chinese_name,
            'city': person.city,
            'birthday': person.birthday.strftime('%Y-%m-%d'),
            'age': person.age,
            'email': person.email,
            'tel': person.tel
        })
    return HttpResponse(json.dumps(data_list))


def backend_pagation(request):
    """
    @note : 后台分页
            请求示例：/test_kendo_grid/backend_pagation/?page=1&pageSize=12
    @param page: 当前的页数
    @param pagesize: 每页记录数
    @ return: 返回结果，json数据
            example: {
                        'result':True,
                        'data':{'data_list':data_list, # 数据列表
                                'total':total,  # 结果总数
                                }
                      }
    """
    # 每页记录数
    record_num = int(request.GET.get('pageSize'))
    # 页码
    page_indx = int(request.GET.get('page'))
    # 分片起始位置
    start = (page_indx - 1) * record_num
    # 分片结束位置
    end = start + record_num
    all_person = Person.objects.all()
    total = all_person.count()
    data_list = []
    for person in all_person[start: end]:
        data_list.append({
            'id': person.pk,
            'english_name': person.english_name,
            'chinese_name': person.chinese_name,
            'city': person.city,
            'birthday': person.birthday.strftime('%Y-%m-%d'),
            'age': person.age,
            'email': person.email,
            'tel': person.tel
        })
    return render_json({'data': data_list, 'total': total})


def create(request):
    """
    @note : 新建表格数据
    """
    models = request.POST.get('models', '{}')
    models_json = json.loads(models)
    create_data_list = []
    try:
        for data in models_json:
            english_name = data['english_name']
            chinese_name = data['chinese_name']
            city = data['city']
            email = data['email']
            tel = data['tel']
            birthday = datetime.datetime.strptime(
                data['birthday'], '%Y-%m-%d %H:%M:%S')
            age = int(data['age'])
            person = Person.objects.create(
                english_name=english_name,
                chinese_name=chinese_name,
                city=city,
                birthday=birthday,
                age=age,
                email=email,
                tel=tel)
            data['id'] = person.pk
            create_data_list.append(data)
        result = {'result': True, 'data': create_data_list}
    except Exception, e:
        logger.error(u"添加新纪录失败，%s" % e)
        result = {'result': False, 'message': u"添加新纪录失败，%s" % e}
    return render_json(result)


def update(request):
    """
    @note : 表格数据更新操作
    """
    models = request.POST.get('models', '{}')
    models_json = json.loads(models)
    update_data_list = []
    try:
        for data in models_json:
            pk = data['id']
            english_name = data['english_name']
            chinese_name = data['chinese_name']
            city = data['city']
            email = data['email']
            tel = data['tel']
            birthday = datetime.datetime.strptime(
                data['birthday'], '%Y-%m-%d %H:%M:%S')
            age = int(data['age'])
            Person.objects.filter(pk=pk).update(
                english_name=english_name,
                chinese_name=chinese_name,
                city=city,
                birthday=birthday,
                age=age,
                email=email,
                tel=tel
            )
            update_data_list.append(data)
        result = {'result': True, 'data': update_data_list}
    except Exception, e:
        logger.error(u"更新纪录失败，%s" % e)
        result = {'result': False, 'message': u"更新纪录失败，%s" % e}
    return render_json(result)


def delete(request):
    """
    @note : 表格删除操作
    """
    models = request.POST.get('models', '{}')
    models_json = json.loads(models)
    delete_data_list = []
    try:
        for data in models_json:
            pk = data['id']
            Person.objects.filter(pk=pk).delete()
            delete_data_list.append(data)
        result = {'result': True, 'data': delete_data_list}
    except Exception, e:
        logger.error(u"删除纪录失败，%s" % e)
        result = {'result': False, 'message': u"删除纪录失败，%s" % e}
    return render_json(result)


def inline_edit(request):
    """
    @note: 单行编辑
    @param operation:操作。value为create、update、destroy
    """
    operation = request.POST.get('operation')
    if operation == 'create':
        return create(request)
    if operation == 'update':
        return update(request)
    if operation == 'destroy':
        return delete(request)


def batch_edit(request):
    """
    @note: 批量编辑
    @param operation:操作。value为create、update、destroy
    """
    operation = request.POST.get('operation')
    if operation == 'create':
        return create(request)
    if operation == 'update':
        return update(request)
    if operation == 'destroy':
        return delete(request)


def popup_edit(request):
    """
    @note: 弹出层编辑
    @param operation:操作。value为create、update、destroy
    """
    operation = request.POST.get('operation')
    if operation == 'create':
        return create(request)
    if operation == 'update':
        return update(request)
    if operation == 'destroy':
        return delete(request)


def filter_books(request):
    """
    @filters:过滤条件
     example:['logic':'and',
                {
                    'field':'person_id',
                    'operator': "eq",
                    'value': '1'
                }
            ]
    """
    filters = request.GET.get('filters', '')
    filters_json = json.loads(filters)
    value = filters_json[0]['value']
    all_book = Book.objects.filter(author__english_name=value)
    total = all_book.count()
    # 每页记录数
    record_num = int(request.GET.get('pageSize'))
    # 页码
    page_indx = int(request.GET.get('page'))
    # 分片起始位置
    start = (page_indx - 1) * record_num
    # 分片结束位置
    end = start + record_num
    data_list = []
    for book in all_book[start:end]:
        data_list.append({
            'id': book.pk,
            'title': book.title,
            'publication_date': book.publication_date.strftime('%Y-%m-%d'),
            'price': book.price,
        })
    return render_json({'data': data_list, 'total': total})


def search_books_by_drop_list(request):
    """
    @note:下拉列表查询。根据选择的english_name，查询对应的book
    """
    filters = request.GET.get('filters', '')
    if filters == '':
        book_queryset = Book.objects.all()
    else:
        filters_json = json.loads(filters)
        value = filters_json[0]['value']
        book_queryset = Book.objects.filter(author__pk=value)
    total = book_queryset.count()
    # 每页记录数
    record_num = int(request.GET.get('pageSize'))
    # 页码
    page_indx = int(request.GET.get('page'))
    # 分片起始位置
    start = (page_indx - 1) * record_num
    # 分片结束位置
    end = start + record_num
    data_list = []
    for book in book_queryset[start:end]:
        data_list.append({
            'id': book.pk,
            'title': book.title,
            'publication_date': book.publication_date.strftime('%Y-%m-%d'),
            'price': book.price,
        })
    return render_json({'data': data_list, 'total': total})


def form_search_autocomplete(request):
    """
    请求autocomplete和combox数据
    """
    person_list = []
    person_all = Person.objects.all()
    for _person in person_all:
        person_list.append({
            'english_name': _person.english_name,
            'city': _person.city,
            'email': _person.email,
            'tel': _person.tel
        })
    return HttpResponse(json.dumps(person_list))


def form_search(request):
    """
    grid+表单查询样例
    """
    english_name = request.GET.get('english_name', '')
    email = request.GET.get('email', '')
    start_birthday = request.GET.get('start_birthday', '')
    end_birthday = request.GET.get('end_birthday', '')
    start_age = request.GET.get('start_age', '')
    end_age = request.GET.get('end_age', '')
    city = request.GET.get('city', '')
    tel = request.GET.get('tel', '')

    person_queryset = Person.objects.all()
    if english_name != '':
        person_queryset = person_queryset.filter(
            english_name__in=english_name.strip().rstrip(';').split(';'))
    if email != '':
        person_queryset = person_queryset.filter(email=email)
    if start_birthday != '':
        _start_birthday = datetime.datetime.strptime(
            start_birthday, '%Y-%m-%d')
        person_queryset = person_queryset.filter(birthday__gte=_start_birthday)
    if end_birthday != '':
        _end_birthday = datetime.datetime.strptime(end_birthday, '%Y-%m-%d')
        person_queryset = person_queryset.filter(birthday__lte=_end_birthday)
    if start_age != '':
        person_queryset = person_queryset.filter(age__gte=int(start_age))
    if end_age != '':
        person_queryset = person_queryset.filter(age__lte=int(end_age))
    if city != '':
        person_queryset = person_queryset.filter(
            city__in=city.strip().rstrip(';').split(';'))
    if tel != '':
        person_queryset = person_queryset.filter(tel=tel)
    total = person_queryset.count()
    # 每页记录数
    record_num = int(request.GET.get('pageSize'))
    # 页码
    page_indx = int(request.GET.get('page'))
    # 分片起始位置
    start = (page_indx - 1) * record_num
    # 分片结束位置
    end = start + record_num
    data_list = []
    for person in person_queryset[start:end]:
        data_list.append({
            'id': person.pk,
            'english_name':  person.english_name,
            'chinese_name': person.chinese_name,
            'city': person.city,
            'birthday': person.birthday.strftime('%Y-%m-%d'),
            'age': person.age,
            'email': person.email,
            'tel': person.tel,
        })
    data = {'data_list': data_list, 'total': total}
    return render_json({'result': True, 'data': data})
