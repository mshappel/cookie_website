from datetime import date, datetime, time

from django.test import TestCase

from cookie_booths.models import BoothLocation
from cookie_booths.models.daily_attributes import BoothDailyAttributes


class BoothDailyAttributesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.booth_location: BoothLocation = BoothLocation.objects.create(
            booth_location="Test Booth Location",
            booth_address="123 Test St",
            booth_enabled=True,
            booth_start_date=date(2024, 1, 1),
            booth_end_date=date(2024, 1, 31),
        )
        cls.booth_daily_attributes: BoothDailyAttributes = BoothDailyAttributes.objects.get(
            booth_location=cls.booth_location
        )

        cls.booth_daily_attributes.set_daily_attributes(
            daily_attributes={
                "monday": {"open": True, "open_time": "09:00:00", "close_time": "17:00:00"},
                "tuesday": {"open": True, "open_time": "09:00:00", "close_time": "17:00:00"},
                "wednesday": {"open": True, "open_time": "09:00:00", "close_time": "17:00:00"},
                "thursday": {"open": True, "open_time": "09:00:00", "close_time": "17:00:00"},
                "friday": {"open": True, "open_time": "09:00:00", "close_time": "17:00:00"},
                "saturday": {
                    "open": True,
                    "open_time": "10:00:00",
                    "close_time": "16:00:00",
                    "golden_ticket": True,
                },
                "sunday": {
                    "open": True,
                    "open_time": "10:00:00",
                    "close_time": "16:00:00",
                    "golden_ticket": True,
                },
            },
        )

    def test_get_daily_attribute_day(self):
        self.assertEqual(
            self.booth_daily_attributes.get_daily_attribute_day("monday"),
            {"open": False, "open_time": None, "close_time": None},
        )

    def test_set_daily_attribute(self):
        self.booth_daily_attributes.set_daily_attribute("monday", "open", True)
        self.assertEqual(
            self.booth_daily_attributes.get_daily_attribute_day("monday"),
            {"open": True, "open_time": None, "close_time": None},
        )

    def test_save(self):
        self.booth_daily_attributes.daily_attributes = {
            "monday": {"open": True, "open_time": "09:00", "close_time": "17:00"},
            "tuesday": {"open": True, "open_time": "09:00", "close_time": "17:00"},
        }
        self.booth_daily_attributes.save()
        self.assertEqual(
            self.booth_daily_attributes.get_daily_attribute_day("monday"),
            {"open": True, "open_time": "09:00", "close_time": "17:00"},
        )
        self.assertEqual(
            self.booth_daily_attributes.get_daily_attribute_day("tuesday"),
            {"open": True, "open_time": "09:00", "close_time": "17:00"},
        )
