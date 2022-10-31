# Tests for the BoothBlock model
from django.conf import settings
from django.test import TestCase

from cookie_booths.models import BoothLocation, BoothDay, BoothBlock

TROOP_NUM_1 = 41001
TROOP_NUM_2 = 312
TROOP_NUM_3 = 309
TROOP_NUM_1_COOKIE_CAP_ID = 1
TROOP_NUM_2_COOKIE_CAP_ID = 2


class BoothBlockTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.location = BoothLocation.objects.create()
        cls.day = BoothDay.objects.create(booth=cls.location)
        cls.block = BoothBlock.objects.create(
            booth_day=cls.day, booth_block_enabled=False
        )

        return super().setUpTestData()

    def test_block_disabled_attempt_reserve(self):
        # Case 1 - block is disabled, trying to reserve.
        # Observe that the block was not reserved.

        # TODO: We should consider adding feedback to the user the reservation failed
        # as part of the model
        self.block.reserve_block(TROOP_NUM_1, TROOP_NUM_1_COOKIE_CAP_ID)
        self.assertNotEqual(self.block.booth_block_current_troop_owner, TROOP_NUM_1)
        self.assertNotEqual(
            self.block.booth_block_current_cookie_captain_owner,
            TROOP_NUM_1_COOKIE_CAP_ID,
        )
        self.assertFalse(self.block.booth_block_reserved)

    def test_block_enabled_attempt_reserve(self):
        # Case 2 - block is enabled, allowed to reserve
        # Observe that the block is reserved
        self._enable_and_reserve_booth_block(TROOP_NUM_1, settings.NO_COOKIE_CAPTAIN_ID)
        self.assertEqual(self.block.booth_block_current_troop_owner, TROOP_NUM_1)
        self.assertEqual(
            self.block.booth_block_current_cookie_captain_owner,
            settings.NO_COOKIE_CAPTAIN_ID,
        )
        self.assertTrue(self.block.booth_block_reserved)

    def test_block_enabled_already_reserved_attempt_reserve(self):
        # Case 3 - block is enabled, already reserved. A new troop cannot reserve it
        # Observe that the block remains reserved to TROOP_NUM_1
        self._enable_and_reserve_booth_block(TROOP_NUM_1, TROOP_NUM_1_COOKIE_CAP_ID)
        self.block.reserve_block(TROOP_NUM_2, TROOP_NUM_2_COOKIE_CAP_ID)
        self.assertEqual(self.block.booth_block_current_troop_owner, TROOP_NUM_1)
        self.assertEqual(
            self.block.booth_block_current_cookie_captain_owner,
            TROOP_NUM_1_COOKIE_CAP_ID,
        )
        self.assertTrue(self.block.booth_block_reserved)

    def test_block_hold_for_cookie_captains_unreserved(self):
        # Verify that a block is held correctly for cookie captains when not reserved
        self.block.hold_for_cookie_captains()
        self.assertTrue(self.block.booth_block_held_for_cookie_captains)

    def test_block_hold_for_cookie_captains_reserved(self):
        # Verify that a block will not be held for cookie captains when it has previously been reserved
        self._enable_and_reserve_booth_block(TROOP_NUM_1, settings.NO_COOKIE_CAPTAIN_ID)
        self.assertFalse(self.block.hold_for_cookie_captains())

    def test_block_unhold_for_cookie_captains_unreserved(self):
        # Verify that a block will be unheld correctly for cookie captains when it has been held previously
        self.block.hold_for_cookie_captains()
        self.block.unhold_for_cookie_captains()
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)

    def test_block_unhold_for_cookie_captains_reserved(self):
        # Verify that when unholding a block that has been reserved will also cause any active reservation to be cancelled
        self.block.hold_for_cookie_captains()
        self._enable_and_reserve_booth_block(TROOP_NUM_1, TROOP_NUM_1_COOKIE_CAP_ID)
        self.block.unhold_for_cookie_captains()
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)
        self.assertEqual(self.block.booth_block_current_troop_owner, 0)
        self.assertEqual(self.block.booth_block_current_cookie_captain_owner, 0)
        self.assertFalse(self.block.booth_block_reserved)

    def test_block_daisy_reservation_disabled(self):
        # Verify that a daisy block reservation fails when the block is disabled
        self.assertFalse(self.block.reserve_daisy_block(TROOP_NUM_1))
        self.assertFalse(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, 0)

    def test_block_daisy_reservation_no_cc(self):
        # Verify that a daisy block reservation fails when the primary owner is not a cookie captain
        self._enable_and_reserve_booth_block(TROOP_NUM_1, settings.NO_COOKIE_CAPTAIN_ID)
        self.assertFalse(self.block.reserve_daisy_block(TROOP_NUM_1))
        self.assertFalse(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, 0)

    def test_block_daisy_reservation_success(self):
        # Verify that a daisy block reservation is successful
        self._enable_and_reserve_booth_block(TROOP_NUM_1, TROOP_NUM_1_COOKIE_CAP_ID)
        self.assertTrue(self.block.reserve_daisy_block(TROOP_NUM_2))
        self.assertTrue(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, TROOP_NUM_2)

    def test_block_daisy_reservation_already_reserved(self):
        # Verify that a daisy block reservation fails when already reserved by another daisy troop
        self._enable_and_reserve_booth_block(TROOP_NUM_1, TROOP_NUM_1_COOKIE_CAP_ID)
        self.assertTrue(self.block.reserve_daisy_block(TROOP_NUM_2))
        self.assertFalse(self.block.reserve_daisy_block(TROOP_NUM_3))
        self.assertTrue(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, TROOP_NUM_2)

    def test_block_daisy_cancellation_disabled(self):
        # Verify that a daisy block reservation cancellation fails when the block is disabled
        self.assertFalse(self.block.cancel_daisy_reservation())

    def test_block_daisy_cancellation_not_reserved(self):
        # Verify that a daisy block reservation cancellation fails when there is no primary owner of the block
        self.block.enable_block()
        self.block.save()

        self.assertFalse(self.block.cancel_daisy_reservation())

    def test_block_daisy_cancellation_not_daisy_reserved(self):
        # Verify that a daisy block reservation cancellation fails when a daisy troop is not currently reserving it
        self._enable_and_reserve_booth_block(TROOP_NUM_1, TROOP_NUM_1_COOKIE_CAP_ID)
        self.assertFalse(self.block.cancel_daisy_reservation())

    def test_block_daisy_cancellation_success(self):
        # Verify that a daisy block reservation cancellation is successful
        self._enable_and_reserve_booth_block(TROOP_NUM_1, TROOP_NUM_1_COOKIE_CAP_ID)
        self.assertTrue(self.block.reserve_daisy_block(TROOP_NUM_2))
        self.assertTrue(self.block.cancel_daisy_reservation())
        self.assertFalse(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, 0)

    def test_block_cancellation_disabled(self):
        # Verify that a booth block cancellation fails when the block is disabled
        self.assertFalse(self.block.cancel_block())

    def test_block_cancellation_not_reserved(self):
        # Verify that a booth block cancellation fails when the block is not currently reserved
        self.block.enable_block()
        self.block.save()

        self.assertFalse(self.block.cancel_block())

    def test_block_cancellation_success(self):
        # Verify that a booth block reservation cancellation is successful
        self._enable_and_reserve_booth_block(TROOP_NUM_1, TROOP_NUM_1_COOKIE_CAP_ID)
        self.assertTrue(self.block.reserve_daisy_block(TROOP_NUM_2))
        self.assertTrue(self.block.cancel_block())
        self.assertFalse(self.block.booth_block_reserved)
        self.assertEqual(self.block.booth_block_current_troop_owner, 0)
        self.assertFalse(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, 0)

    def _enable_and_reserve_booth_block(
        self, TROOP_NUM: int, COOKIE_CAP_ID: int
    ) -> None:
        self.block.booth_block_enabled = True
        self.block.reserve_block(TROOP_NUM, COOKIE_CAP_ID)
