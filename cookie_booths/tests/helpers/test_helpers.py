from datetime import datetime

from cookie_booths.models import BoothLocation, CookieSeason

BOOTH_LOCATION_DATA = {
    "booth_location": "Test Booth Location",
    "booth_address": "Test Booth Address",
    "booth_enabled": True,
    "booth_block_level_restrictions_start": 1,
    "booth_block_level_restrictions_end": 3,
    "booth_start_date": datetime(2023, 1, 1).date(),
    "booth_end_date": datetime(2023, 3, 31).date(),
    "booth_is_outside": False,
    "booth_notes": "Test Booth Notes",
}

COOKIE_SEASON_DATA = {
    "season_start_date": datetime(2023, 1, 1).date(),
    "season_end_date": datetime(2023, 3, 31).date(),
    "real_season_start_date": datetime(2023, 1, 1).date(),
    "ffa_day_of_week": 0,
    "starting_weeks_reservable": 3,
    "daisy_starting_weeks_offset": 1,
}

TEST_DATE = datetime(2023, 1, 15).date()


def create_booth_location(**kwargs):
    """
    Create and return a BoothLocation object with default or overridden attributes.

    Args:
        **kwargs: Optional keyword arguments to override default BOOTH_LOCATION_DATA.

    Returns:
        BoothLocation: The created BoothLocation object.
    """
    data = BOOTH_LOCATION_DATA.copy()
    data.update(kwargs)
    return BoothLocation.objects.create(
        booth_location=data["booth_location"],
        booth_address=data["booth_address"],
        booth_enabled=data["booth_enabled"],
        booth_block_level_restrictions_start=data["booth_block_level_restrictions_start"],
        booth_block_level_restrictions_end=data["booth_block_level_restrictions_end"],
        booth_start_date=data["booth_start_date"],
        booth_end_date=data["booth_end_date"],
        booth_is_outside=data["booth_is_outside"],
        booth_notes=data["booth_notes"],
    )


def create_cookie_season(**kwargs):
    """
    Create and return a CookieSeason object with default or overridden attributes.

    Args:
        **kwargs: Optional keyword arguments to override default COOKIE_SEASON_DATA.

    Returns:
        CookieSeason: The created CookieSeason object.
    """
    data = COOKIE_SEASON_DATA.copy()
    data.update(kwargs)
    return CookieSeason.objects.create(
        season_start_date=data["season_start_date"],
        season_end_date=data["season_end_date"],
        real_season_start_date=data["real_season_start_date"],
        ffa_day_of_week=data["ffa_day_of_week"],
        starting_weeks_reservable=data["starting_weeks_reservable"],
        daisy_starting_weeks_offset=data["daisy_starting_weeks_offset"],
    )
