from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE

from .models import (
    UserProfile,
    Location,
    ImageLocation,
    Event,
    ImageEvent,
)


class FlowbiteFormMixin:
    input_class = (
        "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
        "focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 "
        "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 "
        "dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
    )

    checkbox_class = "w-5 h-5 border border-default-medium rounded bg-neutral-secondary-medium focus:ring-2 focus:ring-brand-soft"
    radio_class = "w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            widget = field.widget
            classes = widget.attrs.get("class", "")

            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs["class"] = f"{classes} {self.checkbox_class}".strip()
            elif isinstance(widget, (forms.RadioSelect,)):
                widget.attrs["class"] = f"{classes} {self.radio_class}".strip()
            else:
                widget.attrs["class"] = f"{classes} {self.input_class}".strip()

            widget.attrs.setdefault("id", f"id_{name}")


class LoginForm(FlowbiteFormMixin, AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Your username"),
                "autocomplete": "username",
            }
        ),
        error_messages={
            "required": _("Please enter your username."),
        },
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Your password"),
                "autocomplete": "current-password",
            }
        ),
        error_messages={
            "required": _("Please enter your password."),
        },
    )


class RegisterForm(FlowbiteFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Create a password"),
                "autocomplete": "new-password",
            }
        ),
        help_text=_("Use at least 8 characters."),
        error_messages={"required": _("Password is required.")},
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Confirm your password"),
                "autocomplete": "new-password",
            }
        ),
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
            "username": forms.TextInput(
                attrs={
                    "placeholder": _("Choose a username"),
                    "autocomplete": "username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": _("name@example.com"),
                    "autocomplete": "email",
                }
            ),
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
                "invalid": _("Enter a valid email address."),
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
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": _("Your first name"),
                    "autocomplete": "given-name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": _("Your last name"),
                    "autocomplete": "family-name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": _("name@example.com"),
                    "autocomplete": "email",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("This email is already in use."))
        return email


