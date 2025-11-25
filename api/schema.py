import graphene
from graphene_django import DjangoObjectType
from .models import Page

class PageType(DjangoObjectType):
    class Meta:
        model = Page
        fields = "__all__"

class PageInput(graphene.InputObjectType):
    slug = graphene.String(required=True)
    language = graphene.String(required=True)
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    is_active = graphene.Boolean()

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

class CreatePage(graphene.Mutation):
    class Arguments:
        input = PageInput(required=True)

    page = graphene.Field(PageType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        try:
            page = Page.objects.create(
                slug=input.slug,
                language=input.language,
                title=input.title,
                content=input.content,
                is_active=input.is_active if input.is_active is not None else True
            )
            return CreatePage(page=page, success=True, message="Page created successfully")
        except Exception as e:
            return CreatePage(page=None, success=False, message=str(e))

class UpdatePage(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = PageInput(required=True)

    page = graphene.Field(PageType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, input):
        try:
            page = Page.objects.get(id=id)
            page.slug = input.slug
            page.language = input.language
            page.title = input.title
            page.content = input.content
            if input.is_active is not None:
                page.is_active = input.is_active
            page.save()
            return UpdatePage(page=page, success=True, message="Page updated successfully")
        except Page.DoesNotExist:
            return UpdatePage(page=None, success=False, message="Page not found")
        except Exception as e:
            return UpdatePage(page=None, success=False, message=str(e))

class DeletePage(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        try:
            page = Page.objects.get(id=id)
            page.delete()
            return DeletePage(success=True, message="Page deleted successfully")
        except Page.DoesNotExist:
            return DeletePage(success=False, message="Page not found")
        except Exception as e:
            return DeletePage(success=False, message=str(e))

class Mutation(graphene.ObjectType):
    create_page = CreatePage.Field()
    update_page = UpdatePage.Field()
    delete_page = DeletePage.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)