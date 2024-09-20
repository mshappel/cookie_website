import logging
from datetime import datetime, time
from typing import TYPE_CHECKING, Optional

from django.db import models
from pytz import utc

from cookie_booths.models.blocks import BoothBlock
from cookie_booths.models.helpers.day_update_blocks import BoothDayUpdateBlocks
from cookie_booths.models.managers.days_manager import BoothDayManager

if TYPE_CHECKING:

    from cookie_booths.models.location import BoothLocation

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothDay(models.Model):
    """Contains data relevant for a day of a booth"""

    booth_location: "BoothLocation" = models.ForeignKey(
        "cookie_booths.BoothLocation",
        on_delete=models.CASCADE,
    )

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
        return f"{self.booth_location} on {self.booth_day_date}"

    def update_golden_status(self, is_golden_booth: bool) -> None:
        _logger.debug("Changing golden status of booth day %s to %s", str(self), is_golden_booth)
        self.booth_day_is_golden = is_golden_booth
        self.save()

    def enable_day(self) -> bool:
        return self._set_day_enabled(True)

    def disable_day(self) -> bool:
        return self._set_day_enabled(False)

    def enable_freeforall(self) -> bool:
        return self._set_freeforall_enabled(True)

    def disable_freeforall(self) -> bool:
        return self._set_freeforall_enabled(False)

    def add_or_update_hours(self, open_time: datetime, close_time: datetime) -> None:
        """
        Add or update the hours for a booth day.

        Args:
            open_time (datetime): The open time for the booth day.
            close_time (datetime): The close time for the booth day.

        Returns:
            None
        """
        update_blocks = BoothDayUpdateBlocks(self, open_time, close_time)
        update_blocks.add_or_update_hours_per_day()

    def update_day(
        self,
        open_time: time,
        close_time: time,
        is_golden: bool,
    ) -> None:
        """
        Updates the booth day with the given open and close times and golden booth status.

        Args:
            open_time (datetime.time): The opening time of the booth.
            close_time (datetime.time): The closing time of the booth.
            is_golden (bool): Indicates whether the booth is a golden booth or not.

        Returns:
            None
        """
        day = self.booth_day_date
        open_datetime = datetime.combine(day, open_time, tzinfo=utc)
        close_datetime = datetime.combine(day, close_time, tzinfo=utc)

        # Add or update hours per day using BoothDayUpdateBlocks
        booth_day_update_blocks = BoothDayUpdateBlocks(
            booth_day_instance=self,
            open_time=open_datetime,
            close_time=close_datetime,
            is_golden=is_golden,
        )
        booth_day_update_blocks.add_or_update_hours_per_day()

    def _set_enabled(
        self,
        enabled: bool,
        day_attr: str,
        block_attr: Optional[str] = None,
        block_method: Optional[str] = None,
    ) -> bool:
        """
        Set the enabled state of a booth day and its associated booth blocks.

        Args:
            enabled (bool): The desired enabled state.
            day_attr (str): The attribute name of the booth day to be modified.
            block_attr (str, optional): The attribute name of the booth blocks to be modified.
                Defaults to None.
            block_method (str, optional): The method name of the booth blocks to be called.
                Defaults to None.

        Returns:
            bool: True if the enabled state was successfully modified, False otherwise.
        """

        # If the state is already as desired, nothing to do
        if getattr(self, day_attr) == enabled:
            return False

        _logger.debug("Setting %s to %s for %s", day_attr, enabled, str(self))
        setattr(self, day_attr, enabled)
        block: "BoothBlock"
        for block in BoothBlock.objects.get_booth_blocks_for_day(self):

            if block_attr:
                setattr(block, block_attr, enabled)
            if block_method:
                getattr(block, block_method)()
            block.save()

        self.save()

        return True

    def _set_day_enabled(self, day_id: int, enabled: bool) -> bool:
        return self._set_enabled(
            day_id=day_id,
            enabled=enabled,
            day_attr="booth_day_enabled",
            block_method="enable_block" if enabled else "disable_block",
        )

    def _set_freeforall_enabled(self, day_id: int, enabled: bool) -> bool:
        return self._set_enabled(
            day_id=day_id,
            enabled=enabled,
            day_attr="booth_day_freeforall_enabled",
            block_attr="booth_block_freeforall_enabled",
        )
