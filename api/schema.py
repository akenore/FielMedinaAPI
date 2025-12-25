import strawberry
import strawberry_django
from strawberry import auto
from typing import List, Optional
import math
from django.db.models import Q
import datetime
import uuid
from django.conf import settings
from graphql.validation import NoSchemaIntrospectionCustomRule
from strawberry.extensions import AddValidationRules


from guard.models import (
    Location,
    LocationCategory,
    Hiking,
    Event,
    EventCategory,
    Ad,
    Tip,
    PublicTransport,
    PublicTransportType,
    PublicTransportTime,
    ImageLocation,
    ImageHiking,
    ImageEvent,
    ImageAd,
    Partner,
    Sponsor,
    Weekday,
)

from cities_light.models import City
from shared.models import Page, UserPreference


@strawberry.type
class ImageFieldType:
    @strawberry.field
    def url(self, root) -> str:
        return root.url if root else ""

    @strawberry.field
    def name(self, root) -> str:
        return root.name if root else ""

    @strawberry.field
    def path(self, root) -> str:
        return root.path if root and hasattr(root, "path") else ""

    @strawberry.field
    def size(self, root) -> int:
        return root.size if root and hasattr(root, "size") else 0

    @strawberry.field
    def width(self, root) -> Optional[int]:
        try:
            return root.width if root and hasattr(root, "width") else None
        except Exception:
            return None

    @strawberry.field
    def height(self, root) -> Optional[int]:
        try:
            return root.height if root and hasattr(root, "height") else None
        except Exception:
            return None


@strawberry_django.type(Page)
class PageType:
    id: auto
    slug: auto
    slug_en: str
    slug_fr: str
    is_active: auto
    created_at: auto
    updated_at: auto
    title: auto
    title_en: str
    title_fr: str
    content: str
    content_en: str
    content_fr: str


@strawberry_django.type(Weekday)
class WeekdayType:
    id: auto
    day: auto


@strawberry_django.type(Partner)
class PartnerType:
    id: auto
    name: auto
    link: auto

    @strawberry.field
    def image(self, root) -> ImageFieldType:
        return root.image


@strawberry_django.type(Sponsor)
class SponsorType:
    id: auto
    name: auto
    link: auto

    @strawberry.field
    def image(self, root) -> ImageFieldType:
        return root.image


@strawberry_django.type(ImageLocation)
class ImageLocationType:
    id: auto
    created_at: auto

    @strawberry.field
    def image(self, root) -> ImageFieldType:
        return root.image

    @strawberry.field
    def image_mobile(self, root) -> Optional[ImageFieldType]:
        return root.image_mobile


@strawberry_django.type(LocationCategory)
class LocationCategoryType:
    id: auto
    name: auto
    name_en: str
    name_fr: str
    created_at: auto
    updated_at: auto


@strawberry_django.type(Location)
class LocationType:
    id: auto
    created_at: auto
    name: auto
    name_en: str
    name_fr: str
    longitude: auto
    latitude: auto
    is_active_ads: auto
    story: str
    story_en: str
    story_fr: str
    open_from: auto = strawberry_django.field(field_name="openFrom")
    open_to: auto = strawberry_django.field(field_name="openTo")
    admission_fee: auto = strawberry_django.field(field_name="admissionFee")
    city: Optional["CityType"]
    category: Optional[LocationCategoryType]

    @strawberry.field
    def images(self, root) -> List[ImageLocationType]:
        return root.images.all()

    @strawberry.field
    def open_days(self, root) -> List[WeekdayType]:
        return root.openDays.all()


@strawberry_django.type(ImageHiking)
class ImageHikingType:
    id: auto
    created_at: auto

    @strawberry.field
    def image(self, root) -> ImageFieldType:
        return root.image

    @strawberry.field
    def image_mobile(self, root) -> Optional[ImageFieldType]:
        return root.image_mobile


@strawberry_django.type(Hiking)
class HikingType:
    id: auto
    created_at: auto
    updated_at: auto
    name: auto
    name_en: str
    name_fr: str
    description: auto
    description_en: str
    description_fr: str
    city: Optional["CityType"]

    @strawberry.field
    def images(self, root) -> List[ImageHikingType]:
        return root.images.all()

    @strawberry.field
    def location(self, root) -> List[LocationType]:
        return root.location.all()


@strawberry_django.type(EventCategory)
class EventCategoryType:
    id: auto
    name: auto
    name_en: str
    name_fr: str
    created_at: auto
    updated_at: auto


