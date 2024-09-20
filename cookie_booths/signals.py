import logging
from datetime import timedelta

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from cookie_booths.models import (
    BoothDailyAttributes,
    BoothDay,
    BoothLocation,
    CookieSeason,
)

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

pre_boothlocation_save_state = {}
pre_boothdailyattributes_save_state = {}


@receiver(post_save, sender=CookieSeason)
def get_real_season_start_date(sender, instance: CookieSeason, created, **kwargs):
    # The season starts on a Saturday, but the for our purposes, it actually starts on a Monday
    start_date = instance.season_start_date
    real_season_start_date = start_date - timedelta(days=start_date.weekday())
    CookieSeason.objects.filter(pk=instance.pk).update(
        real_season_start_date=real_season_start_date
    )


@receiver(pre_save, sender=BoothLocation)
def store_pre_boothlocation_save_state(sender, instance: BoothLocation, **kwargs):
    pre_boothlocation_save_state[instance.pk] = instance


@receiver(pre_save, sender=BoothDailyAttributes)
def store_pre_boothdailyattributes_save_state(sender, instance: BoothDailyAttributes, **kwargs):
    pre_boothdailyattributes_save_state[instance.pk] = instance


@receiver(post_save, sender=BoothLocation)
def update_hours(sender, instance: BoothLocation, created, **kwargs):
    _logger.debug("Updating hours for booth day %s", str(instance))
    if created:
        BoothDailyAttributes.objects.create(booth_location=instance)
    else:
        old_instance: BoothLocation = pre_boothlocation_save_state.pop(instance.pk, None)
        booth_location = instance.booth_location
        if old_instance:
            if _booth_dates_changed(old_instance, instance):
                BoothDay.update_booth_day_attributes(booth_location=booth_location)
            if _booth_enabled_changed(old_instance, instance):
                BoothDay.enable_disable_booth_day(booth_location=booth_location)


@receiver(post_save, sender=BoothDailyAttributes)
def create_or_update_days(sender, instance: BoothDailyAttributes, created, **kwargs):
    _logger.debug("Creating or updating days for booth day %s", str(instance.booth_location))
    BoothDay.update_booth_day_attributes(instance.booth_location)


def _booth_dates_changed(old_instance: BoothLocation, new_instance: BoothLocation):
    start_date_changed = old_instance.booth_start_date != new_instance.booth_start_date
    end_date_changed = old_instance.booth_end_date != new_instance.booth_end_date
    return start_date_changed or end_date_changed


def _booth_enabled_changed(old_instance: BoothLocation, new_instance: BoothLocation):
    booth_enabled_changed = old_instance.booth_enabled != new_instance.booth_enabled
    return booth_enabled_changed

