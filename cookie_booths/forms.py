from django import forms
from django.forms.utils import ErrorList
from django.utils.translation import gettext as _

from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput

from .models import BoothLocation, BoothHours

DAYS_OF_WEEK = tuple(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])


class BoothLocationForm(forms.ModelForm):
    class Meta:
        model = BoothLocation
        fields = ['booth_location',
                  'booth_address',
                  'booth_notes',
                  'booth_requires_masks',
                  'booth_is_outside',
                  'booth_block_level_restrictions_start',
                  'booth_block_level_restrictions_end',
                  'booth_enabled']

        labels = {'booth_location': _('Location Name'),
                  'booth_address': _('Booth Address'),
                  'booth_notes': _('Additional Booth Notes'),
                  'booth_requires_masks': _('Booth Requires Masks'),
                  'booth_is_outside': _('Booth Is Outside'),
                  'booth_block_level_restrictions_start': _('Lowest Troop Level'),
                  'booth_block_level_restrictions_end': _('Highest Troop Level'),
                  'booth_enabled': _('Booth Is Enabled')}

        help_texts = {
            'booth_block_level_restrictions_start': _('Select the lowest level troop that can use this booth, if none '
                                                      'there are no restrictions'),
            'booth_block_level_restrictions_end': _('Select the highest level troop that can use this booth'),
            'booth_enabled': _('Enabled means booth blocks are able to be reserved.')}

    def clean(self):
        # We want to make absolutely sure that we are not duplicating a location. We should be able to uniquely identify
        # A location by a combination of name and address
        if BoothLocation.objects.filter(booth_location=self.cleaned_data['booth_location'],
                                        booth_address=self.cleaned_data['booth_address']):
            cleaned_booth_id = BoothLocation.objects.get(booth_location=self.cleaned_data['booth_location'],
                                                         booth_address=self.cleaned_data['booth_address']).id

            if cleaned_booth_id != self.booth_id or self.booth_id is None:
                self.add_error('booth_location', "Please add a unique location.")
                self.add_error('booth_address', "Please add a unique address.")
                raise forms.ValidationError('This location already exists!')

        # Make sure that the booth range is accurate
        if self.cleaned_data['booth_block_level_restrictions_start'] > \
                self.cleaned_data['booth_block_level_restrictions_end'] != 0:
            self.add_error('booth_block_level_restrictions_start', "Restriction start must be lower than end")
            self.add_error('booth_block_level_restrictions_end', "Restriction start must be lower than end")
            raise forms.ValidationError('Booth levels are invalid')

    def __init__(self, *args, **kwargs):
        # This is used to add booth_id to check if we're duplicating an item on edit.
        try:
            self.booth_id = kwargs.pop('booth_id')
        except KeyError:
            self.booth_id = None
        super(BoothLocationForm, self).__init__(*args, **kwargs)