@strawberry_django.type(ImageEvent)
class ImageEventType:
    id: auto
    created_at: auto

    @strawberry.field
    def image(self, root) -> ImageFieldType:
        return root.image

    @strawberry.field
    def image_mobile(self, root) -> Optional[ImageFieldType]:
        return root.image_mobile


@strawberry_django.type(Event)
class EventType:
    id: auto
    created_at: auto
    name: auto
    name_en: str
    name_fr: str
    start_date: auto = strawberry_django.field(field_name="startDate")
    end_date: auto = strawberry_django.field(field_name="endDate")
    time: auto
    price: auto
    link: auto
    short_link: auto
    short_id: auto
    description: str
    description_en: str
    description_fr: str
    city: Optional["CityType"]
    category: Optional[EventCategoryType]
    location: Optional[LocationType]

    @strawberry.field
    def images(self, root) -> List[ImageEventType]:
        return root.images.all()


@strawberry_django.type(ImageAd)
class ImageAdType:
    id: auto
    created_at: auto

    @strawberry.field
    def image(self, root) -> ImageFieldType:
        return root.image

    @strawberry.field
    def image_mobile(self, root) -> Optional[ImageFieldType]:
        return root.image_mobile


@strawberry_django.type(Ad)
class AdType:
    id: auto
    created_at: auto
    updated_at: auto
    name: auto
    link: auto
    short_link: auto
    short_id: auto
    clicks: auto
    is_active: auto
    city: Optional["CityType"]

    @strawberry.field
    def image_mobile(self, root) -> Optional[ImageFieldType]:
        return root.image_mobile

    @strawberry.field
    def image_tablet(self, root) -> Optional[ImageFieldType]:
        return root.image_tablet

    @strawberry.field
    def images(self, root) -> List[ImageAdType]:
        return root.images.all() if hasattr(root, "images") else []


@strawberry_django.type(Tip)
class TipType:
    id: auto
    created_at: auto
    updated_at: auto
    description: str
    description_en: str
    description_fr: str
    city: Optional["CityType"]


@strawberry_django.type(City)
class CityType:
    id: auto
    name: auto

    @strawberry.field
    def name_en(self, root) -> Optional[str]:
        # root.translations is a dict like {'en': ['Name'], ...}
        translations = getattr(root, "translations", {})
        en_names = translations.get("en", [])
        return en_names[0] if en_names else root.name

    @strawberry.field
    def name_fr(self, root) -> Optional[str]:
        translations = getattr(root, "translations", {})
        fr_names = translations.get("fr", [])
        return fr_names[0] if fr_names else root.name

    @strawberry.field
    def name_ar(self, root) -> Optional[str]:
        translations = getattr(root, "translations", {})
        ar_names = translations.get("ar", [])
        return ar_names[0] if ar_names else root.name

    @strawberry.field
    def region(self, root) -> Optional[str]:
        return root.region.name if hasattr(root, "region") and root.region else None

    @strawberry.field
    def region_en(self, root) -> Optional[str]:
        if not hasattr(root, "region") or not root.region:
            return None
        translations = getattr(root.region, "translations", {})
        en_names = translations.get("en", [])
        return en_names[0] if en_names else root.region.name

    @strawberry.field
    def region_fr(self, root) -> Optional[str]:
        if not hasattr(root, "region") or not root.region:
            return None
        translations = getattr(root.region, "translations", {})
        fr_names = translations.get("fr", [])
        return fr_names[0] if fr_names else root.region.name

    @strawberry.field
    def region_ar(self, root) -> Optional[str]:
        if not hasattr(root, "region") or not root.region:
            return None
        translations = getattr(root.region, "translations", {})
        ar_names = translations.get("ar", [])
        return ar_names[0] if ar_names else root.region.name

    @strawberry.field
    def country(self, root) -> Optional[str]:
        return root.country.name if hasattr(root, "country") and root.country else None

    @strawberry.field
    def country_en(self, root) -> Optional[str]:
        if not hasattr(root, "country") or not root.country:
            return None
        translations = getattr(root.country, "translations", {})
        en_names = translations.get("en", [])
        return en_names[0] if en_names else root.country.name

    @strawberry.field
    def country_fr(self, root) -> Optional[str]:
        if not hasattr(root, "country") or not root.country:
            return None
        translations = getattr(root.country, "translations", {})
        fr_names = translations.get("fr", [])
        return fr_names[0] if fr_names else root.country.name

    @strawberry.field
    def country_ar(self, root) -> Optional[str]:
        if not hasattr(root, "country") or not root.country:
            return None
        translations = getattr(root.country, "translations", {})
        ar_names = translations.get("ar", [])
        return ar_names[0] if ar_names else root.country.name


