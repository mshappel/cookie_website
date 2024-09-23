import logging

from django.db import models

from cookie_booths.models.managers.schedule_manager import BoothScheduleManager
from utils.date_utils import parse_time

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothSchedule(models.Model):
    class Meta:
        verbose_name_plural = "Booth Daily Attributes"

    def __str__(self):
        # Easier to use admin names
        return f"{self.booth_location} Daily Attributes"

    booth_location = models.OneToOneField(
        "cookie_booths.BoothLocation",
        null=True,
        on_delete=models.CASCADE,
    )

    # Use a JSONField to store daily attributes
    booth_schedule: models.JSONField = models.JSONField(default=dict)

    objects: BoothScheduleManager = BoothScheduleManager()

    def save(self, *args, **kwargs):
        print(f"Before save: {self.booth_schedule}")

        # Ensure the JSONField has a default structure if it's empty
        if not self.booth_schedule:
            self.booth_schedule = {
                "monday": {"open": False, "open_time": None, "close_time": None},
                "tuesday": {"open": False, "open_time": None, "close_time": None},
                "wednesday": {"open": False, "open_time": None, "close_time": None},
                "thursday": {"open": False, "open_time": None, "close_time": None},
                "friday": {"open": False, "open_time": None, "close_time": None},
                "saturday": {
                    "open": False,
                    "open_time": None,
                    "close_time": None,
                    "golden_ticket": False,
                },
                "sunday": {
                    "open": False,
                    "open_time": None,
                    "close_time": None,
                    "golden_ticket": False,
                },
            }

        super().save(*args, **kwargs)
        print(f"After save: {self.booth_schedule}")

    def get_daily_attribute_day(self, day: str) -> dict:
        """
        Retrieve the value of a specific attribute for a given day.

        Args:
            day (str): The day for which to retrieve the attribute value.

        Returns:
            The value of the specified day's attributes.
        """
        attributes: dict = self.booth_schedule.get(day, {})
        attributes["open_time"] = parse_time(attributes.get("open_time"))
        attributes["close_time"] = parse_time(attributes.get("close_time"))
        return attributes

    def set_daily_attribute(self, day: str, attribute: str, value: any) -> None:
        """
        Set the value of a specific attribute for a given day.

        Args:
            day (str): The day for which the attribute value is being set.
            attribute (str): The name of the attribute.
            value (any): The value to be set for the attribute.

        Returns:
            None
        """
        if day not in self.booth_schedule:
            self.booth_schedule[day] = {}
        self.booth_schedule[day][attribute] = value
        self.save()

    def set_daily_attributes(self, daily_attributes: dict) -> None:
        """
        Set the daily attributes for the booth.

        Args:
            daily_attributes (dict): The daily attributes to set.

        Returns:
            None
        """
        self.booth_schedule = daily_attributes
        self.save()
