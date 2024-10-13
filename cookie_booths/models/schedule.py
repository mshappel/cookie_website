import logging
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING

from dateutil.rrule import DAILY, rrule
from django.apps import apps
from django.db import models, transaction

from cookie_booths.models.managers.schedule_manager import BoothScheduleManager
from cookie_booths.models.season import CookieSeason
from utils.constants import GOLDEN_TICKET_LIST, DayOfWeek
from utils.date_utils import TIME_BLOCK_IN_HOURS, TIME_BLOCK_IN_SECONDS, parse_time

if TYPE_CHECKING:
    from cookie_booths.models.day import BoothDay
    from cookie_booths.models.time_block import BoothTimeBlock

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def get_default_end_date() -> date:
    return CookieSeason.get_cookie_season_end_date()


def get_default_start_date() -> date:
    return CookieSeason.get_cookie_season_start_date()


class BoothSchedule(models.Model):
    class Meta:
        verbose_name_plural = "Booth Schedules"

    def __str__(self):
        # Easier to use admin names
        return f"{self.booth_location} Schedule"

    booth_location = models.OneToOneField(
        "cookie_booths.BoothLocation",
        null=True,
        on_delete=models.CASCADE,
    )

    booth_start_date = models.DateField(
        default=get_default_start_date,
        blank=False,
        null=False,
    )
    booth_end_date = models.DateField(
        default=get_default_end_date,
        blank=False,
        null=False,
    )

    # Use a JSONField to store daily attributes
    booth_schedule: models.JSONField = models.JSONField(default=dict)

    objects: BoothScheduleManager = BoothScheduleManager()

    def save(self, *args, **kwargs):
        _logger.debug("Before save: %s", self.booth_schedule)

        # Ensure the JSONField has a default structure if it's empty
        if not self.booth_schedule:
            for day in DayOfWeek:
                self._reset_schedule_for_day_to_default(day.name.lower())

        super().save(*args, **kwargs)
        _logger.debug("After save: %s", self.booth_schedule)

    def get_schedule_for_day(self, day_of_week_string: str) -> dict:
        """
        Retrieve the value of a specific attribute for a given day.

        Args:
            day (str): The day for which to retrieve the attribute value.

        Returns:
            The value of the specified day's attributes.
        """
        attributes: dict = self.booth_schedule.get(day_of_week_string, {})
        _logger.debug("%s results in %s", day_of_week_string, attributes)
        if not attributes:
            attributes["open"] = False
            if day_of_week_string in GOLDEN_TICKET_LIST:
                attributes["golden_ticket"] = False

        attributes["open_time"] = parse_time(attributes.get("open_time"))
        attributes["close_time"] = parse_time(attributes.get("close_time"))
        return attributes

    def set_schedule_for_day(self, day_of_week_string: str, attribute: str, value: any) -> None:
        """
        Set the value of a specific attribute for a given day.

        Args:
            day (str): The day for which the attribute value is being set.
            attribute (str): The name of the attribute.
            value (any): The value to be set for the attribute.

        Returns:
            None
        """
        _logger.debug("Setting %s for %s to %s", attribute, day_of_week_string, value)
        if day_of_week_string not in self.booth_schedule:
            self.booth_schedule[day_of_week_string] = {}
        self.booth_schedule[day_of_week_string][attribute] = value
        if attribute == "open" and not value:
            self._reset_schedule_for_day_to_default(day_of_week_string)
        self.save()

    def update_booth_day_per_schedule(self):
        """
        Updates the booth days for the given booth location based on the schedule.

        The method relies on the following helper methods:
        - `_get_existing_booth_days`: Retrieves existing booth days from the database.
        - `_process_booth_days`: Processes the existing booth days to determine changes.
        - `_perform_bulk_operations`: Performs bulk operations to update the booth days and time
            blocks.
        """
        _logger.info("Updating booth days for %s", self.booth_location)
        _logger.info("=====================================")
        BoothDayApp = apps.get_model("cookie_booths", "BoothDay")
        BoothTimeBlockApp = apps.get_model("cookie_booths", "BoothTimeBlock")

        _logger.info("Getting existing booth days")
        existing_booth_days = self._get_existing_booth_days(BoothDayApp)

        _logger.info("Processing booth days")
        booth_day_changes = self._process_booth_days(existing_booth_days, BoothDayApp)

        _logger.info("Performing bulk operations")
        self._perform_bulk_operations(BoothDayApp, BoothTimeBlockApp, booth_day_changes)

    def _get_existing_booth_days(self, BoothDayApp: "BoothDay") -> dict:
        """
        Retrieve existing booth days for a given booth location and date range.

        Args:
            BoothDayApp (BoothDay): The BoothDay application model.

        Returns:
            dict: A dictionary containing existing booth days within the specified date range.
        """
        return BoothDayApp.objects.get_existing_booth_days_in_bulk(
            self.booth_location,
            self.booth_start_date,
            self.booth_end_date,
        )

    def _process_booth_days(self, existing_booth_days: dict, BoothDayApp: "BoothDay") -> dict:
        """
        Processes booth days within the specified date range and updates the booth schedule accordingly.
        Args:
            existing_booth_days (dict): A dictionary of existing booth days.
            BoothDayApp (BoothDay): The BoothDay application model.
        Returns:
            dict: A dictionary containing changes to booth days and time blocks with the following keys:
                - "new_booth_days": List of newly created booth days.
                - "updated_booth_days": List of updated booth days.
                - "new_time_blocks": List of newly created time blocks.
                - "time_blocks_to_delete": List of time blocks to be deleted.
        """
        new_booth_days = []
        updated_booth_days = []
        new_time_blocks = []
        time_blocks_to_delete = []

        for current_date in rrule(DAILY, dtstart=self.booth_start_date, until=self.booth_end_date):
            day = current_date.date()
            booth_schedule_for_day = self.get_schedule_for_day(day.strftime("%A").lower())

            booth_day = self._get_or_create_booth_day(
                existing_booth_days, day, BoothDayApp, new_booth_days, updated_booth_days
            )
            self._update_booth_day(booth_day, booth_schedule_for_day)

            time_block_changes = self._collect_time_blocks(booth_day, booth_schedule_for_day)
            new_time_blocks.extend(time_block_changes["new_time_blocks"])
            time_blocks_to_delete.extend(time_block_changes["time_blocks_to_delete"])

        booth_day_changes = {
            "new_booth_days": new_booth_days,
            "updated_booth_days": updated_booth_days,
            "new_time_blocks": new_time_blocks,
            "time_blocks_to_delete": time_blocks_to_delete,
        }
        _logger.debug("Booth day changes: %s", booth_day_changes)
        return booth_day_changes

    def _get_or_create_booth_day(
        self,
        existing_booth_days: dict,
        day: date,
        BoothDayApp: "BoothDay",
        new_booth_days: list,
        updated_booth_days: list,
    ) -> "BoothDay":
        """
        Retrieve an existing booth day or create a new one if it doesn't exist.

        Args:
            existing_booth_days (dict): A dictionary of existing booth days keyed by date.
            day (datetime.date): The date for which to get or create a booth day.
            BoothDayApp (class): The class used to create a new booth day instance.
            new_booth_days (list): A list to append newly created booth days.
            updated_booth_days (list): A list to append existing booth days that are retrieved.

        Returns:
            BoothDayApp: The booth day instance for the specified date.
        """
        booth_day = existing_booth_days.get(day)
        if booth_day is None:
            booth_day = BoothDayApp(
                booth_location=self.booth_location,
                booth_day_date=day,
            )
            new_booth_days.append(booth_day)
        else:
            updated_booth_days.append(booth_day)
        return booth_day

    def _update_booth_day(self, booth_day: "BoothDay", booth_schedule_for_day: dict) -> None:
        """
        Updates the attributes of a BoothDay instance based on the provided schedule for the day.

        Args:
            booth_day (BoothDay): The BoothDay instance to be updated.
            booth_schedule_for_day (dict): A dictionary containing the schedule information for the day.
                Expected keys:
                    - "open" (bool): Indicates if the booth is open for the day.
                    - "open_time" (str): The opening time of the booth.
                    - "close_time" (str): The closing time of the booth.
                    - "golden_ticket" (bool, optional): Indicates if the day is a golden ticket day.
                        Defaults to False.

        Returns:
            None
        """
        if not booth_schedule_for_day.get("open"):
            booth_day.booth_day_enabled = False
        else:
            booth_day.booth_day_open_time = booth_schedule_for_day.get("open_time")
            booth_day.booth_day_close_time = booth_schedule_for_day.get("close_time")
            booth_day.booth_day_is_golden = booth_schedule_for_day.get("golden_ticket", False)
            booth_day.booth_day_enabled = True

    def _perform_bulk_operations(
        self, BoothDayApp: "BoothDay", BoothTimeBlockApp: "BoothTimeBlock", booth_day_changes: dict
    ) -> None:
        """
        Perform bulk operations on booth days and time blocks.
        This method handles the creation, updating, and deletion of booth days and time blocks
        in a single atomic transaction.
        Args:
            BoothDayApp (BoothDay): The BoothDay model class.
            BoothTimeBlockApp (BoothTimeBlock): The BoothTimeBlock model class.
            booth_day_changes (dict): A dictionary containing the changes to be applied. The dictionary
                should have the following keys:
                - "new_booth_days": A list of new BoothDay instances to be created.
                - "updated_booth_days": A list of BoothDay instances to be updated.
                - "new_time_blocks": A list of new BoothTimeBlock instances to be created.
                - "time_blocks_to_delete": A list of BoothTimeBlock instances to be deleted.
        Returns:
            None
        """
        new_booth_days = booth_day_changes.get("new_booth_days")
        updated_booth_days = booth_day_changes.get("updated_booth_days")
        new_time_blocks = booth_day_changes.get("new_time_blocks")
        time_blocks_to_delete = booth_day_changes.get("time_blocks_to_delete")

        with transaction.atomic():
            if new_booth_days:
                BoothDayApp.objects.bulk_create(new_booth_days)
            if updated_booth_days:
                BoothDayApp.objects.bulk_update(
                    updated_booth_days,
                    [
                        "booth_day_open_time",
                        "booth_day_close_time",
                        "booth_day_is_golden",
                        "booth_day_enabled",
                    ],
                )
            if new_time_blocks:
                BoothTimeBlockApp.objects.bulk_create(new_time_blocks)
            if time_blocks_to_delete:
                BoothTimeBlockApp.objects.delete_blocks(time_blocks_to_delete)

    def _collect_time_blocks(self, booth_day: "BoothDay", booth_schedule_for_day: dict) -> dict:
        """
        Collect BoothTimeBlocks for the given BoothDay.
        """
        BoothTimeBlockApp: "BoothTimeBlock" = apps.get_model("cookie_booths", "BoothTimeBlock")
        open_time = booth_schedule_for_day.get("open_time")
        close_time = booth_schedule_for_day.get("close_time")

        # Ensure open_time and close_time are datetime objects
        open_time, close_time = self._ensure_datetime(booth_day, open_time, close_time)

        # Collect IDs of old time blocks that are completely outside the new time range
        time_blocks_to_delete = self._collect_time_blocks_to_delete(
            BoothTimeBlockApp, booth_day, open_time, close_time
        )

        # Calculate the number of 2-hour blocks
        num_blocks = self._calculate_num_blocks(open_time, close_time)

        # Create a list to hold the new time blocks
        new_time_blocks = self._create_new_time_blocks(
            BoothTimeBlockApp, booth_day, open_time, num_blocks
        )

        block_changes = {
            "new_time_blocks": new_time_blocks,
            "time_blocks_to_delete": time_blocks_to_delete,
        }
        return block_changes

    def _ensure_datetime(self, booth_day: "BoothDay", open_time: time, close_time: time) -> tuple:
        """
        Ensure open_time and close_time are datetime objects.
        """
        if isinstance(open_time, time):
            open_time = datetime.combine(booth_day.booth_day_date, open_time)
        if isinstance(close_time, time):
            close_time = datetime.combine(booth_day.booth_day_date, close_time)
        return open_time, close_time

    def _collect_time_blocks_to_delete(
        self,
        BoothTimeBlockApp: "BoothTimeBlock",
        booth_day: "BoothDay",
        open_time: datetime,
        close_time: datetime,
    ) -> list:
        """
        Collect IDs of old time blocks that are completely outside the new time range.
        """
        time_blocks_to_delete = list(
            BoothTimeBlockApp.objects.get_blocks_outside_start_time(
                booth_day=booth_day,
                open_time=open_time,
            )
        )
        time_blocks_to_delete.extend(
            BoothTimeBlockApp.objects.get_blocks_outside_end_time(
                booth_day=booth_day,
                close_time=close_time,
            )
        )

        # Collect IDs of overlapping blocks
        overlapping_blocks = BoothTimeBlockApp.objects.get_blocks_overlapping(
            booth_day=booth_day,
            open_time=open_time,
            close_time=close_time,
        )
        time_blocks_to_delete.extend(overlapping_blocks)

        return time_blocks_to_delete

    def _calculate_num_blocks(self, open_time: datetime, close_time: datetime) -> int:
        """
        Calculate the number of 2-hour blocks.
        """
        return (close_time - open_time).seconds // TIME_BLOCK_IN_SECONDS

    def _create_new_time_blocks(
        self, BoothTimeBlockApp, booth_day: "BoothDay", open_time: datetime, num_blocks: int
    ) -> list:
        """
        Create a list to hold the new time blocks.
        """
        new_time_blocks = []

        for i in range(num_blocks):
            start_time = open_time + timedelta(hours=TIME_BLOCK_IN_HOURS * i)
            end_time = start_time + timedelta(hours=TIME_BLOCK_IN_HOURS)

            # Create new time block instances
            new_time_blocks.append(
                BoothTimeBlockApp(
                    booth_day=booth_day,
                    booth_block_start_time=start_time,
                    booth_block_end_time=end_time,
                    booth_block_enabled=True,
                    booth_block_freeforall_enabled=False,
                )
            )

        return new_time_blocks

    def _reset_schedule_for_day_to_default(self, day_of_week_string: str) -> None:
        """
        Reset the daily attributes for a given day to the default values.

        Args:
            day (str): The day for which the attributes are being reset.

        Returns:
            None
        """
        self.booth_schedule[day_of_week_string] = {
            "open": False,
            "open_time": None,
            "close_time": None,
        }

        if day_of_week_string in GOLDEN_TICKET_LIST:
            self.booth_schedule[day_of_week_string]["golden_ticket"] = False

    def set_schedule(self, booth_schedule: dict) -> None:
        """
        Set the daily attributes for the booth.

        Args:
            daily_attributes (dict): The daily attributes to set.

        Returns:
            None
        """
        _logger.debug("Setting schedule to %s", booth_schedule)
        self.booth_schedule = booth_schedule
        self.save()
