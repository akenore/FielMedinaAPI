import graphene
from graphene_django import DjangoObjectType
from .models import Page

class PageType(DjangoObjectType):
    class Meta:
        model = Page
        fields = "__all__"


class Query(graphene.ObjectType):
    all_pages = graphene.List(PageType)
    page = graphene.Field(PageType, slug=graphene.String(required=True))
    active_pages = graphene.List(PageType)

    def resolve_all_pages(self, info):
        return Page.objects.all()

    def resolve_page(self, info, slug):
        from django.db.models import Q
        return Page.objects.filter(Q(slug_en=slug) | Q(slug_fr=slug)).first()

    def resolve_active_pages(self, info):
        return Page.objects.filter(is_active=True)

schema = graphene.Schema(query=Query)