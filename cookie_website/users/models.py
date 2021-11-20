from django.contrib.auth.models import AbstractUser, User, Group
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from cookie_booths.models import BoothDay, BoothBlock


class TroopTicketParameters:
    normal_troop_total_tickets_per_week = 5
    normal_troop_golden_tickets_per_week = 1

    super_troop_total_tickets_per_week = 10
    super_troop_golden_tickets_per_week = 2


# User-related Models
class User(AbstractUser):
    pass

    @property
    def full_name(self):
        """Returns the person's full name"""
        return '%s %s' % (self.first_name, self.last_name)


class Troop(models.Model):
    troop_number = models.PositiveSmallIntegerField(unique=True)

    troop_cookie_coordinator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    super_troop = models.BooleanField(default=False)
    daisy_troop = models.BooleanField(default=False)

    total_booth_tickets_per_week = models.PositiveSmallIntegerField(default=0)
    booth_golden_tickets_per_week = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return 'Troop ' + str(self.troop_number)

    def get_num_tickets_remaining(self, start_date, end_date):
        # A couple of preconditions:
        # start_date should be BEFORE end_date
        if start_date > end_date:
            return (0, 0)

        # start_date should be a Monday, end_date should be a Sunday
        if start_date.weekday() != 0 and end_date.weekday() != 6:
            return (0, 0)

        # They should be 6 days apart, so representing a week period inclusive
        delta = end_date - start_date
        if delta.days != 6:
            return (0, 0)

        # OK, we're good to check vs actual data now
        total_booth_count = 0
        super_booth_count = 0
        # We're filtering by Blocks that are owned by this troop, and are associated with a BoothDay which falls into
        # the range of [start_date, end_date] inclusive
        for block in BoothBlock.objects.filter(booth_block_reserved=True,
                                               booth_block_current_troop_owner=self.troop_number,
                                               booth_day__booth_day_date__gte=start_date,
                                               booth_day__booth_day_date__lte=end_date):
            if block.booth_day.booth.booth_is_golden_ticket:
                super_booth_count += 1

            total_booth_count += 1

        rem = 0 if (total_booth_count > self.total_booth_tickets_per_week) else (self.total_booth_tickets_per_week - total_booth_count)
        rem_super = 0 if (super_booth_count > self.booth_golden_tickets_per_week) else (self.booth_golden_tickets_per_week - super_booth_count)

        return (rem, rem_super)


@receiver(post_save, sender=User)
def default_group(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(Group.objects.get(name='Troop Cookie Coordinator'))


@receiver(pre_save, sender=Troop)
def update_tickets(sender, instance, **kwargs):
    # This really should only care about setting/updating these after creation, but there is always the chance
    # A troop could be updated after the fact. In that case, if they've booked more blocks than they should've,
    # oh well.
    if instance.super_troop:
        instance.total_booth_tickets_per_week = TroopTicketParameters.super_troop_total_tickets_per_week
        instance.booth_golden_tickets_per_week = TroopTicketParameters.super_troop_golden_tickets_per_week
    else:
        instance.total_booth_tickets_per_week = TroopTicketParameters.normal_troop_total_tickets_per_week
        instance.booth_golden_tickets_per_week = TroopTicketParameters.normal_troop_golden_tickets_per_week


# Groups
# Administrators
# Service Unit Cookie Coordinator
# Service Unit Booth Coordinator
# Service Unit Cookie Captain Coordinator
# Troop Cookie Coordinator
