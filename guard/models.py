import os
import uuid


from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from django.core.files.uploadedfile import UploadedFile
from shared.models import OptimizedImageModel
from shared.utils import optimize_image
from shared.models import UserProfile


def location_image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return f"locations/{instance.location.id}/{name}.jpg"


def event_image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return f"events/{instance.event.id}/{name}.jpg"


def hiking_image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return f"hikings/{instance.hiking.id}/{name}.jpg"


def ad_image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return f"ads/{instance.ad.id}/{name}.jpg"


class ImageAd(OptimizedImageModel):
    ad = models.ForeignKey("guard.Ad", on_delete=models.CASCADE, related_name="images")

    class Meta:
        verbose_name = _("Ad Image")
        verbose_name_plural = _("Ad Images")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field("image").upload_to = ad_image_path
        self._meta.get_field("image_mobile").upload_to = ad_image_path


class ImageHiking(OptimizedImageModel):
    hiking = models.ForeignKey(
        "guard.Hiking", on_delete=models.CASCADE, related_name="images"
    )

    class Meta:
        verbose_name = _("Hiking Image")
        verbose_name_plural = _("Hiking Images")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field("image").upload_to = hiking_image_path
        self._meta.get_field("image_mobile").upload_to = hiking_image_path


class ImageLocation(OptimizedImageModel):
    location = models.ForeignKey(
        "guard.Location", on_delete=models.CASCADE, related_name="images"
    )

    class Meta:
        verbose_name = _("Location Image")
        verbose_name_plural = _("Location Images")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field("image").upload_to = location_image_path
        self._meta.get_field("image_mobile").upload_to = location_image_path


class ImageEvent(OptimizedImageModel):
    event = models.ForeignKey(
        "guard.Event", on_delete=models.CASCADE, related_name="images"
    )

    class Meta:
        verbose_name = _("Event Image")
        verbose_name_plural = _("Event Images")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field("image").upload_to = event_image_path
        self._meta.get_field("image_mobile").upload_to = event_image_path


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
    category = models.ForeignKey(
        LocationCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations",
        verbose_name=_("Category"),
    )
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        "cities_light.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations",
        verbose_name=_("Country"),
    )
    city = models.ForeignKey(
        "cities_light.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations",
        verbose_name=_("City"),
    )
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_active_ads = models.BooleanField(default=False, verbose_name=_("Active Ads"))
    story = HTMLField(verbose_name=_("Story"))
    openFrom = models.TimeField(
        verbose_name=_("Open From"),
        blank=True,
        null=True,
        help_text=_("Add opening hours if the location is open from a specific time"),
    )
    openTo = models.TimeField(
        verbose_name=_("Open To"),
        blank=True,
        null=True,
        help_text=_("Add opening hours if the location is open to a specific time"),
    )
    admissionFee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Admission Fee"),
        blank=True,
        null=True,
        help_text=_("Add admission fee if the location has a specific admission fee"),
    )

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    def __str__(self):
        return self.name


class Hiking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    city = models.ForeignKey(
        "cities_light.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hikings",
        verbose_name=_("Cities"),
    )
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"))
    location = models.ManyToManyField("Location", verbose_name=_("Location"))

    class Meta:
        verbose_name = _("Hiking")
        verbose_name_plural = _("Hikings")

    def __str__(self):
        return self.name


class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Event Category")
        verbose_name_plural = _("Event Categories")

    def __str__(self):
        return self.name


class Event(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name=_("Client"),
    )
    city = models.ForeignKey(
        "cities_light.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name=_("City"),
    )
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name=_("Category"),
    )
    name = models.CharField(max_length=255)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name=_("Location"),
    )
    startDate = models.DateField(verbose_name=_("Start Date"))
    endDate = models.DateField(verbose_name=_("End Date"))
    time = models.TimeField(verbose_name=_("Time"))
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Price")
    )
    link = models.URLField(verbose_name=_("The link to subscribe"))
    short_link = models.URLField(blank=True, null=True)
    short_id = models.CharField(max_length=50, blank=True, null=True)
    description = HTMLField(verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.name


class Tip(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    city = models.ForeignKey(
        "cities_light.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tips",
        verbose_name=_("Cities"),
    )
    description = models.TextField()
    location = models.ManyToManyField("Location", verbose_name=_("Location"))

    class Meta:
        verbose_name = _("Tip")
        verbose_name_plural = _("Tips")

    def __str__(self):
        return self.description[:50]


class Ad(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(
        max_length=255, verbose_name=_("Add a name"), blank=True, null=True
    )
    city = models.ForeignKey(
        "cities_light.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ads",
        verbose_name=_("City"),
    )
    client = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ads",
        verbose_name=_("Client"),
    )
    image_mobile = models.ImageField(
        upload_to="ads/mobile/",
        help_text=_("Size: 320x50 pixels"),
        verbose_name=_("Mobile Image (320x50)"),
        null=True,
        blank=True,
    )
    image_tablet = models.ImageField(
        upload_to="ads/tablet/",
        help_text=_("Size: 728x90 pixels"),
        verbose_name=_("Tablet Image (728x90)"),
        null=True,
        blank=True,
    )
    link = models.URLField()
    short_link = models.URLField(blank=True, null=True)
    short_id = models.CharField(max_length=50, blank=True, null=True)
    clicks = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Ad")
        verbose_name_plural = _("Ads")

    def save(self, *args, **kwargs):
        if not self.name:
            ref = uuid.uuid4().hex[:6].upper()
            self.name = f"ADS-{ref}"

        for field_name in ["image_mobile", "image_tablet"]:
            field = getattr(self, field_name)
            if field and isinstance(field.file, UploadedFile):
                optimized = optimize_image(field)
                if optimized:
                    _, content = optimized
                    ext = ".jpg"
                    unique_filename = f"{uuid.uuid4()}{ext}"
                    content.name = unique_filename
                    setattr(self, field_name, content)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or self.link


@receiver(post_delete, sender=Ad)
def cleanup_ad_images(sender, instance, **kwargs):
    """
    Delete image files from filesystem when Ad object is deleted.
    """
    for field_name in ["image_mobile", "image_tablet"]:
        field = getattr(instance, field_name)
        if field and field.name:
            try:
                if os.path.isfile(field.path):
                    os.remove(field.path)
            except Exception:
                pass


class TransportType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("Transport Type")
        verbose_name_plural = _("Transport Types")

    def __str__(self):
        return self.name


class PublicTransport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    transportType = models.ForeignKey(
        TransportType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_transports",
        verbose_name=_("Transport Type"),
    )

    city = models.ForeignKey(
        "cities_light.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicTransports",
        verbose_name=_("City"),
    )

    fromRegion = models.ForeignKey(
        "cities_light.SubRegion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicTransportsFromRegion",
        verbose_name=_("From region"),
    )
    toRegion = models.ForeignKey(
        "cities_light.SubRegion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicTransportsToRegion",
        verbose_name=_("To region"),
    )

    class Meta:
        verbose_name = _("Public Transport")
        verbose_name_plural = _("Public Transports")

    def __str__(self):
        return self.city.name


class PublicTransportTime(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publicTransport = models.ForeignKey(
        PublicTransport,
        on_delete=models.CASCADE,
        related_name="publicTransportTimes",
        verbose_name=_("Public Transport"),
    )
    time = models.TimeField(verbose_name=_("Time"))

    class Meta:
        verbose_name = _("Public Transport Time")
        verbose_name_plural = _("Public Transport Times")

    def __str__(self):
        return self.publicTransport.city.name
