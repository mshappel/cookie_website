import logging
from datetime import datetime

from django.db import models
from django.utils import timezone

from cookie_booths.models.managers.season_manager import SeasonManager
from utils.constants import DAYS_OF_WEEK

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class CookieSeason(models.Model):
    season_start_date = models.DateField(blank=True, null=True)
    season_end_date = models.DateField(blank=True, null=True)

    real_season_start_date = models.DateField(blank=True, null=True)

    ffa_day_of_week = models.SmallIntegerField(choices=DAYS_OF_WEEK, default=0)
    starting_weeks_reservable = models.SmallIntegerField(default=0)
    daisy_starting_weeks_offset = models.SmallIntegerField(default=1)

    objects: SeasonManager = SeasonManager()

    def __str__(self):
        # Makes the string in the admin site more useful
        return f"Cookie Season {self.season_start_date} to {self.season_end_date}"

    def cookie_season_week(self, current_date: datetime.date):
        """
        Determines which week in the season the current date exists.

        Args:
            current_date (datetime.date): The current date.

        Returns:
            int: The week number in the season.

        """
        # Determines which week in the season the current date exists
        return (current_date - self.real_season_start_date).days // 7 + 1

    def is_booth_reservable(self, booth_date):
        """
        Checks if a booth is reservable on a given date.

        Args:
            booth_date (datetime.date): The date to check for booth reservation.

        Returns:
            bool: True if the booth is reservable, False otherwise.
        """
        # Is the vieawable, but not reservable
        # Two conditions where a booth is viewable:
        # 1) If the booth date's week is less than or equal to the weeks reserable set by the SUCM
        # 2) If the booth date's week is less than or equal to the current cookie season week + 1.
        # EXAMPLE:
        # Let's say starting_weeks_reservable is 3, this means the first three of the cookie season
        # are immediately reservable. For subsequent weeks, let's say we're now in the 4th week of
        # sales. That means we should be able to see weeks 1-5.
        is_reservable = self.is_week_within_starting_weeks_reservable(
            booth_date=booth_date
        ) or self.is_week_before_or_equal_to_next_week(booth_date=booth_date)

        return is_reservable

    def is_daisy_booth_reservable(self, booth_date):
        """
        Checks if a Daisy booth is reservable on a given date.

        Args:
            booth_date (datetime.date): The date to check for Daisy booth reservation.

        Returns:
            bool: True if the Daisy booth is reservable, False otherwise.
        """
        cookie_week = self.cookie_season_week(current_date=booth_date)
        if cookie_week == self.daisy_starting_weeks_offset:
            return False

        return self.is_booth_reservable(booth_date=booth_date)

    def is_week_within_starting_weeks_reservable(self, booth_date: datetime.date) -> bool:
        return self.cookie_season_week(current_date=booth_date) <= self.starting_weeks_reservable

    def is_week_before_or_equal_to_next_week(self, booth_date: datetime.date) -> bool:
        current_date = timezone.datetime.today().date()
        current_season_week = self.cookie_season_week(current_date=current_date)
        booth_week = self.cookie_season_week(current_date=booth_date)
        return current_season_week + 1 >= booth_week
