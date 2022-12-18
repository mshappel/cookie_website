from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class TicketParameters:
    SMALL_TROOP_TOTAL_TICKETS_PER_WEEK = 5
    SMALL_TROOP_GOLDEN_TICKETS_PER_WEEK = 1

    MEDIUM_TROOP_TOTAL_TICKETS_PER_WEEK = SMALL_TROOP_TOTAL_TICKETS_PER_WEEK * 2
    MEDIUM_TROOP_GOLDEN_TICKETS_PER_WEEK = SMALL_TROOP_GOLDEN_TICKETS_PER_WEEK * 2

    LARGE_TROOP_TOTAL_TICKETS_PER_WEEK = SMALL_TROOP_TOTAL_TICKETS_PER_WEEK * 3
    LARGE_TROOP_GOLDEN_TICKETS_PER_WEEK = SMALL_TROOP_GOLDEN_TICKETS_PER_WEEK * 3


class TroopSize:
    MEDIUM_TROOP = 8
    LARGE_TROOP = 10


class Troop(models.Model):
    troop_number = models.IntegerField(unique=True)
    troop_cookie_coordinator = models.EmailField(null=True)

    troop_size = models.SmallIntegerField(default=0)
    troop_level = models.SmallIntegerField(
        choices=settings.GIRL_SCOUT_TROOP_LEVELS_WITH_NONE, default=0
    )

    total_booth_tickets_per_week = models.PositiveSmallIntegerField(default=0)
    booth_golden_tickets_per_week = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "troops"
        verbose_name = "troop"

    def __str__(self):
        return "Troop " + str(self.troop_number)


@receiver(pre_save, sender=Troop)
def update_tickets(sender, instance, **kwargs):
    # This really should only care about setting/updating these after creation, but there is always the chance
    # A troop could be updated after the fact. In that case, if they've booked more blocks than they should've,
    # oh well.
    if instance.troop_size >= TroopSize.LARGE_TROOP:
        instance.total_booth_tickets_per_week = (
            TicketParameters.LARGE_TROOP_TOTAL_TICKETS_PER_WEEK
        )
        instance.booth_golden_tickets_per_week = (
            TicketParameters.LARGE_TROOP_GOLDEN_TICKETS_PER_WEEK
        )
        return

    if instance.troop_size >= TroopSize.MEDIUM_TROOP:
        instance.total_booth_tickets_per_week = (
            TicketParameters.MEDIUM_TROOP_TOTAL_TICKETS_PER_WEEK
        )
        instance.booth_golden_tickets_per_week = (
            TicketParameters.MEDIUM_TROOP_GOLDEN_TICKETS_PER_WEEK
        )
        return

    instance.total_booth_tickets_per_week = (
        TicketParameters.SMALL_TROOP_TOTAL_TICKETS_PER_WEEK
    )
    instance.booth_golden_tickets_per_week = (
        TicketParameters.SMALL_TROOP_GOLDEN_TICKETS_PER_WEEK
    )
