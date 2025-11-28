from datetime import timedelta
import os
from io import BytesIO
from PIL import Image as PilImage
from django.core.files.base import ContentFile

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

User = get_user_model()

class UserProfile(models.Model):
    class UserType(models.TextChoices):
        STAFF = "staff", _("Staff")
        CLIENT_PARTNER = "client_partner", _("Client / Partenaire")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    user_type = models.CharField(
        max_length=32,
        choices=UserType.choices,
        default=UserType.CLIENT_PARTNER,
    )
    subscription_plan = models.CharField(
        max_length=100,
        blank=True,
        default="Trial",
        help_text=_("Placeholder until Konnect subscription is attached."),
    )
    subscription_status = models.CharField(
        max_length=32,
        blank=True,
        default="trial",
    )
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

class Image(models.Model):
    location = models.ForeignKey("guard.Location", on_delete=models.CASCADE, related_name="images")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=location_image_path)
    image_mobile = models.ImageField(upload_to=location_image_path, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def save(self, *args, **kwargs):
        if self.image and (not self.pk or hasattr(self.image, 'file')):
            try:
                img = PilImage.open(self.image)
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img_tablet = img.copy()
                if img_tablet.width > 1920:
                    ratio = 1920 / float(img_tablet.width)
                    height = int((float(img_tablet.height) * float(ratio)))
                    img_tablet = img_tablet.resize((1920, height), PilImage.Resampling.LANCZOS)
                
                output_tablet = BytesIO()
                img_tablet.save(output_tablet, format='JPEG', quality=80)
                output_tablet.seek(0)
                
                original_name = os.path.basename(self.image.name)
                name_base, _ = os.path.splitext(original_name)
                filename = f"{name_base}.jpg"
                
                self.image = ContentFile(output_tablet.read(), name=filename)

                img_mobile = img.copy()
                if img_mobile.width > 500:
                    ratio = 500 / float(img_mobile.width)
                    height = int((float(img_mobile.height) * float(ratio)))
                    img_mobile = img_mobile.resize((500, height), PilImage.Resampling.LANCZOS)
                
                output_mobile = BytesIO()
                img_mobile.save(output_mobile, format='JPEG', quality=80)
                output_mobile.seek(0)
                
                self.image_mobile = ContentFile(output_mobile.read(), name=f"mobile_{filename}")
                
                try:
                    if self.image.storage.exists(self.image.name):
                        self.image.storage.delete(self.image.name)
                except Exception:
                    pass
                
            except Exception as e:
                print(f"Error processing image: {e}")
                pass

        super().save(*args, **kwargs)

@receiver(post_delete, sender=Image)
def cleanup_image_files(sender, instance, **kwargs):
    """Delete image files when the Image record is deleted."""
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)
        
    if instance.image_mobile and os.path.isfile(instance.image_mobile.path):
        os.remove(instance.image_mobile.path)
            
    try:
        if instance.image:
            directory = os.path.dirname(instance.image.path)
            if os.path.exists(directory) and not os.listdir(directory):
                os.rmdir(directory)
    except Exception:
        pass
    
class Location(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True, related_name='locations', verbose_name=_("Country"))
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='locations', verbose_name=_("City"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_active_ads = models.BooleanField(default=False, verbose_name=_("Active Ads"))
    story = HTMLField(verbose_name=_("Story"))
    
    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    def __str__(self):
        return self.name
    
    
    