from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser, User, Group
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class TicketParameters:
    NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK = 5
    NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK = 1

    SUPER_TROOP_TOTAL_TICKETS_PER_WEEK = 10
    SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK = 2


class Levels:
    GIRL_SCOUT_TROOP_LEVELS = [
        (0, 'None'),
        (1, 'Daisies'),
        (2, 'Brownies'),
        (3, 'Juniors'),
        (4, 'Cadettes'),
        (5, 'Seniors'),
        (6, 'Ambassadors')
    ]


class Troop(models.Model):
    troop_number = models.IntegerField(unique=True)
    troop_cookie_coordinator = models.CharField(max_length=300, null=True)

    super_troop = models.BooleanField(default=False)
    troop_level = models.SmallIntegerField(choices=Levels.GIRL_SCOUT_TROOP_LEVELS, default=0)

    total_booth_tickets_per_week = models.PositiveSmallIntegerField(default=0)
    booth_golden_tickets_per_week = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "troops"
        verbose_name = "troop"

    def __str__(self):
        return 'Troop ' + str(self.troop_number)


@receiver(pre_save, sender=Troop)
def update_tickets(sender, instance, **kwargs):
    # This really should only care about setting/updating these after creation, but there is always the chance
    # A troop could be updated after the fact. In that case, if they've booked more blocks than they should've,
    # oh well.
    if instance.super_troop:
        instance.total_booth_tickets_per_week = TicketParameters.SUPER_TROOP_TOTAL_TICKETS_PER_WEEK
        instance.booth_golden_tickets_per_week = TicketParameters.SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK
    else:
        instance.total_booth_tickets_per_week = TicketParameters.NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK
        instance.booth_golden_tickets_per_week = TicketParameters.NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK
