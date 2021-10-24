from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone

MIN_BOOTH_BLOCK_HOURS = 2

class Booth_Location(models.Model):
    """Contains data relevant for booths"""
    # ID is referenced via Django object ID
    booth_location = models.CharField(max_length=300)
    booth_address = models.CharField(max_length=300)

    booth_enabled = models.BooleanField(default=False)

    booth_is_golden_ticket = models.BooleanField(default=False)
    booth_requires_masks = models.BooleanField(default=False)
    booth_is_outside = models.BooleanField(default=False)

    booth_notes = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "booth locations"
        verbose_name = "booth location"

    def __str__(self):
        return self.booth_location

    def add_or_update_day(self, date, open_time, close_time):
        # First see if we have a Booth_Day existing for that date. If so, grab it and update the open/close time
        booth_day = None
        try:
            booth_day = Booth_Day.objects.get(booth_day_date=date)
        except Booth_Day.DoesNotExist:
            # If it doesn't exist yet, create it
            booth_day = Booth_Day.objects.create(booth=self, \
                                                 booth_day_date=date, \
                                                 booth_day_enabled=False, \
                                                 booth_day_hours_set=False)

        # Set the hours
        booth_day.add_or_update_hours(open_time, close_time)
        booth_day.save()

        return


class Booth_Day(models.Model):
    """Contains data relevant for a day of a booth"""
    booth = models.ForeignKey(Booth_Location, on_delete=models.CASCADE)

    booth_day_date = models.DateField(blank=True, null=True)

    booth_day_hours_set = models.BooleanField(default=False)
    booth_day_open_time = models.DateTimeField(blank=True, null=True)
    booth_day_close_time = models.DateTimeField(blank=True, null=True)

    booth_day_enabled = models.BooleanField(default=False)

    def enable_day(self):
        # If we're already enabled, nothing to do
        if booth_day_enabled:
            return

        booth_day_enabled = true

        for block in Booth_Block.objects.filter(booth_day__id=self.id):
            block.booth_block_enabled = true

    def disable_day(self):
        # If we're already disabled, nothing to do
        if not booth_day_enabled:
            return

        booth_day_enabled = False

        for block in Booth_Block.objects.filter(booth_day__id=self.id):
            block.booth_block_enabled = false


    def add_or_update_hours(self, open_time, close_time):
        # TODO: Enforce permission
        # There are two main cases we need to handle here:
        # If hours have been previously set, or if they haven't

        # Case 1 - Hours have been set
        if self.booth_day_hours_set is True:
            # Easy escape clause - if we've already set hours,
            # And they match what is here, then we have nothing to change
            if open_time is self.booth_day_open_time and \
                close_time is self.booth_day_close_time:
                return

            # So the hours differ, we need to handle this from both ends

            # A few easy operations - Blocks that start before the new open time
            # or end after the new close time should be cleared
            Booth_Block.objects.filter(Q(booth_day__id=self.id),
                                       Q(booth_block_start_time__lt=open_time) | Q(booth_block_end_time__gt=close_time)).delete()

            if not Booth_Block.objects.filter(booth_day__id=self.id):
                self.booth_day_hours_set = False
            else:
                # We should now have a pruned list based on our new open/close times.
                # Now we need to do the following:
                # 1. If the new open time is before our previous one, see if we need to add new blocks on the front end
                first_block = Booth_Block.objects.filter(booth_day__id=self.id).earliest('booth_block_start_time')

                start_end = (first_block.booth_block_start_time.replace(hour=first_block.booth_block_start_time.hour - 2), first_block.booth_block_start_time, True)
                while start_end[0].hour >= open_time.hour and start_end[2]:
                    start_end = self.__add_block_backwards(start_end)

                # 2. If the new close time is after our previous one, see if we need to add new blocks on the back end
                last_block = Booth_Block.objects.filter(booth_day__id=self.id).latest('booth_block_end_time')

                start_end = (last_block.booth_block_end_time, last_block.booth_block_end_time.replace(hour=last_block.booth_block_end_time.hour + 2), True)
                while start_end[1].hour <= close_time.hour and start_end[2]:
                    start_end = self.__add_block_forwards(start_end)

        # If, after our pruning, we end up with an empty list, we can just generate a new one based on time
        if not self.booth_day_hours_set:
            start_end = (open_time, open_time.replace(hour=open_time.hour+2), True)

            while start_end[1].hour <= close_time.hour and start_end[2]:
                start_end = self.__add_block_forwards(start_end)

        self.booth_day_hours_set = True
        self.booth_day_open_time = open_time
        self.booth_day_close_time = close_time

        return

    # Add block forward in time
    def __add_block_forwards(self, start_end):
        # Create a new block
        booth_block = Booth_Block.objects.create(booth_day=self, \
                                                 booth_block_start_time=start_end[0], \
                                                 booth_block_end_time=start_end[1], \
                                                 booth_block_reserved=False, \
                                                 booth_block_enabled=self.booth_day_enabled)

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

        return start_end[0].replace(hour=new_start_time), start_end[1].replace(hour=new_end_time), cont

    # Add block backward in time
    def __add_block_backwards(self, start_end):
        # Create a new block
        booth_block = Booth_Block.objects.create(booth_day=self, \
                                                 booth_block_start_time=start_end[0], \
                                                 booth_block_end_time=start_end[1], \
                                                 booth_block_reserved=False, \
                                                 booth_block_enabled=self.booth_day_enabled)

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

        return start_end[0].replace(hour=new_start_time), start_end[1].replace(hour=new_end_time), cont


class Booth_Block(models.Model):
    """Contains information for a particular booth block"""
    booth_day = models.ForeignKey(Booth_Day, on_delete=models.CASCADE)

    booth_block_start_time = models.DateTimeField(blank=True, null=True)
    booth_block_end_time = models.DateTimeField(blank=True, null=True)

    booth_block_current_troop_owner = models.SmallIntegerField(default=0)
    booth_block_reserved = models.BooleanField(default=False)

    booth_block_enabled = models.BooleanField(default=False)

    def cancel_block(self, troop_id):
        # TODO: Need to Enforce permissions to allow canceling only if the calling user either
        # 1. Is associated with the troop currently reserving this block, in which case they can do this
        # 2. Has a superuser permission and can cancel any block here
        return

    def reserve_block(self, troop_id):
        # If this block is not enabled, no reservation can be made
        if not self.booth_block_enabled:
            return False

        # If this block is already reserved, we cannot reserve it.
        if self.booth_block_reserved:
            return False

        # At this point we're good to go reserving it.
        self.booth_block_reserved = True
        self.booth_block_current_troop_owner = troop_id

        # TODO: Send email confirmation?

        return True


@receiver(pre_delete, sender=Booth_Block)
def notify_block_deletion(sender, instance, **kwargs):
    # TODO: email owner
    return
