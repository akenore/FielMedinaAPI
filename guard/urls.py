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
    SubscribersListView,
    LocationsListView,
    LocationCreateView,
    LocationUpdateView,
    LocationDeleteView,
    EventListView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    TipsListView,
    TipCreateView,
    TipUpdateView,
    TipDeleteView,
    HikingListView,
    HikingCreateView,
    HikingUpdateView,
    HikingDeleteView,
    AdListView,
    AdCreateView,
    AdUpdateView,
    AdDeleteView,
    EventTrackingView,
    AdTrackingView,
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
                path(
                    "subscribersList/",
                    SubscribersListView.as_view(),
                    name="subscribersList",
                ),
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
                    "events/track/<int:pk>/",
                    EventTrackingView.as_view(),
                    name="event_track",
                ),
                path("tips/", TipsListView.as_view(), name="tipsList"),
                path("tips/create/", TipCreateView.as_view(), name="tip_create"),
                path(
                    "tips/update/<int:pk>/", TipUpdateView.as_view(), name="tip_update"
                ),
                path(
                    "tips/delete/<int:pk>/", TipDeleteView.as_view(), name="tip_delete"
                ),
                path("hikings/", HikingListView.as_view(), name="hikingsList"),
                path(
                    "hikings/create/", HikingCreateView.as_view(), name="hiking_create"
                ),
                path(
                    "hikings/update/<int:pk>/",
                    HikingUpdateView.as_view(),
                    name="hiking_update",
                ),
                path(
                    "hikings/delete/<int:pk>/",
                    HikingDeleteView.as_view(),
                    name="hiking_delete",
                ),
                path(
                    "publicTransportsList/",
                    publicTransportsList,
                    name="publicTransportsList",
                ),
            ]
        ),
    ),
    path("adsList/", AdListView.as_view(), name="adsList"),
    path("ads/create/", AdCreateView.as_view(), name="ad_create"),
    path("ads/update/<int:pk>/", AdUpdateView.as_view(), name="ad_update"),
    path("ads/delete/<int:pk>/", AdDeleteView.as_view(), name="ad_delete"),
    path("ads/track/<int:pk>/", AdTrackingView.as_view(), name="ad_track"),
    path(
        "api/cities/<int:country_id>/",
        get_cities_by_country,
        name="get_cities_by_country",
    ),
    path("api/translate/", translate_text, name="translate_text"),
]
