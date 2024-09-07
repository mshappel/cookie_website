import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Callable, Tuple, TypedDict

from django.db.models import Q

from cookie_booths.models.blocks import BoothBlock

if TYPE_CHECKING:
    from cookie_booths.models.day import BoothDay

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

HOURS_ADJUST_FORWARD = 2
HOURS_ADJUST_BACKWARD = -1 * HOURS_ADJUST_FORWARD


class StartEnd(TypedDict):
    start_time: datetime
    end_time: datetime
    cont: bool


class BoothDayHourManager:

    def __init__(self, booth_day: "BoothDay", open_time: datetime, close_time: datetime) -> None:
        self.booth_day = booth_day
        self.open_time = open_time
        self.close_time = close_time

    def add_or_update_hours(self) -> None:
        """
        Adds or updates the hours for a booth day.

        Returns:
            None
        """
        # There are two cases to handle:
        # (1) Hours have been previously set or (2) the hours have not be previously set
        _logger.info("Adding or updating booth day hours")
        if self.booth_day.booth_day_hours_set:
            _logger.debug("Hours have been previously set")
            # (1) Hours have been previously set
            if self._is_same_open_close_time():
                _logger.debug("Open and close times are the same, so no need to update")
                # Escape if the open and close times are the same
                return

            # Hours differ, so clear the overlap blocks and update the booth day hours
            _logger.debug(
                "Open and close times differ, so clear overlap blocks and update booth day hours"
            )
            self._clear_overlap_blocks()
            self._update_booth_day_hours()
        else:
            # (2) Hours have not been previously set
            _logger.debug("Hours have not been previously set")
            self._initialize_blocks_if_not_set()

        _logger.info("Booth day hours have been set")
        self._set_and_save_booth_days()

    def _set_and_save_booth_days(self):
        self.booth_day.booth_day_hours_set = True
        self.booth_day.booth_day_open_time = self.open_time
        self.booth_day.booth_day_close_time = self.close_time
        self.booth_day.save()

    def _initialize_blocks_if_not_set(self) -> None:
        start_end = (self.open_time, self.open_time + timedelta(hours=2), True)
        self._add_blocks(start_end, self._adjust_times_forwards)

    def _update_booth_day_hours(self) -> None:
        """
        Updates the booth day hours by adding or clearing blocks based on the current state.
        """
        # In order to minimize database queries, we will first query all blocks for the booth day
        blocks = list(
            BoothBlock.objects.filter(booth_day__id=self.booth_day.id).order_by(
                "booth_block_start_time"
            )
        )

        if not blocks:
            self.booth_day.booth_day_hours_set = False
        else:
            first_block = blocks[0]  # This is the first block
            start_end = {
                "start_time": first_block.booth_block_start_time - timedelta(hours=2),
                "end_time": first_block.booth_block_start_time,
                "cont": True,
            }
            self._add_blocks(start_end, self._adjust_times_backwards)

            last_block = blocks[-1]  # This is the last block
            start_end = {
                "start_time": last_block.booth_block_end_time,
                "end_time": last_block.booth_block_end_time + timedelta(hours=2),
                "cont": True,
            }
            self._add_blocks(start_end, self._adjust_times_forwards)

    def _clear_overlap_blocks(self) -> None:
        """
        Clears the BoothBlock objects that overlap with the specified open and close times
        for a booth day.
        """
        BoothBlock.objects.filter(
            Q(booth_day__id=self.booth_day.id),
            Q(booth_block_start_time__lt=self.open_time)
            | Q(booth_block_end_time__gt=self.close_time),
        ).delete()

    # fmt: off
    def _add_blocks(self, start_end: StartEnd, adjust_times: Callable[[StartEnd], StartEnd]) -> StartEnd: # noqa E501
        # fmt: on
        """
        Add blocks of time to the given start and end time based on the provided direction
        function.

        Args:
            start_end (StartEnd): A dict representing the start and end time.
            adjust_times (Callable[[StartEnd], StartEnd]): A function that takes a StartEnd dict
                and returns a modified StartEnd dict.

        Returns:
            StartEnd: The modified start and end time after adding blocks.
        """
        new_blocks = []

        while start_end["end_time"].hour <= self.close_time.hour and start_end["cont"]:
            new_block = BoothBlock(
                booth_day=self.booth_day,
                booth_block_start_time=start_end["start_time"],
                booth_block_end_time=start_end["end_time"],
                booth_block_reserved=False,
                booth_block_enabled=self.booth_day.booth_day_enabled,
            )
            new_blocks.append(new_block)

            start_end = adjust_times(start_end)

            # If it is the end of the day and there isn't enough time to add a block,
            # do not create additional blocks.
            if start_end["end_time"] - start_end["start_time"] != timedelta(hours=2):
                start_end["cont"] = False

        # In order to minimize database queries, we will use bulk_create
        BoothBlock.objects.bulk_create(new_blocks)

        return start_end

    def _is_same_open_close_time(self) -> bool:
        """
        Check if the given open and close times are the same as those in the booth day.

        Returns:
            bool: True if both open and close times are the same, False otherwise.
        """
        is_same_open_time = self.open_time == self.booth_day.booth_day_open_time
        is_same_close_time = self.close_time == self.booth_day.booth_day_close_time
        return is_same_open_time and is_same_close_time

    def _adjust_time_within_bounds(self, time: int) -> Tuple[int, bool]:
        """
        Adjusts the given time within the bounds of 0 to 23.

        Args:
            time (int): The time value to be adjusted.

        Returns:
            int: The adjusted time value within the bounds of 0 to 23.
            bool: True if the time value was adjusted, False otherwise.
        """
        if time > 23:
            return 23, False
        elif time < 0:
            return 0, False
        return time, True

    def _adjust_times(self, start_end: StartEnd, adjust_value: int) -> StartEnd:
        new_start_time = start_end["start_time"].hour + adjust_value
        new_start_time, cont_start = self._adjust_time_within_bounds(new_start_time)

        new_end_time = start_end["end_time"].hour + adjust_value
        new_end_time, cont_end = self._adjust_time_within_bounds(new_end_time)

        cont = cont_start and cont_end

        new_start_end = {
            "start_time": start_end["start_time"],
            "end_time": start_end["end_time"],
            "cont": cont,
        }
        return new_start_end

    def _adjust_times_forwards(self, start_end: StartEnd) -> StartEnd:
        return self._adjust_times(start_end, HOURS_ADJUST_FORWARD)

    def _adjust_times_backwards(self, start_end: StartEnd) -> StartEnd:
        return self._adjust_times(start_end, HOURS_ADJUST_BACKWARD)
