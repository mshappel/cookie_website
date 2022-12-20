# Runs pytest for cookie captain accounts
import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from cookie_booths.models import BoothLocation, BoothDay, BoothBlock, CookieSeason
from cookie_booths.views import get_num_tickets_remaining_cookie_captain

START_DATE = datetime.date(2023, 1, 21)
END_DATE = datetime.date(2023, 2, 26)
SUCCESS_BOOTH_DATE = datetime.date(2023, 2, 4)
FAILURE_BOOTH_DATE = datetime.date(2023, 1, 21)

OPEN_TIME = datetime.time(8, 0, 0, 0)
START_BOOTH_1 = datetime.time(10, 0, 0, 0)
START_BOOTH_2 = datetime.time(12, 0, 0, 0)
START_BOOTH_3 = datetime.time(14, 0, 0, 0)
CLOSE_TIME = datetime.time(16, 0, 0, 0)

TROOP_NUM_1_COOKIE_CAP_ID = 1
TROOP_NUM_2_COOKIE_CAP_ID = 2

COOKIE_CAPTAIN_RESERVE_BLOCK = "Reserve a block for a daisy scout"


class CookieCaptainTests(TestCase):

    SUCCESS_OPEN_TIME = make_aware(
        datetime.datetime.combine(SUCCESS_BOOTH_DATE, OPEN_TIME)
    )
    SUCCESS_CLOSE_TIME = make_aware(
        datetime.datetime.combine(SUCCESS_BOOTH_DATE, CLOSE_TIME)
    )

    FAILURE_OPEN_TIME = make_aware(
        datetime.datetime.combine(FAILURE_BOOTH_DATE, OPEN_TIME)
    )
    FAILURE_CLOSE_TIME = make_aware(
        datetime.datetime.combine(FAILURE_BOOTH_DATE, CLOSE_TIME)
    )

    @classmethod
    def setUpTestData(cls) -> None:
        # Currently we look at the #1 position Cookie Season
        CookieSeason.objects.create(
            season_start_date=START_DATE, season_end_date=END_DATE
        )

        cls.location = BoothLocation.objects.create(
            booth_location="Chokey Chicken", booth_address="O-Town", booth_enabled=True
        )

        cls.success_day = BoothDay.objects.create(
            booth=cls.location, booth_day_date=SUCCESS_BOOTH_DATE
        )
        cls.success_day.add_or_update_hours(
            cls.SUCCESS_OPEN_TIME, cls.SUCCESS_CLOSE_TIME
        )
        cls.success_day.enable_day()

        cls.failure_day = BoothDay.objects.create(
            booth=cls.location, booth_day_date=FAILURE_BOOTH_DATE
        )
        cls.failure_day.add_or_update_hours(
            cls.FAILURE_OPEN_TIME, cls.FAILURE_CLOSE_TIME
        )
        cls.failure_day.change_golden_status(is_golden_booth=True)
        cls.failure_day.enable_day()

        return super().setUpTestData()

    def test_pre_condition(self):
        # Check success conditions
        self.assertEqual(
            BoothBlock.objects.filter(booth_day=self.success_day).count(), 4
        )
        self.assertFalse(
            BoothDay.objects.filter(booth_day_date=SUCCESS_BOOTH_DATE)
            .get()
            .booth_day_is_golden
        )

        # Check fail conditions
        self.assertEqual(
            BoothBlock.objects.filter(booth_day=self.failure_day).count(), 4
        )
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=FAILURE_BOOTH_DATE)
            .get()
            .booth_day_is_golden
        )

    def test_check_remaining_tickets_for_captain_initial_success(self):
        # Non-first week results
        rem, rem_golden_ticket = get_num_tickets_remaining_cookie_captain(
            TROOP_NUM_1_COOKIE_CAP_ID, SUCCESS_BOOTH_DATE
        )
        self.assertEqual(rem, 3)
        self.assertFalse(
            rem_golden_ticket
        )  # Zero is false, so we can just check if it is false

    def test_check_remaining_tickets_for_captain_initial_failure(self):
        # First week results
        rem, rem_golden_ticket = get_num_tickets_remaining_cookie_captain(
            TROOP_NUM_1_COOKIE_CAP_ID, FAILURE_BOOTH_DATE
        )
        self.assertFalse(rem)
        self.assertFalse(rem_golden_ticket)

    def test_check_remaining_tickets_for_captain_after_reservation(self):
        # Let's check if we successfully subtract if a cookie_captain owns a booth
        success_block = BoothBlock.objects.filter(
            booth_block_start_time=self.SUCCESS_OPEN_TIME
        ).get()
        success_block.reserve_block(0, TROOP_NUM_1_COOKIE_CAP_ID)

        rem, rem_golden_tickets = get_num_tickets_remaining_cookie_captain(
            TROOP_NUM_1_COOKIE_CAP_ID, SUCCESS_BOOTH_DATE
        )
        self.assertEqual(rem, 2)
        self.assertFalse(rem_golden_tickets)

    def test_check_remaining_tickets_for_captain_after_multiple_reservations(self):
        # Check for multiple reservations
        # Make first reservation
        success_block = BoothBlock.objects.filter(
            booth_block_start_time=self.SUCCESS_OPEN_TIME
        ).get()
        success_block.reserve_block(0, TROOP_NUM_1_COOKIE_CAP_ID)

        # Make second reservation
        START_BOOTH_1_DATE_TIME = make_aware(
            datetime.datetime.combine(SUCCESS_BOOTH_DATE, START_BOOTH_1)
        )
        success_block = BoothBlock.objects.filter(
            booth_block_start_time=START_BOOTH_1_DATE_TIME
        ).get()
        success_block.reserve_block(0, TROOP_NUM_1_COOKIE_CAP_ID)

        rem, rem_golden_tickets = get_num_tickets_remaining_cookie_captain(
            TROOP_NUM_1_COOKIE_CAP_ID, SUCCESS_BOOTH_DATE
        )

        self.assertEqual(rem, 1)
        self.assertFalse(rem_golden_tickets)

        # Make third reservation
        START_BOOTH_2_DATE_TIME = make_aware(
            datetime.datetime.combine(SUCCESS_BOOTH_DATE, START_BOOTH_2)
        )
        success_block = BoothBlock.objects.filter(
            booth_block_start_time=START_BOOTH_2_DATE_TIME
        ).get()
        success_block.reserve_block(0, TROOP_NUM_1_COOKIE_CAP_ID)

        rem, rem_golden_tickets = get_num_tickets_remaining_cookie_captain(
            TROOP_NUM_1_COOKIE_CAP_ID, SUCCESS_BOOTH_DATE
        )

        self.assertFalse(rem)
        self.assertFalse(rem_golden_tickets)

        # Make sure we can cancel and it recognizes it
        success_block.cancel_block()
        rem, rem_golden_tickets = get_num_tickets_remaining_cookie_captain(
            TROOP_NUM_1_COOKIE_CAP_ID, SUCCESS_BOOTH_DATE
        )

        self.assertEqual(rem, 1)
        self.assertFalse(rem_golden_tickets)

        # Make sure we don't mix it with another user
        rem, rem_golden_tickets = get_num_tickets_remaining_cookie_captain(
            TROOP_NUM_2_COOKIE_CAP_ID, SUCCESS_BOOTH_DATE
        )

        self.assertEqual(rem, 3)
        self.assertFalse(rem_golden_tickets)
