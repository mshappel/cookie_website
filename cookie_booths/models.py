from datetime import timedelta, datetime
from pytz import utc

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


class BoothLocation(models.Model):
    """Contains data relevant for booths"""

    # ID is referenced via Django object ID
    booth_location = models.CharField(max_length=300)
    booth_address = models.CharField(max_length=300)

    booth_enabled = models.BooleanField(default=False)

    booth_block_level_restrictions_start = models.SmallIntegerField(
        choices=settings.GIRL_SCOUT_TROOP_LEVELS_WITH_NONE, default=0
    )
    booth_block_level_restrictions_end = models.SmallIntegerField(
        choices=settings.GIRL_SCOUT_TROOP_LEVELS_WITH_NONE, default=0
    )

    booth_requires_masks = models.BooleanField(default=False)
    booth_is_outside = models.BooleanField(default=False)

    booth_notes = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = "booth locations"
        verbose_name = "booth location"

    def __str__(self):
        return self.booth_location

    def update_hours(self):
        # We need to create or delete booth days, or update their hours, based on new hours, and
        # we have a few steps for this
        hours = BoothHours.objects.get(booth_location=self)

        # If no date is set for either start or end date, delete all days owned by this booth
        if hours.booth_start_date is None or hours.booth_end_date is None:
            BoothDay.objects.filter(booth=self).delete()
            return

        # Delete any days outside of the new start/end date - this will cascade down to the blocks
        BoothDay.objects.filter(
            Q(booth=self),
            Q(booth_day_date__lt=hours.booth_start_date)
            | Q(booth_day_date__gt=hours.booth_end_date),
        ).delete()

        # Go through each day between the new start and end date
        for date in self.__daterange(hours.booth_start_date, hours.booth_end_date):
            # Figure out what day of the week it is, and either:
            # 1. If we're closed that day, delete a day if it's present
            if (
                ((date.weekday() == 0) and (not hours.monday_open))
                or ((date.weekday() == 1) and (not hours.tuesday_open))
                or ((date.weekday() == 2) and (not hours.wednesday_open))
                or ((date.weekday() == 3) and (not hours.thursday_open))
                or ((date.weekday() == 4) and (not hours.friday_open))
                or ((date.weekday() == 5) and (not hours.saturday_open))
                or ((date.weekday() == 6) and (not hours.sunday_open))
            ):
                BoothDay.objects.filter(booth=self, booth_day_date=date).delete()
            # 2. If we're open, add or update those hours
            else:
                if date.weekday() == 0:  # Monday
                    self.add_or_update_day(
                        date,
                        datetime.combine(date, hours.monday_open_time, tzinfo=utc),
                        datetime.combine(date, hours.monday_close_time, tzinfo=utc),
                    )
                    self.update_golden_day(date, hours.monday_golden_ticket)
                elif date.weekday() == 1:  # Tuesday
                    self.add_or_update_day(
                        date,
                        datetime.combine(date, hours.tuesday_open_time, tzinfo=utc),
                        datetime.combine(date, hours.tuesday_close_time, tzinfo=utc),
                    )
                    self.update_golden_day(date, hours.tuesday_golden_ticket)
                elif date.weekday() == 2:  # Wednesday
                    self.add_or_update_day(
                        date,
                        datetime.combine(date, hours.wednesday_open_time, tzinfo=utc),
                        datetime.combine(date, hours.wednesday_close_time, tzinfo=utc),
                    )
                    self.update_golden_day(date, hours.wednesday_golden_ticket)
                elif date.weekday() == 3:  # Thursday
                    self.add_or_update_day(
                        date,
                        datetime.combine(date, hours.thursday_open_time, tzinfo=utc),
                        datetime.combine(date, hours.thursday_close_time, tzinfo=utc),
                    )
                    self.update_golden_day(date, hours.thursday_golden_ticket)
                elif date.weekday() == 4:  # Friday
                    self.add_or_update_day(
                        date,
                        datetime.combine(date, hours.friday_open_time, tzinfo=utc),
                        datetime.combine(date, hours.friday_close_time, tzinfo=utc),
                    )
                    self.update_golden_day(date, hours.friday_golden_ticket)
                elif date.weekday() == 5:  # Saturday
                    self.add_or_update_day(
                        date,
                        datetime.combine(date, hours.saturday_open_time, tzinfo=utc),
                        datetime.combine(date, hours.saturday_close_time, tzinfo=utc),
                    )
                    self.update_golden_day(date, hours.saturday_golden_ticket)
                else:  # Sunday
                    self.add_or_update_day(
                        date,
                        datetime.combine(date, hours.sunday_open_time, tzinfo=utc),
                        datetime.combine(date, hours.sunday_close_time, tzinfo=utc),
                    )
                    self.update_golden_day(date, hours.sunday_golden_ticket)

        return

    def update_booth(self):
        hours = BoothHours.objects.get(booth_location=self)
        for date in self.__daterange(hours.booth_start_date, hours.booth_end_date):
            if (
                ((date.weekday() == 0) and hours.monday_open)
                or ((date.weekday() == 1) and hours.tuesday_open)
                or ((date.weekday() == 2) and hours.wednesday_open)
                or ((date.weekday() == 3) and hours.thursday_open)
                or ((date.weekday() == 4) and hours.friday_open)
                or ((date.weekday() == 5) and hours.saturday_open)
                or ((date.weekday() == 6) and hours.sunday_open)
            ):
                booth_day = self.__booth_day_exist(date)
                if self.booth_enabled:
                    booth_day.enable_day()
                else:
                    booth_day.disable_day()

        return

    def add_or_update_day(self, date, open_time, close_time):
        # First see if we have a Booth_Day existing for that date. If so, grab it and update the open/close time
        booth_day = self.__booth_day_exist(date=date)

        # Set the hours
        booth_day.add_or_update_hours(open_time, close_time)
        booth_day.save()

        return

    def update_golden_day(self, date, is_golden_booth):
        # First see if we have a Booth_Day existing for that date. If so, grab it and update the open/close time
        booth_day = self.__booth_day_exist(date=date)

        # Set the golden ticket
        booth_day.change_golden_status(is_golden_booth=is_golden_booth)
        booth_day.save()

        return

    def __daterange(self, start_date, end_date):
        # Need +1 to be inclusive of the end date
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)

    def __booth_day_exist(self, date):
        try:
            booth_day = BoothDay.objects.get(booth=self, booth_day_date=date)

        except BoothDay.DoesNotExist:
            # If it doesn't exist yet, create it
            booth_day = BoothDay.objects.create(
                booth=self,
                booth_day_date=date,
                booth_day_enabled=False,
                booth_day_hours_set=False,
            )

        return booth_day


