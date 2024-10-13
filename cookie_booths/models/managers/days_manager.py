import logging
from datetime import date
from typing import TYPE_CHECKING

from django.apps import apps
from django.db import models

if TYPE_CHECKING:
    from cookie_booths.models.day import BoothDay
    from cookie_booths.models.location import BoothLocation

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothDayManager(models.Manager):
    @property
    def booth_day_model(self) -> "BoothDay":
        """Property to cast self.model to BoothDay."""
        model = apps.get_model("cookie_booths", "BoothDay")
        print(f"Model: {model}")
        return model

    def order_booth_days(self):
        return self.booth_day_model.objects.order_by("booth_location", "booth_day_date")

    def get_existing_booth_days_in_bulk(
        self, location: "BoothLocation", booth_start_date: date, booth_end_date: date
    ) -> models.QuerySet:
        """
        Retrieves existing booth days for a given location within a specified date range.
        Args:
            location (BoothLocation): The location of the booth.
            booth_start_date (date): The start date of the booth.
            booth_end_date (date): The end date of the booth.
        Returns:
            models.QuerySet: A queryset containing the existing booth days within the specified date range,
                             indexed by the booth day date.
        """
        existing_booth_days = self.booth_day_model.objects.filter(
            booth_location=location,
            booth_day_date__range=[booth_start_date, booth_end_date],
        ).in_bulk(field_name="booth_day_date")
        return existing_booth_days
