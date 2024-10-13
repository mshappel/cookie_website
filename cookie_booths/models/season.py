import logging
from datetime import date, datetime
from typing import Optional

from django.db import models
from django.utils import timezone

from cookie_booths.models.managers.season_manager import SeasonManager
from utils.constants import DayOfWeek
from utils.enum_conversation import enum_choices_to_tuple

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class CookieSeason(models.Model):
    season_start_date = models.DateField(blank=True, null=True)
    season_end_date = models.DateField(blank=True, null=True)

    real_season_start_date = models.DateField(blank=True, null=True)

    ffa_day_of_week = models.SmallIntegerField(choices=enum_choices_to_tuple(DayOfWeek), default=0)
    starting_weeks_reservable = models.SmallIntegerField(default=0)
    daisy_starting_weeks_offset = models.SmallIntegerField(default=1)

    objects: SeasonManager = SeasonManager()

    def __str__(self):
        # Makes the string in the admin site more useful
        return f"Cookie Season {self.season_start_date} to {self.season_end_date}"

    @staticmethod
    def get_cookie_season_start_date():
        try:
            return CookieSeason.objects.get().season_start_date
        except CookieSeason.DoesNotExist:
            return date.today()

    @staticmethod
    def get_cookie_season_end_date():
        try:
            return CookieSeason.objects.get().season_end_date
        except CookieSeason.DoesNotExist:
            return date.today()

    def cookie_season_week(self, date_to_check: datetime.date) -> int:
        """
        Determines which week in the season the current date exists.

        Args:
            date_to_check (datetime.date): The current date.

        Returns:
            int: The week number in the season.

        """
        # Determines which week in the season the current date exists
        cookie_week = (date_to_check - self.real_season_start_date).days // 7 + 1
        _logger.debug("%s is cookie week: %s", date_to_check, cookie_week)
        return cookie_week

    def is_booth_reservable(
        self, booth_date: datetime.date, test_date: Optional[datetime.date] = None
    ) -> bool:
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
        is_within_starting_weeks = self._is_week_within_starting_weeks_reservable(
            booth_date=booth_date,
        )
        is_before_or_equal_to_next_week = self._is_week_before_or_equal_to_next_week(
            booth_date=booth_date,
            test_date=test_date,
        )
        is_within_cookie_season = self._is_between_cookie_season(
            booth_date=booth_date,
        )

        is_reservable = (
            is_within_starting_weeks or is_before_or_equal_to_next_week
        ) and is_within_cookie_season
        return is_reservable

    def is_daisy_booth_reservable(self, booth_date) -> bool:
        """
        Checks if a Daisy booth is reservable on a given date.

        Args:
            booth_date (datetime.date): The date to check for Daisy booth reservation.

        Returns:
            bool: True if the Daisy booth is reservable, False otherwise.
        """
        cookie_week = self.cookie_season_week(date_to_check=booth_date)
        if cookie_week == self.daisy_starting_weeks_offset:
            return False

        return self.is_booth_reservable(booth_date=booth_date)

    def _is_week_within_starting_weeks_reservable(self, booth_date: datetime.date) -> bool:
        """
        Check if a given booth date falls within the reservable starting weeks of the cookie season.

        Args:
            booth_date (datetime.date): The date of the booth to check.

        Returns:
            bool: True if the booth date is within the reservable starting weeks, False otherwise.
        """
        is_within_starting_weeks = (
            self.cookie_season_week(date_to_check=booth_date) <= self.starting_weeks_reservable
        )
        _logger.debug("Is %s within starting weeks: %s", booth_date, is_within_starting_weeks)
        return is_within_starting_weeks

    def _is_week_before_or_equal_to_next_week(
        self, booth_date: datetime.date, test_date: Optional[datetime.date] = None
    ) -> bool:
        """
        Determines if the given booth date is within the current week or the next week of the
        cookie season.

        Args:
            booth_date (datetime.date): The date of the booth to check.

        Returns:
            bool: True if the booth date is within the current week or the next week of the cookie
                season, False otherwise.
        """
        current_date = test_date if test_date else timezone.datetime.today().date()
        current_season_week = self.cookie_season_week(date_to_check=current_date)
        booth_week = self.cookie_season_week(date_to_check=booth_date)
        is_within_current_or_next_week = booth_week <= current_season_week + 1
        _logger.debug(
            "Is %s within current or next week: %s", booth_date, is_within_current_or_next_week
        )
        _logger.debug("Current week: %s & booth week: %s", current_season_week, booth_week)
        return is_within_current_or_next_week

    def _is_between_cookie_season(self, booth_date: datetime.date) -> bool:
        """
        Determines if the given booth date is within the cookie season.

        Args:
            booth_date (datetime.date): The date of the booth to check.

        Returns:
            bool: True if the booth date is within the cookie season, False otherwise.
        """
        is_within_season = self.season_start_date <= booth_date <= self.season_end_date
        _logger.debug(
            "Season start: %s, Season end: %s", self.season_start_date, self.season_end_date
        )
        _logger.debug("Is %s within season: %s", booth_date, is_within_season)
        return is_within_season
