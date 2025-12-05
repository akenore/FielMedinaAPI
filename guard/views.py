from django.shortcuts import render, redirect
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
    PasswordChangeView, PasswordChangeDoneView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView,UpdateView,DeleteView, ListView, TemplateView
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
)

from .models import Location, Event
from shared.translator import get_translator

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



class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "guard/views/dashboard.html"

class LocationsListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "guard/views/locations/list.html"
    context_object_name = "locations"
    paginate_by = 10
    ordering = ["-created_at"]


class LocationCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Location
    template_name = "guard/views/locations/index.html"
    form_class = LocationForm
    success_url = reverse_lazy("guard:locationsList")
    success_message = _("Location created successfully.")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ImageLocationFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = ImageLocationFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            has_image = any(
                formset_form.cleaned_data.get('image') and not formset_form.cleaned_data.get('DELETE', False)
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
            context['image_formset'] = ImageLocationFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['image_formset'] = ImageLocationFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            existing_images = sum(
                1 for formset_form in image_formset
                if formset_form.instance.pk and not formset_form.cleaned_data.get('DELETE', False)
            )
            new_images = sum(
                1 for formset_form in image_formset
                if formset_form.cleaned_data.get('image') and not formset_form.instance.pk
            )
            
            if existing_images + new_images < 1:
                form.add_error(None, _("Veuillez conserver ou télécharger au moins une image."))
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


@login_required
def subscribersList(request):
    return render(request, 'guard/views/subscribers/list.html')
@login_required
def publicTransportsList(request):
    return render(request, 'guard/views/publicTransports/list.html')

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
            context['image_formset'] = ImageEventFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = ImageEventFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            # Check if at least one image is uploaded
            has_image = any(
                formset_form.cleaned_data.get('image') and not formset_form.cleaned_data.get('DELETE', False)
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
            context['image_formset'] = ImageEventFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['image_formset'] = ImageEventFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            existing_images = sum(
                1 for formset_form in image_formset
                if formset_form.instance.pk and not formset_form.cleaned_data.get('DELETE', False)
            )
            new_images = sum(
                1 for formset_form in image_formset
                if formset_form.cleaned_data.get('image') and not formset_form.instance.pk
            )
            
            if existing_images + new_images < 1:
                form.add_error(None, _("Veuillez conserver ou télécharger au moins une image."))
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


@login_required
def adsList(request):
    return render(request, 'guard/views/ads/list.html')


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
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'en')
        target_lang = data.get('target_lang', 'fr')
        preserve_html = data.get('preserve_html', False)
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'No text provided'
            }, status=400)
        
        # Get translator and perform translation
        translator = get_translator()
        translated_text = translator.translate(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            preserve_html=preserve_html
        )
        
        return JsonResponse({
            'success': True,
            'translated_text': translated_text
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
