from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _

from .models import User, Troop


class TroopForm(forms.ModelForm):
    class Meta:
        model = Troop
        fields = ['troop_number',
                  'troop_cookie_coordinator',
                  'troop_level',
                  'super_troop']

        labels = {'troop_number': _('Troop Number'),
                  'troop_cookie_coordinator': _('Troop Cookie Coordinator Username'),
                  'troop_level': _('Troop Level'),
                  'super_troop': _('Super Troop')}

    def clean(self):
        # We want to make absolutely sure that we are not duplicating a troop. We should be able to find this uniquely
        # by troop number
        if Troop.objects.filter(troop_number=self.cleaned_data['troop_number']):
            cleaned_troop_id = Troop.objects.get(troop_number=self.cleaned_data['troop_number']).troop_number

            if cleaned_troop_id != self.troop_number or self.troop_number is None:
                self.add_error('troop_number', "Troop number is already taken. Please choose a unique troop number.")
                raise forms.ValidationError('Invalid Troop number!')

    def __init__(self, *args, **kwargs):
        # This is used to add booth_id to check if we're duplicating an item on edit.
        try:
            self.troop_number = kwargs.pop('troop_number')
        except KeyError:
            self.troop_number = None
        super(TroopForm, self).__init__(*args, **kwargs)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    # TODO: Add Troops

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
