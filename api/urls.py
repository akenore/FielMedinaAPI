from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from django.conf import settings


urlpatterns = [
    path(
        "graphql",
        csrf_exempt(GraphQLView.as_view(graphiql=settings.GRAPHQL_GRAPHIQL_ENABLED)),
    ),
]
