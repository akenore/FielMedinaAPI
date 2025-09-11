from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Page

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'language', 'is_active', 'created_at']
    list_filter = ['language', 'is_active', 'created_at']
    search_fields = ['title', 'slug', 'content']
    list_editable = ['is_active']
    ordering = ['slug', 'language']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('slug', 'language', 'is_active')
        }),
        (_('Content'), {
            'fields': ('title', 'content')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
