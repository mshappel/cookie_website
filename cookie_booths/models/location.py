import logging

from django.db import models

from cookie_booths.models.managers.location_manager import BoothLocationManager
from utils.constants import GIRL_SCOUT_TROOP_LEVELS_WITH_NONE

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothLocation(models.Model):
    """Contains data relevant for booths"""

    # ID is referenced via Django object ID
    booth_location = models.CharField(max_length=300, blank=False, null=False)
    booth_address = models.CharField(max_length=300, blank=False, null=False)

    booth_enabled = models.BooleanField(default=False, blank=False, null=False)

    booth_block_level_restrictions_start = models.SmallIntegerField(
        choices=GIRL_SCOUT_TROOP_LEVELS_WITH_NONE, default=0, blank=False, null=False
    )
    booth_block_level_restrictions_end = models.SmallIntegerField(
        choices=GIRL_SCOUT_TROOP_LEVELS_WITH_NONE, default=0, blank=False, null=False
    )

    booth_start_date = models.DateField(blank=False, null=False)
    booth_end_date = models.DateField(blank=False, null=False)

    booth_is_outside = models.BooleanField(default=False, blank=False, null=False)
    booth_notes = models.CharField(max_length=100, blank=True)

    objects: BoothLocationManager = BoothLocationManager()

    class Meta:
        verbose_name_plural = "booth locations"
        verbose_name = "booth location"

    def __str__(self):
        return self.booth_location

    def passes_level_restrictions(self, troop_level: int) -> bool:
        """
        Checks if the troop level passes the level restrictions for the booth.

        Args:
            troop_level (int): The level of the troop.

        Returns:
            bool: True if the troop level passes the level restrictions, False otherwise.
        """
        booth_restrictions_start = self.booth_block_level_restrictions_start
        booth_restrictions_end = self.booth_block_level_restrictions_end

        if booth_restrictions_start:
            return troop_level in range(booth_restrictions_start, booth_restrictions_end + 1)
        return True
