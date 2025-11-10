from django.urls import path

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
    index,
)

app_name = "guard"

urlpatterns = [
    path('', index, name='index'),
    path('auth/login/', CustomLoginView.as_view(), name='login'),
    path('auth/logout/', CustomLogoutView.as_view(), name='logout'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/password-reset/',
         CustomPasswordResetView.as_view(), name='password_reset'),
    path('auth/password-reset/done/',
         CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('auth/password-reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/password-reset/complete/',
         CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('auth/password-change/',
         CustomPasswordChangeView.as_view(), name='password_change'),
    path('auth/password-change/done/',
         CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('auth/settings/', SettingView.as_view(), name='settings'),
]
