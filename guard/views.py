from django.shortcuts import render, redirect
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
    TemplateView,
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .forms import (
    LoginForm,
    RegisterForm,
    FlowbitePasswordResetForm,
    FlowbiteSetPasswordForm,
    FlowbitePasswordChangeForm,
    ProfileUpdateForm,
    LocationForm,
    ImageLocationFormSet,
    EventForm,
    ImageEventFormSet,
    TipForm,
    HikingForm,
    ImageHikingFormSet,
    AdForm,
    ImageAdFormSet,
)

from .models import (
    LocationCategory,
    Location,
    Event,
    UserProfile,
    Tip,
    Hiking,
    Ad,
    ImageAd,
)
from shared.translator import get_translator
from shared.short_io import ShortIOService


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
        messages.success(
            self.request, _("Account created successfully. Please log in.")
        )
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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "guard/views/dashboard.html"


class LocationsListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "guard/views/locations/list.html"
    context_object_name = "locations"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location_categories"] = LocationCategory.objects.all()
        return context


class LocationCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Location
    template_name = "guard/views/locations/index.html"
    form_class = LocationForm
    success_url = reverse_lazy("guard:locationsList")
    success_message = _("Location created successfully.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ImageLocationFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context["image_formset"] = ImageLocationFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            has_image = any(
                formset_form.cleaned_data.get("image")
                and not formset_form.cleaned_data.get("DELETE", False)
                for formset_form in image_formset
                if formset_form.cleaned_data
            )

            if not has_image:
                form.add_error(None, _("Please upload at least one image."))
                return self.form_invalid(form)

            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class LocationUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Location
    template_name = "guard/views/locations/index.html"
    form_class = LocationForm
    success_url = reverse_lazy("guard:locationsList")
    success_message = _("Location updated successfully.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ImageLocationFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context["image_formset"] = ImageLocationFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            existing_images = sum(
                1
                for formset_form in image_formset
                if formset_form.instance.pk
                and not formset_form.cleaned_data.get("DELETE", False)
            )
            new_images = sum(
                1
                for formset_form in image_formset
                if formset_form.cleaned_data.get("image")
                and not formset_form.instance.pk
            )

            if existing_images + new_images < 1:
                form.add_error(
                    None, _("Veuillez conserver ou télécharger au moins une image.")
                )
                return self.form_invalid(form)

            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class LocationDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Location
    success_url = reverse_lazy("guard:locationsList")
    success_message = _("Unfortunately, this location has been deleted")

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super(LocationDeleteView, self).delete(request, *args, **kwargs)


class SubscribersListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = "guard/views/subscribers/list.html"
    context_object_name = "subscribers"
    paginate_by = 10
    ordering = ["-created_at"]


@login_required
def publicTransportsList(request):
    return render(request, "guard/views/publicTransports/list.html")


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "guard/views/events/list.html"
    context_object_name = "events"
    paginate_by = 10
    ordering = ["-created_at"]


class EventCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Event
    template_name = "guard/views/events/index.html"
    form_class = EventForm
    success_url = reverse_lazy("guard:eventsList")
    success_message = _("Event created successfully.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ImageEventFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context["image_formset"] = ImageEventFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            # Check if at least one image is uploaded
            has_image = any(
                formset_form.cleaned_data.get("image")
                and not formset_form.cleaned_data.get("DELETE", False)
                for formset_form in image_formset
                if formset_form.cleaned_data
            )

            if not has_image:
                form.add_error(None, _("Veuillez télécharger au moins une image."))
                return self.form_invalid(form)

            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class EventUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Event
    template_name = "guard/views/events/index.html"
    form_class = EventForm
    success_url = reverse_lazy("guard:eventsList")
    success_message = _("Event updated successfully.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ImageEventFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context["image_formset"] = ImageEventFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            existing_images = sum(
                1
                for formset_form in image_formset
                if formset_form.instance.pk
                and not formset_form.cleaned_data.get("DELETE", False)
            )
            new_images = sum(
                1
                for formset_form in image_formset
                if formset_form.cleaned_data.get("image")
                and not formset_form.instance.pk
            )

            if existing_images + new_images < 1:
                form.add_error(
                    None, _("Veuillez conserver ou télécharger au moins une image.")
                )
                return self.form_invalid(form)

            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class EventDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Event
    success_url = reverse_lazy("guard:eventsList")
    success_message = _("Unfortunately, this event has been deleted")

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super(EventDeleteView, self).delete(request, *args, **kwargs)


class TipsListView(LoginRequiredMixin, ListView):
    model = Tip
    template_name = "guard/views/tips/list.html"
    context_object_name = "tips"
    paginate_by = 10
    ordering = ["-created_at"]


class TipCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Tip
    form_class = TipForm
    template_name = "guard/views/tips/index.html"
    success_url = reverse_lazy("guard:tipsList")
    success_message = _("Tip created successfully")

    success_message = _("Tip created successfully")

    def form_invalid(self, form):
        messages.error(self.request, _("Error creating tip. Please check the form."))
        return super().form_invalid(form)


class TipUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Tip
    form_class = TipForm
    template_name = "guard/views/tips/index.html"
    success_url = reverse_lazy("guard:tipsList")
    success_message = _("Tip updated successfully")

    success_message = _("Tip updated successfully")

    def form_invalid(self, form):
        messages.error(self.request, _("Error updating tip. Please check the form."))
        return super().form_invalid(form)


class TipDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Tip
    success_url = reverse_lazy("guard:tipsList")
    success_message = _("Tip deleted successfully")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class HikingListView(LoginRequiredMixin, ListView):
    model = Hiking
    template_name = "guard/views/hiking/list.html"
    context_object_name = "hikings"
    paginate_by = 10
    ordering = ["-created_at"]


class HikingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Hiking
    form_class = HikingForm
    template_name = "guard/views/hiking/index.html"
    success_url = reverse_lazy("guard:hikingsList")
    success_message = _("Hiking created successfully")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ImageHikingFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context["image_formset"] = ImageHikingFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            has_image = any(
                formset_form.cleaned_data.get("image")
                and not formset_form.cleaned_data.get("DELETE", False)
                for formset_form in image_formset
                if formset_form.cleaned_data
            )

            if not has_image:
                form.add_error(None, _("Please upload at least one image."))
                return self.form_invalid(form)

            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Error creating hiking. Please check the form."))
        return super().form_invalid(form)


class HikingUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Hiking
    form_class = HikingForm
    template_name = "guard/views/hiking/index.html"
    success_url = reverse_lazy("guard:hikingsList")
    success_message = _("Hiking updated successfully")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ImageHikingFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context["image_formset"] = ImageHikingFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            existing_images = sum(
                1
                for formset_form in image_formset
                if formset_form.instance.pk
                and not formset_form.cleaned_data.get("DELETE", False)
            )
            new_images = sum(
                1
                for formset_form in image_formset
                if formset_form.cleaned_data.get("image")
                and not formset_form.instance.pk
            )

            if existing_images + new_images < 1:
                form.add_error(
                    None, _("Veuillez conserver ou télécharger au moins une image.")
                )
                return self.form_invalid(form)

            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Error updating hiking. Please check the form."))
        return super().form_invalid(form)


class HikingDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Hiking
    success_url = reverse_lazy("guard:hikingsList")
    success_message = _("Hiking deleted successfully")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class AdListView(LoginRequiredMixin, ListView):
    model = Ad
    template_name = "guard/views/ads/list.html"
    context_object_name = "ads"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Update clicks for displayed ads (simple implementation)
        # In a real scenario, this should be done asynchronously or on demand
        service = ShortIOService()
        for ad in context["ads"]:
            if ad.short_id:
                try:
                    clicks = service.get_clicks(ad.short_id)
                    if clicks != ad.clicks:
                        ad.clicks = clicks
                        ad.save(update_fields=["clicks"])
                except Exception:
                    pass  # Ignore errors during stats fetch
        return context


class AdCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = "guard/views/ads/index.html"
    success_url = reverse_lazy("guard:adsList")
    success_message = _("Ad created successfully")

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Shorten URL via Short.io
        try:
            service = ShortIOService()
            short_data = service.shorten_url(self.object.link, title="Ad Campaign")
            if short_data:
                self.object.short_link = short_data.get(
                    "secureShortURL"
                ) or short_data.get("shortURL")
                self.object.short_id = short_data.get("idString")
        except Exception as e:
            # Log error but continue saving - Short.io is optional
            import logging

            logging.getLogger(__name__).error(f"Short.io error: {e}")

        self.object.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Error creating ad. Please check the form."))
        return super().form_invalid(form)


class AdUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = "guard/views/ads/index.html"
    success_url = reverse_lazy("guard:adsList")
    success_message = _("Ad updated successfully")

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Re-shorten URL if link changed
        if "link" in form.changed_data:
            try:
                service = ShortIOService()
                short_data = service.shorten_url(self.object.link, title="Ad Campaign")
                if short_data:
                    self.object.short_link = short_data.get(
                        "secureShortURL"
                    ) or short_data.get("shortURL")
                    self.object.short_id = short_data.get("idString")
                    self.object.clicks = 0  # Reset clicks for new link
            except Exception as e:
                import logging

                logging.getLogger(__name__).error(f"Short.io error: {e}")

        self.object.save()
        return super().form_valid(form)


class AdDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Ad
    success_url = reverse_lazy("guard:adsList")
    success_message = _("Ad deleted successfully")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@login_required
def get_cities_by_country(request, country_id):
    from cities_light.models import City

    cities = City.objects.filter(country_id=country_id).values("id", "name")
    cities_list = list(cities)

    return JsonResponse({"success": True, "cities": cities_list})


@login_required
@require_POST
def translate_text(request):
    """
    API endpoint for translating text between English and French.

    Expects JSON payload:
    {
        "text": "text to translate",
        "source_lang": "en" or "fr",
        "target_lang": "fr" or "en",
        "preserve_html": true/false
    }
    """
    try:
        data = json.loads(request.body)
        text = data.get("text", "")
        source_lang = data.get("source_lang", "en")
        target_lang = data.get("target_lang", "fr")
        preserve_html = data.get("preserve_html", False)

        if not text:
            return JsonResponse(
                {"success": False, "error": "No text provided"}, status=400
            )

        translator = get_translator()
        translated_text = translator.translate(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            preserve_html=preserve_html,
        )

        return JsonResponse({"success": True, "translated_text": translated_text})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
