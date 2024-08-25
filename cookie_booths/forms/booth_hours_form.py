import logging

from bootstrap_datepicker_plus.widgets import TimePickerInput
from django import forms
from django.utils.translation import gettext as _

from cookie_booths.models import BoothHours
from utils.constants import DAYS_OF_WEEK, GOLDEN_TICKET_DAYS

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

DAYS = [day.lower() for _, day in DAYS_OF_WEEK]


class BoothHoursForm(forms.ModelForm):
    """
    A form for managing booth hours.

    This form is used to collect and validate booth hours data for a specific booth.

    Attributes:
        model (Model): The model class associated with the form.
        fields (list): The list of fields to include in the form.
        widgets (dict): The dictionary of widgets to use for each field.
        labels (dict): The dictionary of labels to use for each field.
        help_texts (dict): The dictionary of help texts to display for each field.

    Methods:
        clean_booth_start_date: Validates the booth start date.
        clean_booth_end_date: Validates the booth end date.
        clean: Cleans and validates the form data.
        __check_times_set_correctly: Checks if the times in the form are properly set.
    """

    class Meta:
        model = BoothHours

        fields = ["booth_start_date", "booth_end_date"]
        labels = {
            "booth_start_date": _("Enter the date sales will begin at this booth."),
            "booth_end_date": _("Enter the last date of sales for this booth."),
        }
        help_texts = {
            "booth_start_date": _("Enter the date sales will begin at this booth."),
            "booth_end_date": _("Enter the last date of sales for this booth."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {})

        if instance and instance.daily_attributes:
            for day in DAYS:
                day_attributes = instance.daily_attributes.get(day, {})
                initial.update(
                    {
                        f"{day}_open": day_attributes.get("open", False),
                        f"{day}_golden_ticket": (
                            day_attributes.get("golden_ticket", False)
                            if DAYS.index(day) in GOLDEN_TICKET_DAYS
                            else None
                        ),
                        f"{day}_open_time": day_attributes.get("open_time", None),
                        f"{day}_close_time": day_attributes.get("close_time", None),
                    }
                )

        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

        for day in DAYS:
            self.fields[f"{day}_open"] = forms.BooleanField(required=False)
            if DAYS.index(day) in GOLDEN_TICKET_DAYS:
                self.fields[f"{day}_golden_ticket"] = forms.BooleanField(required=False)
            self.fields[f"{day}_open_time"] = forms.TimeField(
                widget=TimePickerInput(), required=False
            )
            self.fields[f"{day}_close_time"] = forms.TimeField(
                widget=TimePickerInput(), required=False
            )

    def clean_booth_start_date(self):
        """
        Validates the booth start date.

        Returns:
            str: The cleaned booth start date.

        Raises:
            forms.ValidationError: If the booth start date is not specified.
        """
        data = self.cleaned_data["booth_start_date"]
        if data is None:
            raise forms.ValidationError("Please specify a valid start date")

        return data

    def clean_booth_end_date(self):
        """
        Validates the booth end date.

        Returns:
            str: The cleaned booth end date.

        Raises:
            forms.ValidationError: If the booth end date is not specified.
        """
        data = self.cleaned_data["booth_end_date"]
        if data is None:
            raise forms.ValidationError("Please specify a valid end date")

        return data

    def clean(self):
        """
        Cleans and validates the form data.

        This method is called after all individual field clean methods have been called.

        Raises:
            forms.ValidationError: If the times in the form are not set correctly.
        """
        super().clean()
        self.instance.daily_attributes = self.__process_daily_attributes(self.cleaned_data)
        # Make sure we have valid times - both populated is needed if the checkbox is checked
        for day in DAYS:
            self.__check_times_set_correctly(day_of_week=day)

    def __process_daily_attributes(self, cleaned_data):
        daily_attributes = {}
        for day in DAYS:
            daily_attributes[day] = {
                "open": cleaned_data.get(f"{day}_open"),
                "open_time": (
                    cleaned_data.get(f"{day}_open_time").strftime("%H:%M:%S")
                    if cleaned_data.get(f"{day}_open_time")
                    else None
                ),
                "close_time": (
                    cleaned_data.get(f"{day}_close_time").strftime("%H:%M:%S")
                    if cleaned_data.get(f"{day}_close_time")
                    else None
                ),
                "golden_ticket": cleaned_data.get(f"{day}_golden_ticket", False),
            }
        cleaned_data["daily_attributes"] = daily_attributes
        return daily_attributes

    def __check_times_set_correctly(self, day_of_week):
        """
        Checks if the times in the form are properly set.

        Args:
            day_of_week (str): The day of the week to check.

        Raises:
            forms.ValidationError: If the open or close time is not specified when the checkbox is checked.
        """
        day_of_week_close = day_of_week + "_close_time"
        day_of_week_open = day_of_week + "_open_time"
        day_of_week_checkbox = day_of_week + "_open"

        if self.cleaned_data[day_of_week_checkbox]:
            if not self.cleaned_data[day_of_week_open]:
                self.add_error(
                    day_of_week_open, f"Please specify a valid open time for {day_of_week.title()}."
                )
            if not self.cleaned_data[day_of_week_close]:
                self.add_error(
                    day_of_week_close,
                    f"Please specify a valid close time for {day_of_week.title()}.",
                )
