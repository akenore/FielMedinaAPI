from django.db import models
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _

# Language choices
LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('fr', 'Français'),
]

# Page model with language support
class Page(models.Model):
    # Common fields (not translatable)
    slug = models.SlugField(unique=True, verbose_name=_("URL Slug"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Translatable fields
    language = models.CharField(
        max_length=2, 
        choices=LANGUAGE_CHOICES, 
        default='en',
        verbose_name=_("Language")
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    content = HTMLField(verbose_name=_("Content"))
    
    class Meta:
        unique_together = ['slug', 'language']
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ['slug', 'language']

    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"
    
    @classmethod
    def get_page(cls, slug, language='en'):
        """Get a page by slug and language"""
        try:
            return cls.objects.get(slug=slug, language=language, is_active=True)
        except cls.DoesNotExist:
            # Fallback to English if requested language doesn't exist
            if language != 'en':
                try:
                    return cls.objects.get(slug=slug, language='en', is_active=True)
                except cls.DoesNotExist:
                    return None
            return None
    
    @classmethod
    def get_available_languages(cls, slug):
        """Get all available languages for a page"""
        return cls.objects.filter(slug=slug, is_active=True).values_list('language', flat=True)