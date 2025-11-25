import graphene
from graphene_django import DjangoObjectType
from .models import Page

class PageType(DjangoObjectType):
    class Meta:
        model = Page
        fields = "__all__"


class Query(graphene.ObjectType):
    all_pages = graphene.List(PageType)
    pages_by_language = graphene.List(PageType, language=graphene.String(required=True))
    page = graphene.Field(PageType, slug=graphene.String(required=True), language=graphene.String())
    available_languages = graphene.List(graphene.String, slug=graphene.String(required=True))
    active_pages = graphene.List(PageType)
    active_pages_by_language = graphene.List(PageType, language=graphene.String(required=True))

    def resolve_all_pages(self, info):
        return Page.objects.all()

    def resolve_pages_by_language(self, info, language):
        return Page.objects.filter(language=language)

    def resolve_page(self, info, slug, language='en'):
        return Page.get_page(slug, language)

    def resolve_available_languages(self, info, slug):
        return list(Page.get_available_languages(slug))

    def resolve_active_pages(self, info):
        return Page.objects.filter(is_active=True)

    def resolve_active_pages_by_language(self, info, language):
        return Page.objects.filter(language=language, is_active=True)

schema = graphene.Schema(query=Query)