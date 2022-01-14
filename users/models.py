from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser, User, Group
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class TroopTicketParameters:
    NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK = 5
    NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK = 1

    SUPER_TROOP_TOTAL_TICKETS_PER_WEEK = 10
    SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK = 2

    GIRL_SCOUT_TROOP_LEVELS = [
        (1, 'Daisies'),
        (2, 'Brownies'),
        (3, 'Juniors'),
        (4, 'Cadettes'),
        (5, 'Seniors'),
        (6, 'Ambassadors')
    ]


# User-related Models
class User(AbstractUser):
    pass

    @property
    def full_name(self):
        """Returns the person's full name"""
        return '%s %s' % (self.first_name, self.last_name)


def get_week_start_end_from_date(date):
    start_date = date - timedelta(days=date.weekday())
    end_date = start_date + timedelta(days=6)

    return start_date, end_date


class Troop(models.Model):
    troop_number = models.IntegerField(unique=True)
    troop_name = models.CharField(max_length=300, blank=True)

    troop_cookie_coordinator = models.CharField(max_length=300, null=True)

    super_troop = models.BooleanField(default=False)
    troop_level = models.SmallIntegerField(choices=TroopTicketParameters.GIRL_SCOUT_TROOP_LEVELS,
                                           default=0)

    total_booth_tickets_per_week = models.PositiveSmallIntegerField(default=0)
    booth_golden_tickets_per_week = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "troops"
        verbose_name = "troop"

        permissions = (('troop_creation', "Create a troop"),
                       ('troop_updates', "Updates a troop"),
                       ('troop_deletion', "Deletes a troop")
                       )

    def __str__(self):
        return 'Troop ' + str(self.troop_number)


@receiver(post_save, sender=User)
def default_group(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(Group.objects.get(name='Troop Cookie Coordinator'))
        instance.groups.add(Group.objects.get(name='Users'))


@receiver(pre_save, sender=Troop)
def update_tickets(sender, instance, **kwargs):
    # This really should only care about setting/updating these after creation, but there is always the chance
    # A troop could be updated after the fact. In that case, if they've booked more blocks than they should've,
    # oh well.
    if instance.super_troop:
        instance.total_booth_tickets_per_week = TroopTicketParameters.SUPER_TROOP_TOTAL_TICKETS_PER_WEEK
        instance.booth_golden_tickets_per_week = TroopTicketParameters.SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK
    else:
        instance.total_booth_tickets_per_week = TroopTicketParameters.NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK
        instance.booth_golden_tickets_per_week = TroopTicketParameters.NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK
