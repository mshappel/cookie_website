from django import forms
from django.utils.translation import gettext as _

from .models import Troop


class TroopForm(forms.ModelForm):
    class Meta:
        model = Troop
        fields = ['troop_number',
                  'troop_cookie_coordinator',
                  'troop_level',
                  'troop_size']

        labels = {'troop_number': _('Troop Number'),
                  'troop_cookie_coordinator': _('Troop Cookie Coordinator Username'),
                  'troop_level': _('Troop Level'),
                  'troop_size': _('Troop Size')}

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