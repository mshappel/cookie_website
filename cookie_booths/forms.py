from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput
from django import forms
from django.utils.translation import gettext as _

from .models import BoothHours, BoothLocation

DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
GOLDEN_TICKET_DAYS = ["saturday", "sunday"]
DAY_FIELD_STRUCTURE = {
    "open": "open",
    "open_time": "open_time",
    "close_time": "close_time",
    "golden_ticket": "golden_ticket",
}


def generate_labels():
    """
    Generate a dictionary of labels for the cookie booth form.

    Returns:
        dict: A dictionary containing labels for various fields in the form.
    """
    labels = {
        "booth_start_date": _("Booth Starting Date"),
        "booth_end_date": _("Booth Ending Date"),
    }

    for day in DAYS_OF_WEEK:
        labels[f"{day}_open"] = _(f"Open {day.capitalize()}s")
        labels[f"{day}_open_time"] = _(f"{day.capitalize()} Open Time")
        labels[f"{day}_close_time"] = _(f"{day.capitalize()} Close Time")
        if day in GOLDEN_TICKET_DAYS:
            labels[f"{day}_golden_ticket"] = _(f"Golden Ticket on {day.capitalize()}")

    return labels


def generate_widgets():
    """
    Generate and return a dictionary of widgets for the cookie booth form.

    Returns:
        dict: A dictionary containing the generated widgets.
    """
    widgets = {
        "booth_start_date": DatePickerInput(
            attrs={"class": "datepicker", "name": "booth_start_date"}
        ),
        "booth_end_date": DatePickerInput(attrs={"class": "datepicker", "name": "booth_end_date"}),
    }

    for day in DAYS_OF_WEEK:
        widgets[f"{day}_open_time"] = TimePickerInput(
            attrs={"id": f"{day}_open_time", "class": "timepicker"}
        )
        widgets[f"{day}_close_time"] = TimePickerInput(
            attrs={"id": f"{day}_close_time", "class": "timepicker"}
        )

    return widgets


def generate_fields():
    """
    Generate a list of fields for a cookie booth form.

    Returns:
        list: A list of field names.
    """
    fields = ["booth_start_date", "booth_end_date"]

    for day in DAYS_OF_WEEK:
        fields.append(f"{day}_open")
        if day in GOLDEN_TICKET_DAYS:
            fields.append(f"{day}_golden_ticket")
        fields.append(f"{day}_open_time")
        fields.append(f"{day}_close_time")

    return fields


class BoothLocationForm(forms.ModelForm):
    """
    A form used for creating and editing booth locations.

    This form is used to collect and validate data for booth locations.
    It inherits from the ModelForm class and is associated with the BoothLocation model.

    Attributes:
        booth_id (int): The ID of the booth being edited (optional).

    Methods:
        clean(): Validates the form data and performs additional cleaning.
        __init__(): Initializes the form instance.
    """

    class Meta:
        model = BoothLocation

        field_label_map = {
            "booth_location": _("Location Name"),
            "booth_address": _("Booth Address"),
            "booth_notes": _("Additional Booth Notes"),
            "booth_is_outside": _("Booth Is Outside"),
            "booth_block_level_restrictions_start": _("Lowest Troop Level"),
            "booth_block_level_restrictions_end": _("Highest Troop Level"),
            "booth_enabled": _("Booth Is Enabled"),
        }

        fields = list(field_label_map.keys())
        labels = field_label_map

        help_texts = {
            "booth_block_level_restrictions_start": _(
                "Select the lowest level troop that can use this booth, if none "
                "there are no restrictions"
            ),
            "booth_block_level_restrictions_end": _(
                "Select the highest level troop that can use this booth"
            ),
            "booth_enabled": _("Enabled means booth blocks are able to be reserved."),
        }

    def clean(self):
        """
        Clean and validate the form data.

        This method is responsible for cleaning and validating the form data before it is saved.
        It ensures that the location is unique by checking the booth location and address.
        It also validates the booth level restrictions.

        Raises:
            forms.ValidationError: If the location already exists or if the booth levels are invalid.

        Returns:
            None
        """
        # Ensure unique location by name and address
        location_filter = BoothLocation.objects.filter(
            booth_location=self.cleaned_data["booth_location"],
            booth_address=self.cleaned_data["booth_address"],
        )

        if location_filter.exists():
            cleaned_booth_id = location_filter.first().id

            if cleaned_booth_id != self.booth_id or self.booth_id is None:
                self.add_error("booth_location", "Please add a unique location.")
                self.add_error("booth_address", "Please add a unique address.")
                raise forms.ValidationError("This location already exists!")

        # Validate booth level restrictions
        start = self.cleaned_data["booth_block_level_restrictions_start"]
        end = self.cleaned_data["booth_block_level_restrictions_end"]

        if start > end != 0:
            error_message = "Restriction start must be lower than end"
            self.add_error("booth_block_level_restrictions_start", error_message)
            self.add_error("booth_block_level_restrictions_end", error_message)
            raise forms.ValidationError("Booth levels are invalid")

    def __init__(self, *args, **kwargs):
        """
        This is used to add booth_id to check if we're duplicating an item on edit.
        """
        try:
            self.booth_id = kwargs.pop("booth_id")
        except KeyError:
            self.booth_id = None
        super(BoothLocationForm, self).__init__(*args, **kwargs)


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

        fields = generate_fields()
        widgets = generate_widgets()
        labels = generate_labels()
        help_texts = {
            "booth_start_date": _("Enter the date sales will begin at this booth."),
            "booth_end_date": _("Enter the last date of sales for this booth."),
        }

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

        # Make sure we have valid times - both populated is needed if the checkbox is checked
        for day in DAYS_OF_WEEK:
            self.__check_times_set_correctly(day_of_week=day)

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


class EnableFreeForAll(forms.Form):

    start_date = forms.DateField(widget=DatePickerInput(options={"range_from": "booth days"}))
    end_date = forms.DateField(widget=DatePickerInput(options={"range_from": "booth days"}))
