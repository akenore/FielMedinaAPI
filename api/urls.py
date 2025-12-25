from django.urls import path

# from django.views.decorators.csrf import csrf_exempt
# from graphene_django.views import GraphQLView
# from django.conf import settings
from strawberry.django.views import GraphQLView
from .schema import schema

urlpatterns = [
    path("graphql", GraphQLView.as_view(schema=schema)),
    # path(
    #     "graphql",
    #     csrf_exempt(GraphQLView.as_view(graphiql=settings.GRAPHQL_GRAPHIQL_ENABLED)),
    # ),
]
