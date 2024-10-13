from datetime import date, time

from django.test import TestCase

from cookie_booths.models import BoothLocation
from cookie_booths.models.schedule import BoothSchedule


class BoothScheduleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.booth_location: BoothLocation = BoothLocation.objects.create(
            booth_location="Test Booth Location",
            booth_address="123 Test St",
            booth_enabled=True,
        )
        cls.booth_schedule: BoothSchedule = BoothSchedule.objects.get(
            booth_location=cls.booth_location,
            booth_start_date=date(2024, 1, 1),
            booth_end_date=date(2024, 1, 31),
        )

        cls.booth_schedule.set_schedule(
            booth_schedule={
                "monday": {"open": True, "open_time": "09:00:00", "close_time": "17:00:00"},
                "tuesday": {"open": True, "open_time": "09:00:00", "close_time": "17:00:00"},
                "thursday": {"open": True, "open_time": "09:00:00", "close_time": "17:00:00"},
                "friday": {"open": True, "open_time": "09:00:00", "close_time": "17:00:00"},
                "sunday": {
                    "open": True,
                    "open_time": "10:00:00",
                    "close_time": "16:00:00",
                    "golden_ticket": True,
                },
            },
        )

    def test_schedule_for_non_golden(self):
        self.assertEqual(
            self.booth_schedule.get_schedule_for_day("monday"),
            {
                "open": True,
                "open_time": time(9, 0),
                "close_time": time(17, 0),
            },
        )

    def test_schedule_for_golden(self):
        self.assertEqual(
            self.booth_schedule.get_schedule_for_day("sunday"),
            {
                "open": True,
                "open_time": time(10, 0),
                "close_time": time(16, 0),
                "golden_ticket": True,
            },
        )

    def test_set_schedule_non_golden(self):
        self.booth_schedule.set_schedule_for_day("monday", "open", False)
        self.assertEqual(
            self.booth_schedule.get_schedule_for_day("monday"),
            {"open": False, "open_time": None, "close_time": None},
        )

    def test_set_schedule_golden(self):
        self.booth_schedule.set_schedule_for_day("sunday", "open", False)
        self.assertEqual(
            self.booth_schedule.get_schedule_for_day("sunday"),
            {"open": False, "open_time": None, "close_time": None, "golden_ticket": False},
        )

    def test_str_method(self):
        expected_str = f"{self.booth_location} Schedule"
        self.assertEqual(str(self.booth_schedule), expected_str)

    def test_set_schedule_for_non_existent_day(self):
        # Check that there is nothing in existence for Wednesday initially
        self.assertEqual(
            self.booth_schedule.get_schedule_for_day("wednesday"),
            {
                "open": False,
                "open_time": None,
                "close_time": None,
            },
        )

        # Set the schedule for Wednesday
        self.booth_schedule.set_schedule_for_day("wednesday", "open", True)
        self.booth_schedule.set_schedule_for_day("wednesday", "open_time", "09:00:00")
        self.booth_schedule.set_schedule_for_day("wednesday", "close_time", "17:00:00")

        # Check that the schedule for Wednesday is set correctly
        self.assertEqual(
            self.booth_schedule.get_schedule_for_day("wednesday"),
            {
                "open": True,
                "open_time": time(9, 0),
                "close_time": time(17, 0),
            },
        )

    def test_set_schedule_for_non_existent_golden_day(self):
        # Check that there is nothing in existence for Wednesday initially
        self.assertEqual(
            self.booth_schedule.get_schedule_for_day("saturday"),
            {
                "open": False,
                "open_time": None,
                "close_time": None,
                "golden_ticket": False,
            },
        )

        # Set the schedule for Wednesday
        self.booth_schedule.set_schedule_for_day("saturday", "open", True)
        self.booth_schedule.set_schedule_for_day("saturday", "open_time", "10:00:00")
        self.booth_schedule.set_schedule_for_day("saturday", "close_time", "16:00:00")
        self.booth_schedule.set_schedule_for_day("saturday", "golden_ticket", False)

        # Check that the schedule for Wednesday is set correctly
        self.assertEqual(
            self.booth_schedule.get_schedule_for_day("saturday"),
            {
                "open": True,
                "open_time": time(10, 0),
                "close_time": time(16, 0),
                "golden_ticket": False,
            },
        )
