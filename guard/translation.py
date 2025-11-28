from modeltranslation.translator import register, TranslationOptions
from .models import Location, LocationCategory

@register(Location)
class LocationTranslationOptions(TranslationOptions):
    fields = ('name', 'story',)

@register(LocationCategory)
class LocationCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
