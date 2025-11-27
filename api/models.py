from django.db import models
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _

# LANGUAGE_CHOICES removed as we use modeltranslation

class Page(models.Model):
    slug = models.SlugField(unique=True, verbose_name=_("URL Slug"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    content = HTMLField(verbose_name=_("Content"))
    
    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ['slug']

    def __str__(self):
        return self.title