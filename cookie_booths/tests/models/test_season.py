from datetime import datetime

from django.test import TestCase

from cookie_booths.models import CookieSeason
from cookie_booths.tests.helpers.test_helpers import TEST_DATE, create_cookie_season

# season_logger = logging.getLogger("cookie_booths.models")
# season_logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# handler.setFormatter(formatter)
# season_logger.addHandler(handler)


class CookieSeasonTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cookie_season: CookieSeason = create_cookie_season()
        cls.test_date = TEST_DATE

    def test_str_method(self):
        self.assertEqual(str(self.cookie_season), "Cookie Season 2023-01-01 to 2023-03-31")

    def test_cookie_season_week(self):
        self.assertEqual(self.cookie_season.cookie_season_week(TEST_DATE), 3)

    def test_is_booth_reservable(self):
        self.assertTrue(self.cookie_season.is_booth_reservable(TEST_DATE))

    def test_is_daisy_booth_reservable(self):
        self.assertTrue(self.cookie_season.is_daisy_booth_reservable(TEST_DATE))

    def test_is_daisy_booth_not_reservable(self):
        test_date = datetime(2023, 1, 6).date()
        self.assertFalse(self.cookie_season.is_daisy_booth_reservable(test_date))
        self.assertTrue(self.cookie_season.is_booth_reservable(test_date))

    def test_is_booth_reservable_outside_starting_weeks(self):
        test_date = datetime(2023, 2, 1).date()
        self.assertFalse(self.cookie_season.is_booth_reservable(test_date, TEST_DATE))

    def test_is_booth_reservable_one_week_after_starting_weeks(self):
        test_date = datetime(2023, 1, 22).date()
        self.assertTrue(self.cookie_season.is_booth_reservable(test_date, TEST_DATE))

    def test_is_week_within_starting_weeks_reservable(self):
        self.assertTrue(self.cookie_season._is_week_within_starting_weeks_reservable(TEST_DATE))

    def test_is_week_before_or_equal_to_next_week(self):
        self.assertTrue(self.cookie_season._is_week_before_or_equal_to_next_week(TEST_DATE))

    def test_is_week_outside_cookie_season_not_reservable(self):
        test_date = datetime(2023, 4, 1).date()
        self.assertFalse(self.cookie_season._is_between_cookie_season(test_date))

    def test_is_week_within_cookie_season_reservable(self):
        test_date = datetime(2023, 2, 1).date()
        self.assertTrue(self.cookie_season._is_between_cookie_season(test_date))
