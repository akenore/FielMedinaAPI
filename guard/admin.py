from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Location,
    ImageLocation,
    ImageEvent,
    LocationCategory,
    Event,
    EventCategory,
    Tip,
    Hiking,
    ImageHiking,
    Ad,
)
from modeltranslation.admin import TranslationAdmin


class ImageInline(admin.TabularInline):
    model = ImageLocation
    extra = 1


@admin.register(Location)
class LocationAdmin(TranslationAdmin):
    list_display = ["name", "country", "city", "category", "created_at"]
    list_filter = ["country", "is_active_ads", "category"]
    search_fields = ["name", "story", "city__name", "country__name", "category__name"]
    inlines = [ImageInline]

    fieldsets = (
        (
            _("Basic Information"),
            {"fields": ("country", "city", "is_active_ads", "category")},
        ),
        (
            _("Location Details"),
            {
                "fields": (
                    "name",
                    "latitude",
                    "longitude",
                    "openFrom",
                    "openTo",
                    "admissionFee",
                    "story",
                )
            },
        ),
    )


@admin.register(LocationCategory)
class LocationCategoryAdmin(TranslationAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


class ImageEventInline(admin.TabularInline):
    model = ImageEvent
    extra = 1


@admin.register(Event)
class EventAdmin(TranslationAdmin):
    list_display = [
        "name",
        "location",
        "client",
        "startDate",
        "endDate",
        "price",
        "created_at",
    ]
    list_filter = ["startDate", "endDate", "location"]
    search_fields = ["name", "description", "location__name", "client__user__username"]
    inlines = [ImageEventInline]

    fieldsets = (
        (
            _("Basic Information"),
            {"fields": ("name", "client", "location", "category")},
        ),
        (
            _("Event Schedule"),
            {
                "fields": (
                    "startDate",
                    "endDate",
                    "time",
                    "link",
                    "short_link",
                    "short_id",
                )
            },
        ),
        (_("Details"), {"fields": ("price", "description")}),
    )


@admin.register(EventCategory)
class EventCategoryAdmin(TranslationAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Tip)
class TipAdmin(TranslationAdmin):
    list_display = ["description", "created_at"]
    search_fields = ["description"]


class ImageHikingInline(admin.TabularInline):
    model = ImageHiking
    extra = 1


@admin.register(Hiking)
class HikingAdmin(TranslationAdmin):
    list_display = [
        "city",
        "name",
    ]
    list_filter = ["city", "name", "location"]
    search_fields = [
        "name",
        "description",
    ]
    inlines = [ImageHikingInline]

    fieldsets = (
        (
            _("Basic Information"),
            {"fields": ("name", "city", "description", "location")},
        ),
    )


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "client",
        "clicks",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "client"]
    search_fields = ["name", "link", "client__user__username"]

    fieldsets = (
        (
            _("Basic Information"),
            {"fields": ("name", "client", "is_active")},
        ),
        (
            _("Ad Images"),
            {"fields": ("image_mobile", "image_tablet")},
        ),
        (
            _("Link Information"),
            {
                "fields": (
                    "link",
                    "short_link",
                    "short_id",
                )
            },
        ),
        (_("Statistics"), {"fields": ("clicks",)}),
    )
