from modeltranslation.translator import register, TranslationOptions
from .models import Location, LocationCategory, Event, EventCategory

@register(Location)
class LocationTranslationOptions(TranslationOptions):
    fields = ('name', 'story',)

@register(LocationCategory)
class LocationCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Event)
class EventTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)

@register(EventCategory)
class EventCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
