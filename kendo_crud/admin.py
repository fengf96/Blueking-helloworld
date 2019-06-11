# -*- coding: utf-8 -*-

from django.contrib import admin
from kendo_crud.models import Person, Book


class PersonAdmin(admin.ModelAdmin):
    list_display = ('english_name', 'chinese_name')
    search_fields = ('english_name', )
    ordering = ('english_name',)


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')
    search_fields = ('title', )
    ordering = ('title',)

admin.site.register(Person, PersonAdmin)
admin.site.register(Book, BookAdmin)
