import logging
from typing import TYPE_CHECKING

from django.apps import apps
from django.db import models

if TYPE_CHECKING:
    from cookie_booths.models.daily_attributes import BoothDailyAttributes
    from cookie_booths.models.location import BoothLocation

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothAttributesManager(models.Manager):
    def fetch_booth_daily_attributes(
        self,
        booth_location: "BoothLocation",
    ) -> "BoothDailyAttributes":
        """Fetches the booth hours for the given booth location.

        Args:
            booth_location (BoothLocation): The booth location instance to fetch hours for.

        Returns:
            BoothHours: The booth hours instance.
        """
        _logger.debug("Fetching booth hours for booth location %s", str(booth_location))
        booth_hours_model: "BoothDailyAttributes" = apps.get_model(
            "cookie_booths.BoothDailyAttributes"
        )
        return booth_hours_model.objects.get(booth_location=booth_location)
