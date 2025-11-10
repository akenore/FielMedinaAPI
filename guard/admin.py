from django.contrib import admin

from .models import UserProfile


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
