from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms


class EnableFreeForAll(forms.Form):

    start_date = forms.DateField(widget=DatePickerInput(options={"range_from": "booth days"}))
    end_date = forms.DateField(widget=DatePickerInput(options={"range_from": "booth days"}))
