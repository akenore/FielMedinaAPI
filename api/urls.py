from django.urls import path
from django.conf import settings
from strawberry.django.views import GraphQLView
from .schema import schema

urlpatterns = [
    path(
        "graphql",
        GraphQLView.as_view(
            schema=schema, graphql_ide="graphiql" if settings.DEBUG else None
        ),
    ),
]
