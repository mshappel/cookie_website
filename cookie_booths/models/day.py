from datetime import timedelta

from django.db import models
from django.db.models import Q

from cookie_booths.models.helpers import _get_booth_block_model
from cookie_booths.models.location import BoothLocation
from cookie_booths.models.managers.days_manager import BoothDayManager


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
        permissions = (
            ("toggle_day", "Enable/Disable a day for a booth"),
            ("add_or_update_hours", "Add or update hours for a booth day"),
            ("make_golden_booth", "Make a booth day golden"),
            ("toggle_freeforall", "Enable/Disable free for all"),
        )

    def __str__(self):
        # More useful name in the admin site
        return f"{self.booth} on {self.booth_day_date}"

    def enable_day(self):
        BoothBlock = _get_booth_block_model()

        # If we're already enabled, nothing to do
        if self.booth_day_enabled:
            return

        self.booth_day_enabled = True

        for block in BoothBlock.objects.filter(booth_day__id=self.id):
            block.enable_block()

        self.save()

        return

    def disable_day(self):
        BoothBlock = _get_booth_block_model()
        # If we're already disabled, nothing to do
        if not self.booth_day_enabled:
            return

        self.booth_day_enabled = False

        for block in BoothBlock.objects.filter(booth_day__id=self.id):
            block.disable_block()

        self.save()

        return

    def add_or_update_hours(self, open_time, close_time):
        BoothBlock = _get_booth_block_model()
        # There are two main cases we need to handle here:
        # If hours have been previously set, or if they haven't

        # Case 1 - Hours have been set
        if self.booth_day_hours_set is True:
            # Easy escape clause - if we've already set hours,
            # And they match what is here, then we have nothing to change
            if open_time is self.booth_day_open_time and close_time is self.booth_day_close_time:
                return

            # So the hours differ, we need to handle this from both ends

            # A few easy operations - Blocks that start before the new open time
            # or end after the new close time should be cleared
            BoothBlock.objects.filter(
                Q(booth_day__id=self.id),
                Q(booth_block_start_time__lt=open_time) | Q(booth_block_end_time__gt=close_time),
            ).delete()

            if not BoothBlock.objects.filter(booth_day__id=self.id):
                self.booth_day_hours_set = False
            else:
                # We should now have a pruned list based on our new open/close times.
                # Now we need to do the following:
                # 1. If the new open time is before our previous one, see if we need to add new blocks on the front end
                first_block = BoothBlock.objects.filter(booth_day__id=self.id).earliest(
                    "booth_block_start_time"
                )

                start_end = (
                    first_block.booth_block_start_time - timedelta(hours=2),
                    first_block.booth_block_start_time,
                    True,
                )
                while start_end[0].hour >= open_time.hour and start_end[2]:

                    start_end = self.__add_block_backwards(start_end)

                # 2. If the new close time is after our previous one, see if we need to add new blocks on the back end
                last_block = BoothBlock.objects.filter(booth_day__id=self.id).latest(
                    "booth_block_end_time"
                )

                start_end = (
                    last_block.booth_block_end_time,
                    last_block.booth_block_end_time + timedelta(hours=2),
                    True,
                )
                while start_end[1].hour <= close_time.hour and start_end[2]:
                    start_end = self.__add_block_forwards(start_end)

        # If, after our pruning, we end up with an empty list, we can just generate a new one based on time
        if not self.booth_day_hours_set:
            start_end = (open_time, open_time + timedelta(hours=2), True)

            while start_end[1].hour <= close_time.hour and start_end[2]:
                start_end = self.__add_block_forwards(start_end)

        self.booth_day_hours_set = True
        self.booth_day_open_time = open_time
        self.booth_day_close_time = close_time

        return

    def change_golden_status(self, is_golden_booth):
        self.booth_day_is_golden = is_golden_booth
        self.save()

        return

    def enable_freeforall(self):
        BoothBlock = _get_booth_block_model()
        # If we're already enabled, nothing to do
        if self.booth_day_freeforall_enabled:
            return

        for block in BoothBlock.objects.filter(booth_day__id=self.id):
            block.booth_block_freeforall_enabled = True
            block.save()

        self.booth_day_freeforall_enabled = True
        self.save()

    def disable_freeforall(self):
        BoothBlock = _get_booth_block_model()
        # If we're already disabled, nothing to do
        if not self.booth_day_freeforall_enabled:
            return

        self.booth_day_freeforall_enabled = False

        for block in BoothBlock.objects.filter(booth_day__id=self.id):
            block.booth_block_freeforall_enabled = False
            block.save()

        self.save()

    # Add block forward in time
    def __add_block_forwards(self, start_end):
        BoothBlock = _get_booth_block_model()
        # Create a new block
        BoothBlock.objects.create(
            booth_day=self,
            booth_block_start_time=start_end[0],
            booth_block_end_time=start_end[1],
            booth_block_reserved=False,
            booth_block_enabled=self.booth_day_enabled,
        )

        cont = True
        # Shift hours forward, if we can
        new_start_time = start_end[0].hour + 2
        if new_start_time > 23:
            new_start_time = 23
            cont = False

        new_end_time = start_end[1].hour + 2
        if new_end_time > 23:
            new_end_time = 23
            cont = False

        # If we hit the end of the day and there isn't enough time to add a block, we can bail on block creation
        if new_end_time - new_start_time != 2:
            cont = False

        return (
            start_end[0].replace(hour=new_start_time),
            start_end[1].replace(hour=new_end_time),
            cont,
        )

    # Add block backward in time
    def __add_block_backwards(self, start_end):
        BoothBlock = _get_booth_block_model()
        # Create a new block
        BoothBlock.objects.create(
            booth_day=self,
            booth_block_start_time=start_end[0],
            booth_block_end_time=start_end[1],
            booth_block_reserved=False,
            booth_block_enabled=self.booth_day_enabled,
        )

        cont = True
        # Shift hours backward
        new_start_time = start_end[0].hour - 2
        if new_start_time < 0:
            new_start_time = 0
            cont = False

        new_end_time = start_end[1].hour - 2
        if new_end_time < 0:
            new_end_time = 0
            cont = False

        # If we hit the beginning of the day and there isn't enough time to add a block, we can bail on block creation
        if new_end_time - new_start_time != 2:
            cont = False

        return (
            start_end[0].replace(hour=new_start_time),
            start_end[1].replace(hour=new_end_time),
            cont,
        )
