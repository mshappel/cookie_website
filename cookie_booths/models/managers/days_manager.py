import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from django.db import models

from cookie_booths.models.blocks import BoothBlock
from cookie_booths.models.managers.days_manager_helper import BoothDayHourManager

if TYPE_CHECKING:
    from cookie_booths.models.day import BoothDay

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothDayManager(models.Manager):
    def order_booth_days(self):
        return self.order_by("booth", "booth_day_date")

    def enable_day(self, day_id: int) -> bool:
        return self._set_day_enabled(day_id, True)

    def disable_day(self, day_id: int) -> bool:
        return self._set_day_enabled(day_id, False)

    def enable_freeforall(self, day_id: int) -> bool:
        return self._set_freeforall_enabled(day_id, True)

    def disable_freeforall(self, day_id: int) -> bool:
        return self._set_freeforall_enabled(day_id, False)

    def add_or_update_hours(
        self, booth_day: "BoothDay", open_time: datetime, close_time: datetime
    ) -> None:
        """
        Add or update the hours for a booth day.

        Args:
            booth_day (BoothDay): The booth day to add or update hours for.
            open_time (datetime): The open time for the booth day.
            close_time (datetime): The close time for the booth day.

        Returns:
            None
        """
        BoothDayHourManager(booth_day, open_time, close_time).add_or_update_hours()

    def _set_enabled(
        self,
        day_id: int,
        enabled: bool,
        day_attr: str,
        block_attr: Optional[str] = None,
        block_method: Optional[str] = None,
    ) -> bool:
        """
        Set the enabled state of a booth day and its associated booth blocks.

        Args:
            day_id (int): The ID of the booth day.
            enabled (bool): The desired enabled state.
            day_attr (str): The attribute name of the booth day to be modified.
            block_attr (str, optional): The attribute name of the booth blocks to be modified.
                Defaults to None.
            block_method (str, optional): The method name of the booth blocks to be called.
                Defaults to None.

        Returns:
            bool: True if the enabled state was successfully modified, False otherwise.
        """
        day: "BoothDay" = self.get(id=day_id)

        # If the state is already as desired, nothing to do
        if getattr(day, day_attr) == enabled:
            return False

        _logger.debug("Setting %s to %s for %s", day_attr, enabled, str(day))
        setattr(day, day_attr, enabled)

        block: BoothBlock
        for block in BoothBlock.objects.filter(booth_day__id=day_id):
            if block_attr:
                setattr(block, block_attr, enabled)
            if block_method:
                getattr(block, block_method)()
            block.save()

        day.save()

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