class BoothHours(models.Model):
    booth_location = models.OneToOneField(
        BoothLocation, null=True, on_delete=models.CASCADE
    )

    booth_start_date = models.DateField(blank=True, null=True)
    booth_end_date = models.DateField(blank=True, null=True)

    sunday_open = models.BooleanField(default=False)
    sunday_golden_ticket = models.BooleanField(default=False)
    sunday_open_time = models.TimeField(blank=True, null=True)
    sunday_close_time = models.TimeField(blank=True, null=True)

    monday_open = models.BooleanField(default=False)
    monday_golden_ticket = models.BooleanField(default=False)
    monday_open_time = models.TimeField(blank=True, null=True)
    monday_close_time = models.TimeField(blank=True, null=True)

    tuesday_open = models.BooleanField(default=False)
    tuesday_golden_ticket = models.BooleanField(default=False)
    tuesday_open_time = models.TimeField(blank=True, null=True)
    tuesday_close_time = models.TimeField(blank=True, null=True)

    wednesday_open = models.BooleanField(default=False)
    wednesday_golden_ticket = models.BooleanField(default=False)
    wednesday_open_time = models.TimeField(blank=True, null=True)
    wednesday_close_time = models.TimeField(blank=True, null=True)

    thursday_open = models.BooleanField(default=False)
    thursday_golden_ticket = models.BooleanField(default=False)
    thursday_open_time = models.TimeField(blank=True, null=True)
    thursday_close_time = models.TimeField(blank=True, null=True)

    friday_open = models.BooleanField(default=False)
    friday_golden_ticket = models.BooleanField(default=False)
    friday_open_time = models.TimeField(blank=True, null=True)
    friday_close_time = models.TimeField(blank=True, null=True)

    saturday_open = models.BooleanField(default=False)
    saturday_golden_ticket = models.BooleanField(default=False)
    saturday_open_time = models.TimeField(blank=True, null=True)
    saturday_close_time = models.TimeField(blank=True, null=True)


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

    class Meta:
        permissions = (
            ("toggle_day", "Enable/Disable a day for a booth"),
            ("add_or_update_hours", "Add or update hours for a booth day"),
            ("make_golden_booth", "Make a booth day golden"),
            ("toggle_freeforall", "Enable/Disable free for all"),
        )

    def enable_day(self):
        # If we're already enabled, nothing to do
        if self.booth_day_enabled:
            return

        self.booth_day_enabled = True

        for block in BoothBlock.objects.filter(booth_day__id=self.id):
            block.enable_block()

        self.save()

        return

    def disable_day(self):
        # If we're already disabled, nothing to do
        if not self.booth_day_enabled:
            return

        self.booth_day_enabled = False

        for block in BoothBlock.objects.filter(booth_day__id=self.id):
            block.disable_block()

        self.save()

        return

    def add_or_update_hours(self, open_time, close_time):
        # There are two main cases we need to handle here:
        # If hours have been previously set, or if they haven't

        # Case 1 - Hours have been set
        if self.booth_day_hours_set is True:
            # Easy escape clause - if we've already set hours,
            # And they match what is here, then we have nothing to change
            if (
                open_time is self.booth_day_open_time
                and close_time is self.booth_day_close_time
            ):
                return

            # So the hours differ, we need to handle this from both ends

            # A few easy operations - Blocks that start before the new open time
            # or end after the new close time should be cleared
            BoothBlock.objects.filter(
                Q(booth_day__id=self.id),
                Q(booth_block_start_time__lt=open_time)
                | Q(booth_block_end_time__gt=close_time),
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

        return

    def enable_freeforall(self):
        # If we're already enabled, nothing to do
        if self.booth_day_freeforall_enabled:
            return

        for block in BoothBlock.objects.filter(booth_day__id=self.id):
            block.booth_block_freeforall_enabled = True
            block.save()

        self.booth_day_freeforall_enabled = True
        self.save()

    def disable_freeforall(self):
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


class BoothBlock(models.Model):
    """Contains information for a particular booth block"""

    booth_day = models.ForeignKey(BoothDay, on_delete=models.CASCADE)

    booth_block_start_time = models.DateTimeField(blank=True, null=True)
    booth_block_end_time = models.DateTimeField(blank=True, null=True)

    booth_block_held_for_cookie_captains = models.BooleanField(default=False)

    booth_block_current_troop_owner = models.IntegerField(default=0)
    booth_block_current_cookie_captain_owner = models.IntegerField(default=0)
    booth_block_reserved = models.BooleanField(default=False)

    booth_block_enabled = models.BooleanField(default=False)
    booth_block_freeforall_enabled = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("block_reservation", "Reserve/Cancel a booth"),
            ("reserve_block", "Reserve a booth"),
            ("cookie_captain_reserve_block", "Reserve a block for a daisy scout"),
            (
                "block_reservation_admin",
                "Administrator reserve/cancel any booth, or hold booths for cookie captains to reserve",
            ),
        )

    def cancel_block(self):
        # If this block is not enabled, no reservation can be made
        if not self.booth_block_enabled:
            return False

        # If this block is not reserved, we cannot cancel the block
        if self.booth_block_reserved:
            pass
        else:
            return False

        # At this point we can cancel the reservation
        self.booth_block_reserved = False
        self.booth_block_current_troop_owner = 0
        self.booth_block_current_cookie_captain_owner = 0

        # TODO: Send email confirmation

        self.save()

        return True

    def reserve_block(self, troop_id, cookie_cap_id):
        # If this block is not enabled, no reservation can be made
        if not self.booth_block_enabled:
            return False

        # If this block is already reserved, we cannot reserve it.
        if self.booth_block_reserved:
            return False

        # At this point we're good to go reserving it.
        self.booth_block_reserved = True
        self.booth_block_current_troop_owner = troop_id
        self.booth_block_current_cookie_captain_owner = cookie_cap_id

        # TODO: Send email confirmation

        self.save()
        return True

    def hold_for_cookie_captains(self):
        # If already held, return
        if self.booth_block_held_for_cookie_captains:
            return True

        # If this block is already reserved, we can't hold it
        if self.booth_block_reserved:
            return False

        self.booth_block_held_for_cookie_captains = True
        self.save()

        return True

    def unhold_for_cookie_captains(self):
        # If already unheld, return
        if not self.booth_block_held_for_cookie_captains:
            return True

        # If reserved, we should also unreserve the block
        self.cancel_block()

        self.booth_block_held_for_cookie_captains = False
        self.save()

        return True

    def enable_block(self):
        # If this block is enabled return
        if self.booth_block_enabled:
            return True

        self.booth_block_enabled = True
        self.save()

        return True

    def disable_block(self):
        # If this block is already disabled return
        if self.booth_block_enabled:
            self.booth_block_enabled = False
            self.save()

        return True


