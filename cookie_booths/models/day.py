import logging

from django.db import models

from cookie_booths.models.location import BoothLocation
from cookie_booths.models.managers.days_manager import BoothDayManager

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothDay(models.Model):
    """Contains data relevant for a day of a booth"""

    booth = models.ForeignKey(BoothLocation, on_delete=models.CASCADE)

    booth_day_date = models.DateField(blank=True, null=True)

    booth_day_hours_set = models.BooleanField(default=False)
    booth_day_open_time = models.DateTimeField(blank=True, null=True)
    booth_day_close_time = models.DateTimeField(blank=True, null=True)
    booth_day_is_golden = models.BooleanField(default=False)

    booth_day_enabled = models.BooleanField(default=False)
    booth_day_freeforall_enabled = models.BooleanField(default=False)

    objects: BoothDayManager = BoothDayManager()

    class Meta:
        permissions = (("update_booth_day", "Update booth day"),)

    def __str__(self):
        # More useful name in the admin site
        return f"{self.booth} on {self.booth_day_date}"

    def change_golden_status(self, is_golden_booth):
        _logger.debug("Changing golden status of booth day %s to %s", str(self), is_golden_booth)
        self.booth_day_is_golden = is_golden_booth
        self.save()
