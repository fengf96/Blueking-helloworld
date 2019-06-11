# -*- coding: utf-8 -*-
from django.conf.urls import patterns

urlpatterns = patterns(
    'kendo_crud.views',
    # =========================================================================
    # kendo grid样例
    # =========================================================================
    (r'^$', 'kendo_home'),
    (r'^get_part_by_name/$', 'get_part_by_name'),
    # 前台分页
    (r'^headend_pagation/$', 'headend_pagation'),
    # 后台分页
    (r'^backend_pagation/$', 'backend_pagation'),
    # 单行编辑
    (r'^inline_edit/$', 'inline_edit'),
    # 批量编辑
    (r'^batch_edit/$', 'batch_edit'),
    # 弹出层编辑
    (r'^popup_edit/$', 'popup_edit'),
    # 过滤
    (r'^filter_books/$', 'filter_books'),
    # drop_list查询
    (r'^search_books_by_drop_list/$', 'search_books_by_drop_list'),
    # form查询
    (r'^form_search/$', 'form_search'),
    (r'^form_search/autocomplete/', 'form_search_autocomplete'),
    # =========================================================================
    # form_sample
    # =========================================================================
    # 表单样例首页
    (r'^form_sample/$', 'form_sample'),
    # 表单验证
    (r'^form_validator/$', 'form_validator'),
    # 表单提交
    (r'^form_sample/form_submit/$', 'form_submit'),
    # ajax请求到数据，前台进行过滤
    (r'^form_sample/autocomplete_filter_by_before/$',
     'autocomplete_filter_by_before'),
    # ajax请求到数据，后台进行过滤
    (r'^form_sample/autocomplete_filter_by_background/$',
     'autocomplete_filter_by_background'),
    # 自定义验证规则，判断姓名是否存在
    (r'^form_sample/name_is_exist/$', 'name_is_exist'),
    # combobox级联
    (r'^form_sample/combobox_cascading_filter/$', 'combobox_cascading_filter'),
    # dropdownlist级联
    (r'^form_sample/dropdownlist_cascading_filter/$',
     'dropdownlist_cascading_filter'),
)
