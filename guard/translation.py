from modeltranslation.translator import register, TranslationOptions
from .models import Location

@register(Location)
class LocationTranslationOptions(TranslationOptions):
    fields = ('name', 'story',)
