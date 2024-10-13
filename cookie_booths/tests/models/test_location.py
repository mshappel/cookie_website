from django.test import TestCase

from cookie_booths.models import BoothLocation
from cookie_booths.tests.helpers.test_helpers import (
    BOOTH_LOCATION_DATA,
    create_booth_location,
)


class BoothLocationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.booth_location: BoothLocation = create_booth_location()

    def test_booth_location_setup(self):
        booth_location = self.booth_location
        self.assertEqual(booth_location.booth_location, BOOTH_LOCATION_DATA["booth_location"])
        self.assertEqual(booth_location.booth_address, BOOTH_LOCATION_DATA["booth_address"])
        self.assertTrue(booth_location.booth_enabled)
        self.assertEqual(
            booth_location.booth_block_level_restrictions_start,
            BOOTH_LOCATION_DATA["booth_block_level_restrictions_start"],
        )
        self.assertEqual(
            booth_location.booth_block_level_restrictions_end,
            BOOTH_LOCATION_DATA["booth_block_level_restrictions_end"],
        )
        self.assertEqual(booth_location.booth_start_date, BOOTH_LOCATION_DATA["booth_start_date"])
        self.assertEqual(booth_location.booth_end_date, BOOTH_LOCATION_DATA["booth_end_date"])
        self.assertFalse(booth_location.booth_is_outside)
        self.assertEqual(booth_location.booth_notes, BOOTH_LOCATION_DATA["booth_notes"])

    def test_passes_level_restrictions(self):
        self.assertTrue(self.booth_location.passes_level_restrictions(2))
        self.assertFalse(self.booth_location.passes_level_restrictions(4))