@strawberry_django.type(PublicTransportType)
class PublicTransportTypeType:
    id: auto
    name: auto
    name_en: str
    name_fr: str


@strawberry_django.type(PublicTransportTime)
class PublicTransportTimeType:
    id: auto
    created_at: auto
    updated_at: auto
    time: auto


@strawberry_django.type(PublicTransport)
class PublicTransportNodeType:
    id: auto
    created_at: auto
    updated_at: auto
    city: Optional[CityType]

    @strawberry.field
    def public_transport_type(self, root) -> Optional[PublicTransportTypeType]:
        return root.publicTransportType

    @strawberry.field
    def from_region(self, root) -> Optional[str]:
        return root.fromRegion.name if root.fromRegion else None

    @strawberry.field
    def from_region_en(self, root) -> Optional[str]:
        if not root.fromRegion:
            return None
        translations = getattr(root.fromRegion, "translations", {})
        names = translations.get("en", [])
        return names[0] if names else root.fromRegion.name

    @strawberry.field
    def from_region_fr(self, root) -> Optional[str]:
        if not root.fromRegion:
            return None
        translations = getattr(root.fromRegion, "translations", {})
        names = translations.get("fr", [])
        return names[0] if names else root.fromRegion.name

    @strawberry.field
    def from_region_ar(self, root) -> Optional[str]:
        if not root.fromRegion:
            return None
        translations = getattr(root.fromRegion, "translations", {})
        names = translations.get("ar", [])
        return names[0] if names else root.fromRegion.name

    @strawberry.field
    def to_region(self, root) -> Optional[str]:
        return root.toRegion.name if root.toRegion else None

    @strawberry.field
    def to_region_en(self, root) -> Optional[str]:
        if not root.toRegion:
            return None
        translations = getattr(root.toRegion, "translations", {})
        names = translations.get("en", [])
        return names[0] if names else root.toRegion.name

    @strawberry.field
    def to_region_fr(self, root) -> Optional[str]:
        if not root.toRegion:
            return None
        translations = getattr(root.toRegion, "translations", {})
        names = translations.get("fr", [])
        return names[0] if names else root.toRegion.name

    @strawberry.field
    def to_region_ar(self, root) -> Optional[str]:
        if not root.toRegion:
            return None
        translations = getattr(root.toRegion, "translations", {})
        names = translations.get("ar", [])
        return names[0] if names else root.toRegion.name

    @strawberry.field
    def times(self, root) -> List[PublicTransportTimeType]:
        return root.publicTransportTimes.all()


