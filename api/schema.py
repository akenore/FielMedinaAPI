import graphene
from graphene_django import DjangoObjectType

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
)

from cities_light.models import City
from shared.models import Page


class ImageLocationType(DjangoObjectType):
    class Meta:
        model = ImageLocation
        fields = "__all__"


class LocationCategoryType(DjangoObjectType):
    class Meta:
        model = LocationCategory
        fields = "__all__"


class LocationType(DjangoObjectType):
    images = graphene.List(ImageLocationType)

    class Meta:
        model = Location
        fields = "__all__"

    def resolve_images(self, info):
        return self.images.all()


class ImageHikingType(DjangoObjectType):
    class Meta:
        model = ImageHiking
        fields = "__all__"


class HikingType(DjangoObjectType):
    images = graphene.List(ImageHikingType)

    class Meta:
        model = Hiking
        fields = "__all__"

    def resolve_images(self, info):
        return self.images.all()


class EventCategoryType(DjangoObjectType):
    class Meta:
        model = EventCategory
        fields = "__all__"


class ImageEventType(DjangoObjectType):
    class Meta:
        model = ImageEvent
        fields = "__all__"


class EventType(DjangoObjectType):
    images = graphene.List(ImageEventType)

    class Meta:
        model = Event
        fields = "__all__"

    def resolve_images(self, info):
        return self.images.all()


class ImageAdType(DjangoObjectType):
    class Meta:
        model = ImageAd
        fields = "__all__"


class AdType(DjangoObjectType):
    images = graphene.List(ImageAdType)

    class Meta:
        model = Ad
        fields = "__all__"

    def resolve_images(self, info):
        return self.images.all() if hasattr(self, "images") else []


class TipType(DjangoObjectType):
    class Meta:
        model = Tip
        fields = "__all__"


class CityType(DjangoObjectType):
    class Meta:
        model = City
        fields = ("id", "name", "region", "country")


class PublicTransportTypeType(DjangoObjectType):
    class Meta:
        model = PublicTransportType
        fields = "__all__"


class PublicTransportTimeType(DjangoObjectType):
    class Meta:
        model = PublicTransportTime
        fields = "__all__"


class PublicTransportNodeType(DjangoObjectType):
    times = graphene.List(PublicTransportTimeType)

    class Meta:
        model = PublicTransport
        fields = "__all__"

    def resolve_times(self, info):
        return self.publicTransportTimes.all()


class Query(graphene.ObjectType):
    # Pages
    pages = graphene.List(
        lambda: PageType,
        is_active=graphene.Boolean(required=False),
    )
    page = graphene.Field(lambda: PageType, slug=graphene.String(required=True))
    # Locations
    locations = graphene.List(
        LocationType,
        city_id=graphene.Int(required=False),
        category_id=graphene.Int(required=False),
    )
    location = graphene.Field(LocationType, id=graphene.ID(required=True))
    location_categories = graphene.List(LocationCategoryType)

    # Hiking
    hikings = graphene.List(
        HikingType,
        city_id=graphene.Int(required=False),
    )
    hiking = graphene.Field(HikingType, id=graphene.ID(required=True))

    # Events
    events = graphene.List(
        EventType,
        city_id=graphene.Int(required=False),
        category_id=graphene.Int(required=False),
    )
    event = graphene.Field(EventType, id=graphene.ID(required=True))
    event_categories = graphene.List(EventCategoryType)

    # Ads
    ads = graphene.List(
        AdType,
        city_id=graphene.Int(required=False),
        is_active=graphene.Boolean(required=False),
    )
    ad = graphene.Field(AdType, id=graphene.ID(required=True))

    # Tips (list only, no detail view)
    tips = graphene.List(
        TipType,
        city_id=graphene.Int(required=False),
    )

    # Public transport
    public_transports = graphene.List(
        PublicTransportNodeType,
        city_id=graphene.Int(required=False),
        type_id=graphene.Int(required=False),
        from_region_id=graphene.Int(required=False),
        to_region_id=graphene.Int(required=False),
    )
    public_transport = graphene.Field(
        PublicTransportNodeType,
        id=graphene.ID(required=True),
    )
    public_transport_types = graphene.List(PublicTransportTypeType)

    def resolve_pages(self, info, is_active=None):
        qs = Page.objects.all()
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs

    def resolve_page(self, info, slug):
        return Page.objects.filter(slug=slug).first()

    def resolve_locations(self, info, city_id=None, category_id=None):
        qs = (
            Location.objects.select_related("city", "country", "category")
            .prefetch_related("images")
        )
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        if category_id is not None:
            qs = qs.filter(category_id=category_id)
        return qs

    def resolve_location(self, info, id):
        return Location.objects.prefetch_related("images").filter(pk=id).first()

    def resolve_location_categories(self, info):
        return LocationCategory.objects.all()

    def resolve_hikings(self, info, city_id=None):
        qs = (
            Hiking.objects.select_related("city")
            .prefetch_related("images", "location")
        )
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        return qs

    def resolve_hiking(self, info, id):
        return Hiking.objects.prefetch_related("images", "location").filter(pk=id).first()

    def resolve_events(self, info, city_id=None, category_id=None):
        qs = (
            Event.objects.select_related("city", "category", "client", "location")
            .prefetch_related("images")
        )
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        if category_id is not None:
            qs = qs.filter(category_id=category_id)
        return qs

    def resolve_event(self, info, id):
        return (
            Event.objects.prefetch_related("images", "location", "category")
            .filter(pk=id)
            .first()
        )

    def resolve_event_categories(self, info):
        return EventCategory.objects.all()

    def resolve_ads(self, info, city_id=None, is_active=None):
        qs = Ad.objects.select_related("city", "client")
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs

    def resolve_ad(self, info, id):
        return Ad.objects.filter(pk=id).first()

    def resolve_tips(self, info, city_id=None):
        qs = Tip.objects.select_related("city")
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        return qs

    def resolve_public_transports(
        self,
        info,
        city_id=None,
        type_id=None,
        from_region_id=None,
        to_region_id=None,
    ):
        qs = (
            PublicTransport.objects.select_related(
                "city", "publicTransportType", "fromRegion", "toRegion"
            ).prefetch_related("publicTransportTimes")
        )
        if city_id is not None:
            qs = qs.filter(city_id=city_id)
        if type_id is not None:
            qs = qs.filter(publicTransportType_id=type_id)
        if from_region_id is not None:
            qs = qs.filter(fromRegion_id=from_region_id)
        if to_region_id is not None:
            qs = qs.filter(toRegion_id=to_region_id)
        return qs

    def resolve_public_transport(self, info, id):
        return (
            PublicTransport.objects.select_related(
                "city", "publicTransportType", "fromRegion", "toRegion"
            )
            .prefetch_related("publicTransportTimes")
            .filter(pk=id)
            .first()
        )

    def resolve_public_transport_types(self, info):
        return PublicTransportType.objects.all()


class PageType(DjangoObjectType):
    class Meta:
        model = Page
        fields = "__all__"


schema = graphene.Schema(query=Query)

