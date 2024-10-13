from datetime import date, datetime
from typing import Generator

from django.utils import timezone
from django.utils.timezone import timedelta

TIME_BLOCK_IN_HOURS = 2
TIME_BLOCK_IN_SECONDS = TIME_BLOCK_IN_HOURS * 3600


def get_week_start_end_from_date(date):
    start_date = date - timedelta(days=date.weekday())
    end_date = start_date + timedelta(days=6)

    return start_date, end_date


def date_range_generator(start_date: date, end_date: date) -> Generator[date, None, None]:
    # Need +1 to be inclusive of the end date
    difference_in_days: int = (end_date - start_date).days

    for n in range(difference_in_days + 1):
        yield start_date + timedelta(n)


def parse_time(time_str: str) -> datetime.time:
    return datetime.strptime(time_str, "%H:%M:%S").time() if time_str else None


def get_one_week_ago():
    one_week_ago = timezone.now() - timedelta(days=7)
    return one_week_ago
