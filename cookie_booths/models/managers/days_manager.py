import logging
from datetime import date
from typing import TYPE_CHECKING

from django.apps import apps
from django.db import models
from django.db.models import Q

from cookie_booths.models.managers.helpers.day_update_days import BoothDayUpdateDays

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

    def find_booth_days_outside_range_for_deletion(
        self,
        booth_location: "BoothLocation",
        start_date: date,
        end_date: date,
        deletions: list,
    ) -> None:
        """Collects booth days that are out of the specified date range for deletion.

        Args:
            booth_location (BoothLocation): The booth location instance to delete days for.
            start_date (date): The start date of the range.
            end_date (date): The end date of the range.
            deletions (list): List to collect deletions.
        """
        query = Q(booth_location=booth_location)

        if start_date and end_date:
            query &= Q(booth_day_date__lt=start_date) | Q(booth_day_date__gt=end_date)

        out_of_range_booth_days = self.filter(query).values_list("id", flat=True)
        deletions.extend(out_of_range_booth_days)

    def update_booth_day_attributes(self, booth_location: "BoothLocation") -> None:
        """
        Updates the booths for the given booth location. Will delete days no longer in range

        Args:
            booth_location (BoothLocation): The booth location instance to update hours for.
        """
        update_days = BoothDayUpdateDays(self.booth_day_model, booth_location)
        update_days.update_booth_common(BoothDayUpdateDays.update_booth_day_attributes)

    def enable_disable_booth_day(self, booth_location: "BoothLocation") -> None:
        """Updates the booth for the given booth location.

        Args:
            booth_location (BoothLocation): The booth location instance to update.
        """
        update_days = BoothDayUpdateDays(self.booth_day_model, booth_location)
        update_days.update_booth_common(BoothDayUpdateDays.enable_disable_booth_day)
