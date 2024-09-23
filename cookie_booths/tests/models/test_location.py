from django.test import TestCase

from cookie_booths.models import BoothLocation, BoothSchedule


class BoothLocationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.booth_location: BoothLocation = BoothLocation.objects.create(
            booth_location="Test Booth Location",
            booth_address="Test Booth Address",
            booth_enabled=True,
            booth_block_level_restrictions_start=1,
            booth_block_level_restrictions_end=3,
            booth_is_outside=False,
            booth_notes="Test Booth Notes",
        )

    def test_str(self):
        self.assertEqual(str(self.booth_location), "Test Booth Location")

    def test_passes_level_restrictions(self):
        self.assertTrue(self.booth_location.passes_level_restrictions(2))
        self.assertFalse(self.booth_location.passes_level_restrictions(4))
