import datetime
import logging
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from cookie_booths.models.season import CookieSeason

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class SeasonManager(models.Manager):
    def is_booth_reservable_for_date(self, booth_day: datetime.date) -> bool:
        """
        Checks if a booth is reservable for a given date.

        Args:
            booth_day (datetime.date): The date to check for booth reservation.
            
        Returns:
            bool: True if the booth is reservable for the given date, False otherwise.
        """
        season: "CookieSeason" = self.get(
            Q(season_start_date__lte=booth_day) & Q(season_end_date__gte=booth_day)
        )
        if season is None:
            return False
        return season.is_booth_reservable(booth_date=booth_day)
