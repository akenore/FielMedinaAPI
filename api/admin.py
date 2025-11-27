from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from .models import Page

@admin.register(Page)
class PageAdmin(TranslationAdmin):
    list_display = ['title', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'slug', 'content']
    list_editable = ['is_active']
    ordering = ['slug']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'content')
        }),
    )

