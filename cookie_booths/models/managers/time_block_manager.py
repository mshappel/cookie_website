from datetime import date, datetime

from django.db import models
from django.db.models import QuerySet


class BoothTimeBlockManager(models.Manager):
    def delete_blocks(self, block_ids):
        return self.filter(id__in=block_ids).delete()

    def get_blocks_outside_start_time(self, booth_day: date, open_time: datetime) -> QuerySet:
        """
        Retrieve the IDs of time blocks that start before a given open time on a specific booth day.

        Args:
            booth_day (datetime.date): The specific day for the booth.
            open_time (datetime.datetime): The opening time to compare against.

        Returns:
            QuerySet: A QuerySet containing the IDs of time blocks that start before the given
                open time.
        """
        outside_start_time = self.filter(
            booth_day=booth_day,
            booth_block_start_time__lt=open_time,
        ).values_list("id", flat=True)
        return outside_start_time

    def get_blocks_outside_end_time(self, booth_day: date, close_time: datetime) -> QuerySet:
        """
        Retrieve the IDs of time blocks that end after a specified close time for a given booth day.

        Args:
            booth_day (datetime.date): The specific day for which to retrieve time blocks.
            close_time (datetime.datetime): The close time to compare against the end times of the
                time blocks.

        Returns:
            QuerySet: A QuerySet containing the IDs of the time blocks that end after the specified
                close time.
        """
        outside_end_time = self.filter(
            booth_day=booth_day,
            booth_block_end_time__gt=close_time,
        ).values_list("id", flat=True)
        return outside_end_time

    def get_blocks_overlapping(
        self, booth_day: date, open_time: datetime, close_time: datetime
    ) -> QuerySet:
        """
        Retrieve the IDs of time blocks that overlap with a given time range on a specific
            booth day.

        Args:
            booth_day (datetime.date): The specific day for which to find overlapping time blocks.
            open_time (datetime.datetime): The start time of the range to check for overlaps.
            close_time (datetime.datetime): The end time of the range to check for overlaps.

        Returns:
            QuerySet: A QuerySet containing the IDs of the overlapping time blocks.
        """
        overlapping_blocks = self.filter(
            booth_day=booth_day,
            booth_block_start_time__lt=close_time,
            booth_block_end_time__gt=open_time,
        ).values_list("id", flat=True)
        return overlapping_blocks
