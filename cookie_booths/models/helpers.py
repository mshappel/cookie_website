def _get_booth_block_model(self):
    from cookie_booths.models.blocks import BoothBlock

    return BoothBlock


def _get_booth_day_model(self):
    from cookie_booths.models.day import BoothDay

    return BoothDay


def _get_booth_hours_model(self):
    from cookie_booths.models.hours import BoothHours

    return BoothHours
