import logging

from django import forms
from django.utils.translation import gettext as _

from cookie_booths.models import BoothLocation

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


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
