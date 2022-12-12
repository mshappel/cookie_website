from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import CustomUser, UserPreferences


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs) -> None:
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['email'].help_text = "Required"
        self.fields["first_name"].required = True
        self.fields['first_name'].help_text = "Required"
        self.fields["last_name"].required = True
        self.fields["last_name"].help_text = "Required"

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name")


class ChangeUserPreferences(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ('email','phone_number', 'communication_preference')

    def __init__(self, *args, **kwargs):
        super(ChangeUserPreferences, self).__init__(*args, **kwargs)

        self.fields['email'].disabled = True
