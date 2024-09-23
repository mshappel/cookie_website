import logging
from datetime import date
from typing import TYPE_CHECKING, Callable

from cookie_booths.models.schedule import BoothSchedule
from cookie_booths.models.helpers.day_update_blocks import BoothDayUpdateBlocks
from cookie_booths.models.location import BoothLocation
from utils.date_utils import date_range_generator

if TYPE_CHECKING:
    from cookie_booths.models.day import BoothDay

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothDayUpdateDays:

    def __init__(self, booth_day: "BoothDay", booth_location: BoothLocation) -> None:
        self.booth_day: "BoothDay" = booth_day
        self.booth_location = booth_location

    def update_booth_common(
        self,
        process_day_method: Callable[["BoothLocation", BoothSchedule, date], None],
    ) -> None:
        """Common logic for updating booth location.

        Args:
            process_day_method (Callable): The method to process each day.
        """
        booth_start_date: date = self.booth_location.booth_start_date
        booth_end_date: date = self.booth_location.booth_end_date

        daily_attributes_for_day: BoothSchedule = BoothSchedule.objects.fetch_booth_schedule(
            booth_location=self.booth_location
        )

        # Collect operations for bulk processing
        deletions = []

        self.booth_day.objects.find_booth_days_outside_range_for_deletion(
            booth_location=self.booth_location,
            start_date=booth_start_date,
            end_date=booth_end_date,
            deletions=deletions,
        )

        for day in date_range_generator(start_date=booth_start_date, end_date=booth_end_date):
            process_day_method(self.booth_location, daily_attributes_for_day, day)

        # Perform bulk operations
        self.delete_days_in_bulk(deletions=deletions)

    def delete_days_in_bulk(self, deletions: list) -> None:
        """Performs bulk operations for deleting booth days.

        Args:
            deletions (list): List of deletions.
        """
        # Perform bulk deletions
        if deletions:
            BoothDay.objects.filter(id__in=deletions).delete()

    def update_booth_day_attributes(
        self,
        booth_location: "BoothLocation",
        daily_attributes: BoothSchedule,
        day: date,
        deletions: list,
    ) -> None:
        """Processes a single day within the date range.

        Args:
            booth_location (BoothLocation): The booth location instance.
            daily_attributes (BoothDailyAttributes): The booth daily attributes instance.
            day (date): The day to process.
            updates (list): List to collect updates.
            deletions (list): List to collect deletions.
        """
        daily_attributes_for_day: dict = daily_attributes.get(day)

        if not daily_attributes_for_day:
            deletions.append(day)
        else:
            open_status = daily_attributes_for_day.get("open")
            open_time = daily_attributes_for_day.get("open_time")
            close_time = daily_attributes_for_day.get("close_time")
            is_golden = daily_attributes_for_day.get("golden_ticket")

            if not open_status:
                deletions.append(day)
            else:
                booth_day_instance: "BoothDay"
                booth_day_instance, _ = self.booth_day.objects.get_or_create(
                    booth_location=booth_location, date=day
                )
                booth_day_update_blocks = BoothDayUpdateBlocks(
                    booth_day_instance=booth_day_instance,
                    open_time=open_time,
                    close_time=close_time,
                    is_golden=is_golden,
                )
                booth_day_update_blocks.add_or_update_hours_per_day()

    def enable_disable_booth_day(
        self,
        booth_location: "BoothLocation",
        daily_attributes: BoothSchedule,
        day: date,
        deletions: list,
    ) -> None:
        """Processes a single day within the date range.

        Args:
            booth_location (BoothLocation): The booth location instance.
            hours (BoothHours): The booth hours instance.
            day (date): The day to process.
        """
        # Retrieve the daily attributes for the given day
        daily_attributes_for_day: dict = daily_attributes.get(day)
        open_status = daily_attributes_for_day.get("open")

        # Check if the booth is open on the given day
        if open_status:
            booth_day_instance: "BoothDay"
            booth_day_instance, _ = self.booth_day.objects.get_or_create(
                booth_location=booth_location, date=day
            )
            if booth_location.booth_enabled:
                booth_day_instance.enable_day()
            else:
                booth_day_instance.disable_day()
        else:
            deletions.append(day)
