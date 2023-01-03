from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


class TicketParameters(models.Model):
    small_troop_total_tickets_per_week = models.IntegerField(default=5)
    small_troop_golden_tickets_per_week = models.IntegerField(default=1)
    medium_troop_additional_golden_tickets = models.IntegerField(default=1)
    large_troop_additional_golden_tickets = models.IntegerField(default=2)

    @property
    def get_small_troop_total_tickets_per_week(self):
        return self.small_troop_total_tickets_per_week

    @property
    def get_small_troop_golden_tickets_per_week(self):
        return self.small_troop_golden_tickets_per_week
    
    @property
    def get_medium_troop_total_tickets_per_week(self):
        return int(self.small_troop_golden_tickets_per_week * 2)

    @property
    def get_medium_troop_golden_tickets_per_week(self):
        return int(self.small_troop_golden_tickets_per_week + 
            self.medium_troop_additional_golden_tickets)

    @property
    def get_large_troop_total_tickets_per_week(self):
        return int(self.small_troop_total_tickets_per_week * 3)
        
    @property
    def get_large_troop_golden_tickets_per_week(self):
        return int(self.small_troop_golden_tickets_per_week +
            self.large_troop_additional_golden_tickets)

    # We only EVER need one instance of this model.
    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)


class TroopSize(models.Model):
    medium_troop_size = models.IntegerField(default=8)
    large_troop_size = models.IntegerField(default=10)

    @property
    def get_medium_troop_size(self):
        return int(self.medium_troop_size)

    @property
    def get_large_troop_size(self):
        return int(self.large_troop_size)

    # We only EVER need one instance of this model.
    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)


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
def update_troop(sender, instance, **kwargs):
    # This really should only care about setting/updating these after creation, but there is always the chance
    # A troop could be updated after the fact. In that case, if they've booked more blocks than they should've,
    # oh well.
    if not TroopSize.objects.first():
        TroopSize.objects.create()
    if not TicketParameters.objects.first():    
        TicketParameters.objects.create()
    update_tickets(instance)


@receiver(post_save, sender=TroopSize)
@receiver(post_save, sender=TicketParameters)
def update_all_troops(sender, instance, **kwargs):
    troops = Troop.objects.all()
    for troop in troops:
        update_tickets(troop=troop)
        troop.save()

def update_tickets(troop):
    # This really should only care about setting/updating these after creation, but there is always the chance
    # A troop could be updated after the fact. In that case, if they've booked more blocks than they should've,
    # oh well.
    try:
        if troop.troop_size >= TroopSize.objects.first().get_large_troop_size:
            troop.total_booth_tickets_per_week = (
                TicketParameters.objects.first().get_large_troop_total_tickets_per_week
            )
            troop.booth_golden_tickets_per_week = (
                TicketParameters.objects.first().get_large_troop_golden_tickets_per_week
            )
            return

        if troop.troop_size >= TroopSize.objects.first().get_medium_troop_size:
            troop.total_booth_tickets_per_week = (
                TicketParameters.objects.first().get_medium_troop_total_tickets_per_week
            )
            troop.booth_golden_tickets_per_week = (
                TicketParameters.objects.first().get_medium_troop_golden_tickets_per_week
            )
            return

        troop.total_booth_tickets_per_week = (
            TicketParameters.objects.first().get_small_troop_total_tickets_per_week
        )
        troop.booth_golden_tickets_per_week = (
            TicketParameters.objects.first().get_small_troop_golden_tickets_per_week
        )
    except AttributeError:
        # Do not try to update if we cannot find the Parameters yet. 
        pass
