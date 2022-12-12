from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from .forms import CustomUserCreationForm, ChangeUserPreferences
from .models import UserPreferences


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class UserPreferenceView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy("login")
    
    model = UserPreferences
    form_class = ChangeUserPreferences
    success_url = reverse_lazy("home")
    template_name = "accounts/preferences.html"

    def get_object(self, queryset=None):
        obj = super(UserPreferenceView, self).get_object(queryset=queryset)
        current_obj=(self.model.objects.get(email=self.request.user.pk))
        if obj.pk != current_obj.pk:
            raise Http404()
        
        return obj