class LocationForm(FlowbiteFormMixin, forms.ModelForm):
    name_en = forms.CharField(
        label=_("Name (English)"),
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Enter location name in English"),
            }
        ),
        error_messages={
            "required": _("Please enter the name in English."),
        },
    )
    name_fr = forms.CharField(
        label=_("Name (French)"),
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Enter location name in French"),
            }
        ),
        error_messages={
            "required": _("Please enter the name in French."),
        },
    )

    story_en = forms.CharField(
        label=_("Story (English)"),
        required=True,
        widget=TinyMCE(attrs={"cols": 80, "rows": 30}),
        error_messages={
            "required": _("Please enter the story in English."),
        },
    )
    story_fr = forms.CharField(
        label=_("Story (French)"),
        required=True,
        widget=TinyMCE(attrs={"cols": 80, "rows": 30}),
        error_messages={
            "required": _("Please enter the story in French."),
        },
    )

    class Meta:
        model = Location
        fields = [
            "name_en",
            "name_fr",
            "category",
            "country",
            "city",
            "latitude",
            "longitude",
            "story_en",
            "story_fr",
            "openFrom",
            "openTo",
            "admissionFee",
            "is_active_ads",
        ]
        widgets = {
            "category": forms.Select(
                attrs={
                    "placeholder": _("Select location category"),
                    "required": True,
                }
            ),
            "country": forms.Select(
                attrs={
                    "placeholder": _("Select location country"),
                    "required": True,
                }
            ),
            "city": forms.Select(
                attrs={
                    "placeholder": _("Select location city"),
                    "required": True,
                }
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "placeholder": _("e.g., 36.8065"),
                    "step": "0.000001",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "placeholder": _("e.g., 10.1815"),
                    "step": "0.000001",
                }
            ),
            "openFrom": forms.TimeInput(
                attrs={
                    "type": "time",
                    "placeholder": _("Opening time"),
                }
            ),
            "openTo": forms.TimeInput(
                attrs={
                    "type": "time",
                    "placeholder": _("Closing time"),
                }
            ),
            "admissionFee": forms.NumberInput(
                attrs={
                    "placeholder": _("e.g., 5.00"),
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "is_active_ads": forms.CheckboxInput(),
        }

        error_messages = {
            "category": {
                "required": _("Please select a category."),
            },
            "country": {
                "required": _("Please select a country."),
            },
            "city": {
                "required": _("Please select a city."),
            },
        }

        help_texts = {
            "latitude": _("Latitude in decimal degrees (e.g., 36.8065)"),
            "longitude": _("Longitude in decimal degrees (e.g., 10.1815)"),
            "openFrom": _("Leave empty if location is always open"),
            "openTo": _("Leave empty if location is always open"),
            "admissionFee": _("Leave empty if admission is free"),
            "is_active_ads": _("Enable advertisements for this location"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "category" in self.fields:
            self.fields["category"].required = True
        if "country" in self.fields:
            self.fields["country"].required = True
        if "city" in self.fields:
            self.fields["city"].required = True

        if "city" in self.fields:
            from cities_light.models import City

            if self.instance and self.instance.country:
                self.fields["city"].queryset = City.objects.filter(
                    country=self.instance.country
                )
            else:
                self.fields["city"].queryset = City.objects.all()

    def clean(self):
        cleaned_data = super().clean()

        # Check required multilingual fields and add non-field errors so they appear at top
        errors = []

        if not cleaned_data.get("name_en"):
            errors.append(_("Please enter the name in English."))
            # Remove field-specific error to avoid duplication
            if "name_en" in self.errors:
                del self.errors["name_en"]

        if not cleaned_data.get("name_fr"):
            errors.append(_("Please enter the name in French."))
            if "name_fr" in self.errors:
                del self.errors["name_fr"]

        if not cleaned_data.get("story_en"):
            errors.append(_("Please enter the story in English."))
            if "story_en" in self.errors:
                del self.errors["story_en"]

        if not cleaned_data.get("story_fr"):
            errors.append(_("Please enter the story in French."))
            if "story_fr" in self.errors:
                del self.errors["story_fr"]

        # Add all errors as non-field errors
        for error in errors:
            self.add_error(None, error)

        # Existing validation
        open_from = cleaned_data.get("openFrom")
        open_to = cleaned_data.get("openTo")

        if open_from and open_to and open_from >= open_to:
            self.add_error("openTo", _("Opening time must be before closing time."))

        return cleaned_data


class ImageLocationForm(forms.ModelForm):
    class Meta:
        model = ImageLocation
        fields = ["image"]
        widgets = {
            "image": forms.FileInput(
                attrs={
                    "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
                    "accept": "image/*",
                }
            )
        }


ImageLocationFormSet = inlineformset_factory(
    Location,
    ImageLocation,
    form=ImageLocationForm,
    extra=1,
    can_delete=True,
    max_num=10,
)


class EventForm(FlowbiteFormMixin, forms.ModelForm):
    name_en = forms.CharField(
        label=_("Name (English)"),
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Enter event name in English"),
            }
        ),
        error_messages={
            "required": _("Please enter the name in English."),
        },
    )
    name_fr = forms.CharField(
        label=_("Name (French)"),
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Enter event name in French"),
            }
        ),
        error_messages={
            "required": _("Please enter the name in French."),
        },
    )

    description_en = forms.CharField(
        label=_("Description (English)"),
        required=True,
        widget=TinyMCE(attrs={"cols": 80, "rows": 30}),
        error_messages={
            "required": _("Please enter the description in English."),
        },
    )
    description_fr = forms.CharField(
        label=_("Description (French)"),
        required=True,
        widget=TinyMCE(attrs={"cols": 80, "rows": 30}),
        error_messages={
            "required": _("Please enter the description in French."),
        },
    )

    class Meta:
        model = Event
        fields = [
            "name_en",
            "name_fr",
            "description_en",
            "description_fr",
            "location",
            "category",
            "startDate",
            "endDate",
            "time",
            "price",
        ]
        widgets = {
            "location": forms.Select(
                attrs={
                    "placeholder": _("Select event location"),
                }
            ),
            "category": forms.Select(
                attrs={
                    "placeholder": _("Select event category"),
                }
            ),
            "startDate": forms.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": _("Select event start date"),
                }
            ),
            "endDate": forms.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": _("Select event end date"),
                }
            ),
            "time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "placeholder": _("Select event time"),
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "placeholder": _("Enter event price"),
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Check required multilingual fields and add non-field errors so they appear at top
        errors = []

        if not cleaned_data.get("name_en"):
            errors.append(_("Please enter the name in English."))
            # Remove field-specific error to avoid duplication
            if "name_en" in self.errors:
                del self.errors["name_en"]

        if not cleaned_data.get("name_fr"):
            errors.append(_("Please enter the name in French."))
            if "name_fr" in self.errors:
                del self.errors["name_fr"]

        if not cleaned_data.get("description_en"):
            errors.append(_("Please enter the description in English."))
            if "description_en" in self.errors:
                del self.errors["description_en"]

        if not cleaned_data.get("description_fr"):
            errors.append(_("Please enter the description in French."))
            if "description_fr" in self.errors:
                del self.errors["description_fr"]

        # Add all errors as non-field errors
        for error in errors:
            self.add_error(None, error)

        return cleaned_data


class ImageEventForm(forms.ModelForm):
    class Meta:
        model = ImageEvent
        fields = ["image"]
        widgets = {
            "image": forms.FileInput(
                attrs={
                    "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
                    "accept": "image/*",
                }
            )
        }


ImageEventFormSet = inlineformset_factory(
    Event,
    ImageEvent,
    form=ImageEventForm,
    extra=1,
    can_delete=True,
    max_num=10,
)
