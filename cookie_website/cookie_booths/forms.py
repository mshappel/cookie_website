from django import forms
from django.utils.translation import gettext as _

from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput

from .models import BoothLocation, BoothHours


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


class BoothHoursForm(forms.ModelForm):
    class Meta:
        model = BoothHours
        fields = ['booth_start_date',
                  'booth_end_date',
                  'sunday_open',
                  'sunday_open_time',
                  'sunday_close_time',
                  'monday_open',
                  'monday_open_time',
                  'monday_close_time',
                  'tuesday_open',
                  'tuesday_open_time',
                  'tuesday_close_time',
                  'wednesday_open',
                  'wednesday_open_time',
                  'wednesday_close_time',
                  'thursday_open',
                  'thursday_open_time',
                  'thursday_close_time',
                  'friday_open',
                  'friday_open_time',
                  'friday_close_time',
                  'saturday_open',
                  'saturday_open_time',
                  'saturday_close_time']

        widgets = {'booth_start_date': DatePickerInput(format='%m/%d/%Y').start_of('booth days'),
                   'booth_end_date': DatePickerInput(format='%m/%d/%Y').end_of('booth days'),
                   'sunday_open_time': TimePickerInput(format='%I:%M %p',
                                                       attrs={'id': 'sunday_time'}).start_of('sunday'),
                   'sunday_close_time': TimePickerInput(format='%I:%M %p',
                                                        attrs={'id': 'sunday_time'}).end_of('sunday'),
                   'monday_open_time': TimePickerInput(format='%I:%M %p').start_of('monday'),
                   'monday_close_time': TimePickerInput(format='%I:%M %p').end_of('monday'),
                   'tuesday_open_time': TimePickerInput(format='%I:%M %p').start_of('tuesday'),
                   'tuesday_close_time': TimePickerInput(format='%I:%M %p').end_of('tuesday'),
                   'wednesday_open_time': TimePickerInput(format='%I:%M %p').start_of('wednesday'),
                   'wednesday_close_time': TimePickerInput(format='%I:%M %p').end_of('wednesday'),
                   'thursday_open_time': TimePickerInput(format='%I:%M %p').start_of('thursday'),
                   'thursday_close_time': TimePickerInput(format='%I:%M %p').end_of('thursday'),
                   'friday_open_time': TimePickerInput(format='%I:%M %p').start_of('friday'),
                   'friday_close_time': TimePickerInput(format='%I:%M %p').end_of('friday'),
                   'saturday_open_time': TimePickerInput(format='%I:%M %p').start_of('saturday'),
                   'saturday_close_time': TimePickerInput(format='%I:%M %p').end_of('saturday'),
                   }

        labels = {'booth_start_date': _('Booth Starting Date'),
                  'booth_end_date': _('Booth Ending Date'),
                  'sunday_open': _('Open Sundays'),
                  'sunday_open_time': _('Sunday Open Time'),
                  'sunday_close_time': _('Sunday Close Time'),
                  'monday_open': _('Open Mondays'),
                  'monday_open_time': _('Monday Open Time'),
                  'monday_close_time': _('Monday Close Time'),
                  'tuesday_open': _('Open Tuesdays'),
                  'tuesday_open_time': _('Tuesday Open Time'),
                  'tuesday_close_time': _('Tuesday Close Time'),
                  'wednesday_open': _('Open Wednesdays'),
                  'wednesday_open_time': _('Wednesday Open Time'),
                  'wednesday_close_time': _('Wednesday Close Time'),
                  'thursday_open': _('Open Thursdays'),
                  'thursday_open_time': _('Thursday Open Time'),
                  'thursday_close_time': _('Thursday Close Time'),
                  'friday_open': _('Open Fridays'),
                  'friday_open_time': _('Friday Open Time'),
                  'friday_close_time': _('Friday Close Time'),
                  'saturday_open': _('Open Saturdays'),
                  'saturday_open_time': _('Saturday Open Time'),
                  'saturday_close_time': _('Saturday Close Time')}

        help_texts = {'booth_start_date': _('Enter the date sales will begin at this booth.'),
                      'booth_end_date': _('Enter the last date of sales for this booth.')}
