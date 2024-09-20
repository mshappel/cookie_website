from datetime import date, datetime

from django.test import TestCase
from django.utils import timezone

from accounts.models import AccountType
from accounts.models import CustomUser as User
from cookie_booths.models import BoothLocation
from cookie_booths.models.day import BoothDay
from cookie_booths.models.managers.days_manager import BoothDayManager


class BoothDayManagerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # open_time = timezone.make_aware(datetime(2023, 1, 1, 9, 0))
        # close_time = timezone.make_aware(datetime(2023, 1, 1, 17, 0))

        cls.manager = BoothDayManager()
        cls.user = User.objects.create(
            email="admin@test.com",
            account_type=AccountType.COOKIE_ADMIN,
        )
        cls.booth_location: BoothLocation = BoothLocation.objects.create(
            booth_location="Test Booth Location",
            booth_address="123 Test St",
            booth_enabled=True,
            booth_start_date=date(2023, 1, 1),
            booth_end_date=date(2023, 1, 31),

        )
        # cls.booth_day: BoothDay = BoothDay.objects.create(
        #     booth_location=cls.booth_location,
        #     booth_day_date=date(2023, 1, 1),
        #     booth_day_enabled=True,
        #     booth_day_hours_set=True,
        #     booth_day_open_time=open_time,
        #     booth_day_close_time=close_time,
        # )