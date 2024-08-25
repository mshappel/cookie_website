from django.utils.timezone import timedelta


def get_week_start_end_from_date(date):
    start_date = date - timedelta(days=date.weekday())
    end_date = start_date + timedelta(days=6)

    return start_date, end_date
