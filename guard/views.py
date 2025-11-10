from django.shortcuts import render, redirect
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from .forms import LoginForm, RegisterForm


class CustomLoginView(LoginView):
    template_name = "guard/auth/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

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
    email_template_name = "guard/auth/password_reset_email.html"
    success_url = reverse_lazy("guard:password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "guard/auth/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "guard/auth/password_reset_confirm.html"
    success_url = reverse_lazy("guard:password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "guard/auth/password_reset_complete.html"


class ProfileView(TemplateView):
    template_name = "guard/auth/profile.html"


# @login_required
def index(request):
    return render(request, 'guard/views/index.html')


def login(request):
    return render(request, 'guard/auth/login.html')
