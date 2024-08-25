from datetime import date, datetime, timedelta
from typing import Generator

from django.db import models
from django.db.models import Q
from pytz import utc

from cookie_booths.models.helpers import _get_booth_day_model, _get_booth_hours_model
from cookie_booths.models.managers.location_manager import BoothLocationManager
from utils.constants import (
    GIRL_SCOUT_TROOP_LEVELS_WITH_NONE,
    GOLDEN_TICKET_DAYS,
    WEEKDAY_MAPPING,
)


class BoothLocation(models.Model):
    """Contains data relevant for booths"""

    # ID is referenced via Django object ID
    booth_location = models.CharField(max_length=300)
    booth_address = models.CharField(max_length=300)

    booth_enabled = models.BooleanField(default=False)

    booth_block_level_restrictions_start = models.SmallIntegerField(
        choices=GIRL_SCOUT_TROOP_LEVELS_WITH_NONE, default=0
    )
    booth_block_level_restrictions_end = models.SmallIntegerField(
        choices=GIRL_SCOUT_TROOP_LEVELS_WITH_NONE, default=0
    )

    booth_is_outside = models.BooleanField(default=False)
    booth_notes = models.CharField(max_length=100, blank=True)

    objects: BoothLocationManager = BoothLocationManager()

    class Meta:
        verbose_name_plural = "booth locations"
        verbose_name = "booth location"

    def __str__(self):
        return self.booth_location

    def update_hours(self):
        # We need to create or delete booth days, or update their hours, based on new hours, and
        # we have a few steps for this
        BoothHours = _get_booth_hours_model()
        hours = BoothHours.objects.get(booth_location=self)
        BoothDay = _get_booth_day_model()

        # If no date is set for either start or end date, delete all days owned by this booth
        if hours.booth_start_date is None or hours.booth_end_date is None:
            BoothDay.objects.filter(booth=self).delete()
            return

        # Delete any days outside of the new start/end date - this will cascade down to the blocks
        BoothDay.objects.filter(
            Q(booth=self),
            Q(booth_day_date__lt=hours.booth_start_date)
            | Q(booth_day_date__gt=hours.booth_end_date),
        ).delete()

        # Go through each day between the new start and end date
        for day in self.__daterange(hours.booth_start_date, hours.booth_end_date):
            # Define a list to map weekdays to their corresponding attributes

            # Get the current weekday
            weekday = day.weekday()

            # Retrieve the corresponding day name
            day_name = WEEKDAY_MAPPING[weekday]

            # Retrieve the daily attributes for the given day
            open_status = hours.get_daily_attribute(day_name, "open")
            open_time = hours.get_daily_attribute(day_name, "open_time")
            close_time = hours.get_daily_attribute(day_name, "close_time")
            golden_ticket = hours.get_daily_attribute(day_name, "golden_ticket")

            # Check if the booth is closed on the given day
            if not open_status:
                BoothDay.objects.filter(booth=self.booth_location, booth_day_date=date).delete()
            else:
                # Perform the operations
                open_datetime = datetime.combine(
                    day, datetime.strptime(open_time, "%H:%M:%S").time(), tzinfo=utc
                )
                close_datetime = datetime.combine(
                    day, datetime.strptime(close_time, "%H:%M:%S").time(), tzinfo=utc
                )

                self.add_or_update_day(day, open_datetime, close_datetime)

                if weekday in GOLDEN_TICKET_DAYS:
                    self.update_golden_day(day, golden_ticket)

        return

    def update_booth(self):
        BoothHours = _get_booth_hours_model()
        hours = BoothHours.objects.get(booth_location=self)
        BoothDay = _get_booth_day_model()

        # If no date is set for either start or end date, delete all days owned by this booth
        if hours.booth_start_date is None or hours.booth_end_date is None:
            BoothDay.objects.filter(booth=self).delete()
            return

        # Go through each day between the new start and end date
        for day in self.__daterange(hours.booth_start_date, hours.booth_end_date):
            # Get the current weekday
            weekday = day.weekday()

            # Retrieve the corresponding day name
            day_name = WEEKDAY_MAPPING[weekday]

            # Retrieve the daily attributes for the given day
            open_status = hours.get_daily_attribute(day_name, "open")

            # Check if the booth is open on the given day
            if open_status:
                booth_day = self.__booth_day_exist(day)
                if self.booth_enabled:
                    booth_day.enable_day()
                else:
                    booth_day.disable_day()
            else:
                BoothDay.objects.filter(booth=self.booth_location, booth_day_date=day).delete()

        return

    def add_or_update_day(self, day, open_time, close_time):
        # First see if we have a Booth_Day existing for that date. If so, grab it and update the open/close time
        booth_day = self.__booth_day_exist(day=day)

        # Set the hours
        booth_day.add_or_update_hours(open_time, close_time)
        booth_day.save()

        return

    def update_golden_day(self, day, is_golden_booth):
        # First see if we have a Booth_Day existing for that date. If so, grab it and update the open/close time
        booth_day = self.__booth_day_exist(day=day)

        # Set the golden ticket
        booth_day.change_golden_status(is_golden_booth=is_golden_booth)
        booth_day.save()

        return

    def passes_level_restrictions(self, troop_level):
        booth_restrictions_start = self.booth_block_level_restrictions_start
        booth_restrictions_end = self.booth_block_level_restrictions_end

        if booth_restrictions_start:
            return troop_level in range(booth_restrictions_start, booth_restrictions_end + 1)
        return True

    @staticmethod
    def __daterange(start_date: date, end_date: date) -> Generator[date, None, None]:
        # Need +1 to be inclusive of the end date
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)

    def __booth_day_exist(self, day):
        BoothDay = _get_booth_day_model()

        try:
            booth_day = BoothDay.objects.get(booth=self, booth_day_date=day)

        except BoothDay.DoesNotExist:
            # If it doesn't exist yet, create it
            booth_day = BoothDay.objects.create(
                booth=self,
                booth_day_date=day,
                booth_day_enabled=False,
                booth_day_hours_set=False,
            )

        return booth_day
