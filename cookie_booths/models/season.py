from django.db import models
from django.db.models import Q
from django.utils import timezone

from utils.constants import DAYS_OF_WEEK


class CookieSeason(models.Model):
    season_start_date = models.DateField(blank=True, null=True)
    season_end_date = models.DateField(blank=True, null=True)

    real_season_start_date = models.DateField(blank=True, null=True)

    ffa_day_of_week = models.SmallIntegerField(choices=DAYS_OF_WEEK, default=0)
    starting_weeks_reservable = models.SmallIntegerField(default=0)

    def __str__(self):
        # Makes the string in the admin site more useful
        return f"Cookie Season {self.season_start_date} to {self.season_end_date}"

    def cookie_season_week(self, current_date):
        # Determines which week in the season the current date exists
        return (current_date - self.real_season_start_date).days // 7 + 1

    def is_booth_reservable(self, booth_date):
        # Is the vieawable, but not reservable
        # Two conditions where a booth is viewable:
        # 1) If the booth date's week is less than or equal to the weeks reserable set by the SUCM
        # 2) If the booth date's week is less than or equal to the current cookie season week + 1.
        # EXAMPLE:
        # Let's say starting_weeks_reservable is 3, this means the first three of the cookie season
        # are immediately reservable. For subsequent weeks, let's say we're now in the 4th week of
        # sales. That means we should be able to see weeks 1-5.
        is_reservable = self.cookie_season_week(
            current_date=booth_date
        ) <= self.starting_weeks_reservable or self.cookie_season_week(
            current_date=timezone.datetime.today().date()
        ) + 1 >= self.cookie_season_week(
            current_date=booth_date
        )

        return is_reservable

    @classmethod
    def is_booth_reservable_for_date(cls, booth_day):
        try:
            season = cls.objects.get(
                Q(season_start_date__lte=booth_day) & Q(season_end_date__gte=booth_day)
            )
            return season.is_booth_reservable(booth_date=booth_day)
        except cls.DoesNotExist:
            return False

    def get_ffa_start_date(self, current_date):
        pass