@strawberry.type
class Query:
    @strawberry.field
    def pages(self, is_active: Optional[bool] = None) -> List[PageType]:
        qs = Page.objects.all()
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs

    @strawberry.field
    def page(self, slug: str) -> Optional[PageType]:
        return (
            Page.objects.filter(Q(slug_en=slug) | Q(slug_fr=slug))
            .filter(is_active=True)
            .first()
        )

    @strawberry.field
    def locations(
        self, city_id: Optional[int] = None, category_id: Optional[int] = None
    ) -> List[LocationType]:
        qs = Location.objects.select_related(
            "city", "country", "category"
        ).prefetch_related("images")
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        if category_id is not None:
            qs = qs.filter(category_id=category_id)
        return qs

    @strawberry.field
    def location(self, id: strawberry.ID) -> Optional[LocationType]:
        return Location.objects.prefetch_related("images").filter(pk=id).first()

    @strawberry.field
    def location_categories(self) -> List[LocationCategoryType]:
        return LocationCategory.objects.all()

    @strawberry.field
    def hikings(self, city_id: Optional[int] = None) -> List[HikingType]:
        qs = Hiking.objects.select_related("city").prefetch_related(
            "images", "location"
        )
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        return qs

    @strawberry.field
    def hiking(self, id: strawberry.ID) -> Optional[HikingType]:
        return (
            Hiking.objects.prefetch_related("images", "location").filter(pk=id).first()
        )

    @strawberry.field
    def events(
        self, city_id: Optional[int] = None, category_id: Optional[int] = None
    ) -> List[EventType]:
        qs = Event.objects.select_related(
            "city", "category", "client", "location"
        ).prefetch_related("images")
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        if category_id is not None:
            qs = qs.filter(category_id=category_id)
        return qs

    @strawberry.field
    def event(self, id: strawberry.ID) -> Optional[EventType]:
        return (
            Event.objects.prefetch_related("images", "location", "category")
            .filter(pk=id)
            .first()
        )

    @strawberry.field
    def event_categories(self) -> List[EventCategoryType]:
        return EventCategory.objects.all()

    @strawberry.field
    def ads(
        self, city_id: Optional[int] = None, is_active: Optional[bool] = None
    ) -> List[AdType]:
        qs = Ad.objects.select_related("city", "client")
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs

    @strawberry.field
    def ad(self, id: strawberry.ID) -> Optional[AdType]:
        return Ad.objects.filter(pk=id).first()

    @strawberry.field
    def tips(self, city_id: Optional[int] = None) -> List[TipType]:
        qs = Tip.objects.select_related("city")
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        return qs

    @strawberry.field
    def public_transports(
        self,
        city_id: Optional[int] = None,
        type_id: Optional[int] = None,
        from_region_id: Optional[int] = None,
        to_region_id: Optional[int] = None,
    ) -> List[PublicTransportNodeType]:
        qs = PublicTransport.objects.select_related(
            "city", "publicTransportType", "fromRegion", "toRegion"
        ).prefetch_related("publicTransportTimes")
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        if type_id is not None:
            qs = qs.filter(publicTransportType_id=type_id)
        if from_region_id is not None:
            qs = qs.filter(fromRegion_id=from_region_id)
        if to_region_id is not None:
            qs = qs.filter(toRegion_id=to_region_id)
        return qs

    @strawberry.field
    def public_transport(self, id: strawberry.ID) -> Optional[PublicTransportNodeType]:
        return (
            PublicTransport.objects.select_related(
                "city", "publicTransportType", "fromRegion", "toRegion"
            )
            .prefetch_related("publicTransportTimes")
            .filter(pk=id)
            .first()
        )

    @strawberry.field
    def public_transport_types(self) -> List[PublicTransportTypeType]:
        return PublicTransportType.objects.all()

    @strawberry.field
    def nearest_city(
        self, lat: float, lon: float, max_distance_km: Optional[float] = None
    ) -> Optional[CityType]:
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in km
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = (
                math.sin(dphi / 2) ** 2
                + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        candidates = (
            City.objects.exclude(latitude__isnull=True)
            .exclude(longitude__isnull=True)
            .values("id", "name", "latitude", "longitude")
        )

        nearest = None
        nearest_distance = None

        for city in candidates:
            distance = haversine(
                lat, lon, float(city["latitude"]), float(city["longitude"])
            )
            if max_distance_km is not None and distance > max_distance_km:
                continue
            if nearest_distance is None or distance < nearest_distance:
                nearest_distance = distance
                nearest = city["id"]

        if nearest is None:
            return None

        return City.objects.filter(pk=nearest).first()

    @strawberry.field
    def partners(self) -> List[PartnerType]:
        return Partner.objects.all()

    @strawberry.field
    def sponsor(self, id: strawberry.ID) -> Optional[SponsorType]:
        return Sponsor.objects.filter(pk=id).first()

    @strawberry.field
    def sponsors(self) -> List[SponsorType]:
        return Sponsor.objects.all()


@strawberry.type
class SyncUserPreferencePayload:
    ok: bool


@strawberry.type
class Mutation:
    @strawberry.mutation
    def sync_user_preference(
        self,
        user_uid: uuid.UUID,
        first_visit: bool,
        traveling_with: str,
        interests: List[str],
        updated_at: datetime.datetime,
    ) -> SyncUserPreferencePayload:
        obj, created = UserPreference.objects.get_or_create(
            user_uid=user_uid,
            defaults={
                "first_visit": first_visit,
                "traveling_with": traveling_with,
                "interests": interests,
                "updated_at": updated_at,
            },
        )

        if not created and updated_at > obj.updated_at:
            obj.first_visit = first_visit
            obj.traveling_with = traveling_with
            obj.interests = interests
            obj.save()

        return SyncUserPreferencePayload(ok=True)

    @strawberry.mutation
    def forget_me(self, user_uid: uuid.UUID) -> SyncUserPreferencePayload:
        UserPreference.objects.filter(user_uid=user_uid).delete()
        return SyncUserPreferencePayload(ok=True)


extensions = []
if not settings.DEBUG:
    extensions.append(AddValidationRules([NoSchemaIntrospectionCustomRule]))
schema = strawberry.Schema(query=Query, mutation=Mutation, extensions=extensions)
