from datetime import timedelta
import os

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from shared.models import OptimizedImageModel

User = get_user_model()

class UserProfile(models.Model):
    class UserType(models.TextChoices):
        STAFF = "staff", _("Staff")
        CLIENT_PARTNER = "client_partner", _("Client / Partenaire")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile",)
    user_type = models.CharField(max_length=32, choices=UserType.choices, default=UserType.CLIENT_PARTNER)
    subscription_plan = models.CharField(max_length=100, blank=True, default="Trial", help_text=_("Placeholder until Konnect subscription is attached."))
    subscription_status = models.CharField(max_length=32, blank=True, default="trial",)
    subscription_started_at = models.DateField(null=True, blank=True)
    subscription_renews_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")

    def __str__(self) -> str:
        return f"{self.user.get_username()} ({self.get_user_type_display()})"

    @property
    def is_staff_type(self) -> bool:
        return self.user_type == self.UserType.STAFF

    @property
    def subscription_days_left(self):
        if not self.subscription_renews_at:
            return None
        return (self.subscription_renews_at - timezone.now().date()).days

    @property
    def is_subscription_expiring(self) -> bool:
        days_left = self.subscription_days_left
        return days_left is not None and days_left <= 7

    @property
    def subscription_status_label(self) -> str:
        mapping = {
            "trial": _("Trial"),
            "active": _("Active"),
            "grace": _("Grace period"),
            "expired": _("Expired"),
        }
        key = (self.subscription_status or "").lower()
        return mapping.get(key, key.capitalize() or _("Pending"))

@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """Create or sync the related profile whenever a user is saved."""
    today = timezone.now().date()
    default_type = (
        UserProfile.UserType.STAFF
        if instance.is_staff
        else UserProfile.UserType.CLIENT_PARTNER
    )
    profile, created_profile = UserProfile.objects.get_or_create(
        user=instance,
        defaults={
            "user_type": default_type,
            "subscription_started_at": today,
            "subscription_renews_at": today + timedelta(days=30),
        },
    )
    updated_fields = []
    if profile.user_type == UserProfile.UserType.CLIENT_PARTNER and instance.is_staff:
        profile.user_type = UserProfile.UserType.STAFF
        updated_fields.append("user_type")
    if not profile.subscription_started_at:
        profile.subscription_started_at = today
        updated_fields.append("subscription_started_at")
    if not profile.subscription_renews_at:
        profile.subscription_renews_at = today + timedelta(days=30)
        updated_fields.append("subscription_renews_at")
    if updated_fields:
        profile.save(update_fields=updated_fields)


def location_image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return f'locations/{instance.location.id}/{name}.jpg'

def event_image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return f'events/{instance.event.id}/{name}.jpg'

class ImageLocation(OptimizedImageModel):
    location = models.ForeignKey("guard.Location", on_delete=models.CASCADE, related_name="images")
    
    class Meta:
        verbose_name = _("Location Image")
        verbose_name_plural = _("Location Images")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the upload_to for this specific model
        self._meta.get_field('image').upload_to = location_image_path
        self._meta.get_field('image_mobile').upload_to = location_image_path


class ImageEvent(OptimizedImageModel):
    event = models.ForeignKey("guard.Event", on_delete=models.CASCADE, related_name="images")
    
    class Meta:
        verbose_name = _("Event Image")
        verbose_name_plural = _("Event Images")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the upload_to for this specific model
        self._meta.get_field('image').upload_to = event_image_path
        self._meta.get_field('image_mobile').upload_to = event_image_path

class LocationCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Location Category")
        verbose_name_plural = _("Location Categories")
        
    def __str__(self):
        return self.name  

class Location(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(LocationCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='locations', verbose_name=_("Category"))
    name = models.CharField(max_length=255)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True, related_name='locations', verbose_name=_("Country"))
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='locations', verbose_name=_("City"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_active_ads = models.BooleanField(default=False, verbose_name=_("Active Ads"))
    story = HTMLField(verbose_name=_("Story"))
    openFrom = models.TimeField(verbose_name=_("Open From"),blank=True,null=True, help_text=_("Add opening hours if the location is open from a specific time"))
    openTo = models.TimeField(verbose_name=_("Open To"),blank=True,null=True, help_text=_("Add opening hours if the location is open to a specific time"))
    admissionFee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Admission Fee"),blank=True,null=True, help_text=_("Add admission fee if the location has a specific admission fee"))
    
    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    def __str__(self):
        return self.name
    
class Event(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='events', verbose_name=_("Client"))
    name = models.CharField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='events', verbose_name=_("Location"))
    startDate = models.DateField(verbose_name=_("Start Date"))
    endDate = models.DateField(verbose_name=_("End Date"))
    time = models.TimeField(verbose_name=_("Time"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    description = HTMLField(verbose_name=_("Description"))
    
    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.name