@receiver(post_save, sender=BoothHours)
def update_booth_location(sender, instance, created, **kwargs):
    # We don't care if it was just created - only on updates that actually set real hours
    if not created:
        instance.booth_location.update_hours()
        instance.booth_location.update_booth()


@receiver(post_save, sender=BoothLocation)
def generate_hours_if_needed(sender, instance, created, **kwargs):
    if created:
        BoothHours.objects.create(booth_location=instance)
    else:
        instance.update_booth()


# TODO: This is broken and our testing does not cover this
@receiver(pre_delete, sender=BoothBlock)
def notify_block_deletion(sender, instance, **kwargs):
    # If this block has been reserved, notify the owner. Otherwise we have nothing to do
    if not instance.booth_block_reserved:
        return

    # Get the troop
    reserved_troop = Troop.objects.get(
        troop_number=instance.booth_block_current_troop_owner
    )
    if not reserved_troop:
        return

    # Then the owner from that
    block_owner = User.objects.get(username=reserved_troop.troop_cookie_coordinator)
    if not block_owner:
        return

    title = "Your Reserved Booth Block Has Been Removed"
    message = (
        "Hello "
        + block_owner.first_name
        + ",\n"
        + "Due to a schedule change, the following block is no longer available for reservation:\n\n"
        + "Location: "
        + instance.booth_day.booth.booth_location
        + "\n"
        + "Address: "
        + instance.booth_day.booth.booth_address
        + "\n"
        + "Date: "
        + instance.booth_day.booth_day_date.strftime("%A, %B %d, %Y")
        + "\n"
        + "Time Block: "
        + instance.booth_block_start_time.strftime("%I:%M %p")
        + " - "
        + instance.booth_block_end_time.strftime("%I:%M %p")
        + "\n\n\n"
        + "NOTE: Please do not reply to this email directly, this email address is not monitored. Please reach out to an administrator with any further questions."
    )

    send_mail(
        title,
        message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[block_owner.email],
    )

    return
