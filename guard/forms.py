from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import UserProfile


class FlowbiteFormMixin:
    input_class = (
        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
        "focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 "
        "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 "
        "dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{classes} {self.input_class}".strip(
            )
            field.widget.attrs.setdefault("id", f"id_{name}")


class LoginForm(FlowbiteFormMixin, AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={
            "placeholder": _("Your username"),
            "autocomplete": "username",
        }),
        error_messages={
            "required": _("Please enter your username."),
        },
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("Your password"),
            "autocomplete": "current-password",
        }),
        error_messages={
            "required": _("Please enter your password."),
        },
    )


class RegisterForm(FlowbiteFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("Create a password"),
            "autocomplete": "new-password",
        }),
        help_text=_("Use at least 8 characters."),
        error_messages={"required": _("Password is required.")},
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("Confirm your password"),
            "autocomplete": "new-password",
        }),
        error_messages={"required": _("Please confirm your password.")},
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        labels = {
            "username": _("Username"),
            "email": _("Email address"),
        }
        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": _("Choose a username"),
                "autocomplete": "username",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": _("name@example.com"),
                "autocomplete": "email",
            }),
        }
        help_texts = {
            "username": _("Letters, digits and @/./+/-/_ only."),
        }
        error_messages = {
            "username": {
                "required": _("Username is required."),
                "unique": _("This username is already taken."),
            },
            "email": {
                "required": _("Email is required."),
                "invalid":  _("Enter a valid email address."),
            },
        }

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", _("Passwords do not match."))
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"user_type": UserProfile.UserType.CLIENT_PARTNER},
            )
        return user


class FlowbitePasswordResetForm(FlowbiteFormMixin, PasswordResetForm):
    pass


class FlowbiteSetPasswordForm(FlowbiteFormMixin, SetPasswordForm):
    pass


class FlowbitePasswordChangeForm(FlowbiteFormMixin, PasswordChangeForm):
    pass


class ProfileUpdateForm(FlowbiteFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": _("First name"),
            "last_name": _("Last name"),
            "email": _("Email"),
        }
        widgets = {
            "first_name": forms.TextInput(attrs={
                "placeholder": _("Your first name"),
                "autocomplete": "given-name",
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": _("Your last name"),
                "autocomplete": "family-name",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": _("name@example.com"),
                "autocomplete": "email",
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("This email is already in use."))
        return email
