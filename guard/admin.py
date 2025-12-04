from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, Location, ImageLocation, ImageEvent, LocationCategory, Event
from modeltranslation.admin import TranslationAdmin


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "user_type",
        "subscription_plan",
        "subscription_status",
        "subscription_renews_at",
        "created_at",
    )
    list_filter = ("user_type", "subscription_status")
    search_fields = ("user__username", "user__email")

    def save_model(self, request, obj, form, change):
        obj.user.is_staff = obj.user_type == UserProfile.UserType.STAFF
        obj.user.save(update_fields=["is_staff"])
        super().save_model(request, obj, form, change)

class ImageInline(admin.TabularInline):
    model = ImageLocation
    extra = 1

@admin.register(Location)
class LocationAdmin(TranslationAdmin):
    list_display = ['name', 'country', 'city', 'category', 'created_at']
    list_filter = ['country', 'is_active_ads', 'category']
    search_fields = ['name', 'story', 'city__name', 'country__name', 'category__name']
    inlines = [ImageInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('country', 'city', 'is_active_ads', 'category')
        }),
        (_('Location Details'), {
            'fields': ('name','latitude', 'longitude', 'openFrom', 'openTo', 'admissionFee','story')
        }),
    )

@admin.register(LocationCategory)
class LocationCategoryAdmin(TranslationAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


class ImageEventInline(admin.TabularInline):
    model = ImageEvent
    extra = 1


@admin.register(Event)
class EventAdmin(TranslationAdmin):
    list_display = ['name', 'location', 'client', 'startDate', 'endDate', 'price', 'created_at']
    list_filter = ['startDate', 'endDate', 'location']
    search_fields = ['name', 'description', 'location__name', 'client__user__username']
    inlines = [ImageEventInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'client', 'location')
        }),
        (_('Event Schedule'), {
            'fields': ('startDate', 'endDate', 'time')
        }),
        (_('Details'), {
            'fields': ('price', 'description')
        }),
    )