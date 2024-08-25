from django.db import models

from cookie_booths.models.location import BoothLocation


class BoothHours(models.Model):
    class Meta:
        verbose_name_plural = "Booth hours"

    def __str__(self):
        # Easier to use admin names
        return f"{self.booth_location} Hours"

    booth_location = models.OneToOneField(BoothLocation, null=True, on_delete=models.CASCADE)
    booth_start_date = models.DateField(blank=True, null=True)
    booth_end_date = models.DateField(blank=True, null=True)

    # Use a JSONField to store daily attributes
    daily_attributes: models.JSONField = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        # Ensure the JSONField has a default structure if it's empty
        if not self.daily_attributes:
            self.daily_attributes = {
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

    def get_daily_attribute(self, day: str, attribute: str) -> any:
        """
        Retrieve the value of a specific attribute for a given day.

        Args:
            day (str): The day for which to retrieve the attribute value.
            attribute (str): The name of the attribute to retrieve.

        Returns:
            The value of the specified attribute for the given day, or None if the attribute or day does not exist.
        """
        return self.daily_attributes.get(day, {}).get(attribute)

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
        if day not in self.daily_attributes:
            self.daily_attributes[day] = {}
        self.daily_attributes[day][attribute] = value
        self.save()
