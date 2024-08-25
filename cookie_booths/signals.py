from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver

from cookie_booths.models import BoothHours, BoothLocation, CookieSeason


@receiver(post_save, sender=CookieSeason)
def get_real_season_start_date(sender, instance, created, **kwargs):
    # The season starts on a Saturday, but the for our purposes, it actually starts on a Monday
    start_date = instance.season_start_date
    real_season_start_date = start_date - timedelta(days=start_date.weekday())
    CookieSeason.objects.filter(pk=instance.pk).update(
        real_season_start_date=real_season_start_date
    )


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
