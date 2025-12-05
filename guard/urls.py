from django.urls import path, include

from .views import (
    CustomLoginView,
    CustomLogoutView,
    RegisterView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView,
    SettingView,
    DashboardView,
    subscribersList,
    LocationsListView,
    LocationCreateView,
    LocationUpdateView,
    LocationDeleteView,
    EventListView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    adsList,
    publicTransportsList,
    get_cities_by_country,
    translate_text,
)

app_name = "guard"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("auth/login/", CustomLoginView.as_view(), name="login"),
    path("auth/logout/", CustomLogoutView.as_view(), name="logout"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path(
        "auth/password-reset/", CustomPasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "auth/password-reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "auth/password-reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "auth/password-reset/complete/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "auth/password-change/",
        CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "auth/password-change/done/",
        CustomPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("auth/settings/", SettingView.as_view(), name="settings"),
    path(
        "staff/",
        include(
            [
                path("subscribersList/", subscribersList, name="subscribersList"),
                path(
                    "locationsList/", LocationsListView.as_view(), name="locationsList"
                ),
                path(
                    "locations/create/",
                    LocationCreateView.as_view(),
                    name="location_create",
                ),
                path(
                    "locations/update/<int:pk>/",
                    LocationUpdateView.as_view(),
                    name="location_update",
                ),
                path(
                    "locations/delete/<int:pk>/",
                    LocationDeleteView.as_view(),
                    name="location_delete",
                ),
                path("eventsList/", EventListView.as_view(), name="eventsList"),
                path("events/create/", EventCreateView.as_view(), name="event_create"),
                path(
                    "events/update/<int:pk>/",
                    EventUpdateView.as_view(),
                    name="event_update",
                ),
                path(
                    "events/delete/<int:pk>/",
                    EventDeleteView.as_view(),
                    name="event_delete",
                ),
                path(
                    "publicTransportsList/",
                    publicTransportsList,
                    name="publicTransportsList",
                ),
            ]
        ),
    ),
    path("adsList/", adsList, name="adsList"),
    path(
        "api/cities/<int:country_id>/",
        get_cities_by_country,
        name="get_cities_by_country",
    ),
    path("api/translate/", translate_text, name="translate_text"),
]
