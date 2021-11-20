from django import forms
from django.utils.translation import gettext as _

from .models import BoothLocation

# Add forms for booths here


class BoothLocationForm(forms.ModelForm):
    class Meta:
        model = BoothLocation
        fields = ['booth_location',
                  'booth_address',
                  'booth_notes',
                  'booth_is_golden_ticket',
                  'booth_requires_masks',
                  'booth_is_outside',
                  'booth_enabled']

        labels = {'booth_location': _('Location Name'),
                  'booth_address': _('Booth Address'),
                  'booth_notes': _('Additional Booth Notes'),
                  'booth_is_golden_ticket': _('Golden Ticket Booth'),
                  'booth_requires_masks': _('Booth Requires Masks'),
                  'booth_is_outside': _('Booth Is Outside'),
                  'booth_enabled': _('Booth Is Enabled')}

        help_texts = {'booth_enabled': _('Enabled means booth blocks are able to be reserved.')}


class BoothHoursForm(forms.Form):
    booth_start_date = forms.DateField(help_text="Enter the date sales will start at this location (inclusive)")
    booth_end_date = forms.DateField(help_text="Enter the date sales will end at this location (inclusive)")

    # TODO: Add cleaning to enable/disable TimeFields based on BooleanField
    sunday_open = forms.BooleanField(label="Open Sundays")
    sunday_open_time = forms.TimeField(label="Sunday Open Time")
    sunday_close_time = forms.TimeField(label="Sunday Close Time")

    monday_open = forms.BooleanField(label="Open Monday")
    monday_open_time = forms.TimeField(label="Monday Open Time")
    monday_close_time = forms.TimeField(label="Monday Close Time")

    tuesday_open = forms.BooleanField(label="Open Tuesday")
    tuesday_open_time = forms.TimeField(label="Tuesday Open Time")
    tuesday_close_time = forms.TimeField(label="Tuesday Close Time")

    wednesday_open = forms.BooleanField(label="Open Wednesday")
    wednesday_open_time = forms.TimeField(label="Wednesday Open Time")
    wednesday_close_time = forms.TimeField(label="Wednesday Close Time")

    thursday_open = forms.BooleanField(label="Open Thursday")
    thursday_open_time = forms.TimeField(label="Thursday Open Time")
    thursday_close_time = forms.TimeField(label="Thursday Close Time")

    friday_open = forms.BooleanField(label="Open Friday")
    friday_open_time = forms.TimeField(label="Friday Open Time")
    friday_close_time = forms.TimeField(label="Friday Close Time")

    saturday_open = forms.BooleanField(label="Open Saturday")
    saturday_open_time = forms.TimeField(label="Saturday Open Time")
    saturday_close_time = forms.TimeField(label="Saturday Close Time")