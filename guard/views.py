from django.shortcuts import render, redirect
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
    PasswordChangeView, PasswordChangeDoneView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from .forms import (
    LoginForm,
    RegisterForm,
    FlowbitePasswordResetForm,
    FlowbiteSetPasswordForm,
    FlowbitePasswordChangeForm,
    ProfileUpdateForm,
)


class CustomLoginView(LoginView):
    template_name = "guard/auth/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("guard:dashboard")

    def form_valid(self, form):
        messages.success(self.request, _("Welcome back!"))
        return super().form_valid(form)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "guard/auth/register.html"
    success_url = reverse_lazy("guard:login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _(
            "Account created successfully. Please log in."))
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("guard:login")


class CustomPasswordResetView(PasswordResetView):
    template_name = "guard/auth/password_reset.html"
    form_class = FlowbitePasswordResetForm
    email_template_name = "guard/auth/password_reset_email.txt"
    subject_template_name = "guard/auth/password_reset_subject.txt"
    success_url = reverse_lazy("guard:password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "guard/auth/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "guard/auth/password_reset_confirm.html"
    form_class = FlowbiteSetPasswordForm
    success_url = reverse_lazy("guard:password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "guard/auth/password_reset_complete.html"


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "guard/auth/password_change.html"
    form_class = FlowbitePasswordChangeForm
    success_url = reverse_lazy("guard:password_change_done")

    def form_valid(self, form):
        messages.success(self.request, _("Password updated successfully."))
        return super().form_valid(form)


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "guard/auth/password_change_done.html"


class SettingView(LoginRequiredMixin, TemplateView):
    template_name = "guard/auth/settings.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated successfully."))
            return redirect("guard:settings")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "profile", None)
        context["user_profile"] = profile
        context["profile_form"] = kwargs.get("form") or ProfileUpdateForm(
            instance=self.request.user
        )
        context["subscription_rows"] = self._build_subscription_rows(profile)
        context["subscription_alert"] = self._build_subscription_alert(profile)
        return context

    def _build_subscription_rows(self, profile):
        if not profile:
            return [
                {
                    "plan": _("Konnect subscription"),
                    "status": _("Not available"),
                    "started": None,
                    "renews": None,
                    "days_left": _("—"),
                }
            ]
        days_left = profile.subscription_days_left
        return [
            {
                "plan": profile.subscription_plan or _("Pending Konnect setup"),
                "status": profile.subscription_status_label,
                "started": profile.subscription_started_at,
                "renews": profile.subscription_renews_at,
                "days_left": days_left if days_left is not None else _("—"),
            }
        ]

    def _build_subscription_alert(self, profile):
        if not profile or not profile.is_subscription_expiring:
            return None
        return {
            "level": "warning",
            "days_left": profile.subscription_days_left,
            "renew_date": profile.subscription_renews_at,
        }


@login_required
def dashboard(request):
    return render(request, 'guard/views/dashboard.html')

@login_required
def subscribersList(request):
    return render(request, 'guard/views/subscribers/list.html')

@login_required
def locationsList(request):
    return render(request, 'guard/views/locations/list.html')

@login_required
def eventsList(request):
    return render(request, 'guard/views/events/list.html')

@login_required
def adsList(request):
    return render(request, 'guard/views/ads/list.html')