class BoothHoursForm(forms.ModelForm):
    class Meta:
        model = BoothHours
        fields = ['booth_start_date',
                  'booth_end_date',
                  'sunday_open',
                  'sunday_golden_ticket',
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
                  'saturday_golden_ticket',
                  'saturday_open_time',
                  'saturday_close_time']

        widgets = {'booth_start_date': DatePickerInput(format='%m/%d/%Y').start_of('booth days'),
                   'booth_end_date': DatePickerInput(format='%m/%d/%Y').end_of('booth days'),
                   'sunday_open_time': TimePickerInput(format='%I:%M %p',
                                                       attrs={'id': 'sunday_time'}).start_of('sunday'),
                   'sunday_close_time': TimePickerInput(format='%I:%M %p',
                                                        attrs={'id': 'sunday_time'}).end_of('sunday'),
                   'monday_open_time': TimePickerInput(format='%I:%M %p',
                                                       attrs={'id': 'monday_time'}).start_of('monday'),
                   'monday_close_time': TimePickerInput(format='%I:%M %p',
                                                        attrs={'id': 'monday_time'}).end_of('monday'),
                   'tuesday_open_time': TimePickerInput(format='%I:%M %p',
                                                        attrs={'id': 'tuesday_time'}).start_of('tuesday'),
                   'tuesday_close_time': TimePickerInput(format='%I:%M %p',
                                                         attrs={'id': 'tuesday_time'}).end_of('tuesday'),
                   'wednesday_open_time': TimePickerInput(format='%I:%M %p',
                                                          attrs={'id': 'wednesday_time'}).start_of('wednesday'),
                   'wednesday_close_time': TimePickerInput(format='%I:%M %p',
                                                           attrs={'id': 'wednesday_time'}).end_of('wednesday'),
                   'thursday_open_time': TimePickerInput(format='%I:%M %p',
                                                         attrs={'id': 'thursday_time'}).start_of('thursday'),
                   'thursday_close_time': TimePickerInput(format='%I:%M %p',
                                                          attrs={'id': 'thursday_time'}).end_of('thursday'),
                   'friday_open_time': TimePickerInput(format='%I:%M %p',
                                                       attrs={'id': 'friday_time'}).start_of('friday'),
                   'friday_close_time': TimePickerInput(format='%I:%M %p',
                                                        attrs={'id': 'friday_time'}).end_of('friday'),
                   'saturday_open_time': TimePickerInput(format='%I:%M %p',
                                                         attrs={'id': 'saturday_time'}).start_of('saturday'),
                   'saturday_close_time': TimePickerInput(format='%I:%M %p',
                                                          attrs={'id': 'saturday_time'}).end_of('saturday'),
                   }

        labels = {'booth_start_date': _('Booth Starting Date'),
                  'booth_end_date': _('Booth Ending Date'),
                  'sunday_open': _('Open Sundays'),
                  'sunday_golden_ticket': _('Golden Ticket on Sunday'),
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
                  'saturday_golden_ticket': _('Golden Ticket on Saturday'),
                  'saturday_open_time': _('Saturday Open Time'),
                  'saturday_close_time': _('Saturday Close Time')}

        help_texts = {'booth_start_date': _('Enter the date sales will begin at this booth.'),
                      'booth_end_date': _('Enter the last date of sales for this booth.')}

    def clean(self):
        # Make sure we have valid dates - both populated or both not is fine
        if (self.cleaned_data['booth_start_date'] is None and self.cleaned_data['booth_end_date'] is not None) or \
                (self.cleaned_data['booth_start_date'] is not None and self.cleaned_data['booth_end_date'] is None):

            if self.cleaned_data['booth_start_date'] is None:
                self.add_error('booth_start_date', "Please specify valid start date.")
            if self.cleaned_data['booth_end_date'] is None:
                self.add_error('booth_end_date', "Please specify valid end date.")
            raise forms.ValidationError('Must have valid start and ending dates!')

        # Make sure we have valid times - both populated is needed if the checkbox is checked
        valid_times = True
        for day in DAYS_OF_WEEK:
            day_is_valid = self.__check_times_set_correctly(day_of_week=day)
            valid_times = valid_times and day_is_valid

        if not valid_times:
            raise forms.ValidationError('Open and close times must be specified for open days!')

    def __check_times_set_correctly(self, day_of_week):
        """Checks to see if the times in the forms are properly set"""
        day_of_week_close = day_of_week + "_close_time"
        day_of_week_open = day_of_week + "_open_time"
        day_of_week_checkbox = day_of_week + "_open"
        valid_times = True

        if ((self.cleaned_data[day_of_week_checkbox]) and
                (self.cleaned_data[day_of_week_open] is None or self.cleaned_data[day_of_week_close] is None)):
            valid_times = False
            if self.cleaned_data[day_of_week_open] is None:
                self.add_error(day_of_week_open, "Please specify valid open time.")
            if self.cleaned_data[day_of_week_close] is None:
                self.add_error(day_of_week_close, "Please specify valid close time.")

        return valid_times


class EnableFreeForAll(forms.Form):

    start_date = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y').start_of('booth days')
    )
    end_date = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y').end_of('booth days')
    )
