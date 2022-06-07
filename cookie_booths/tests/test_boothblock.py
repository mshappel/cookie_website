# Tests for the BoothBlock model
from django.test import TestCase

from cookie_booths.models import BoothLocation, BoothDay, BoothBlock

TROOP_NUM_1 = 41001
TROOP_NUM_2 = 312


class BoothBlockTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls) -> None:
        cls.location = BoothLocation.objects.create()
        cls.day = BoothDay.objects.create(booth=cls.location)
        cls.block = BoothBlock.objects.create(booth_day=cls.day, booth_block_enabled=False)

        return super().setUpTestData()
    
    def test_block_disabled_attempt_reserve(self):
        # Case 1 - block is disabled, trying to reserve.
        # Observe that the block was not reserved.
        
        # TODO: We should consider adding feedback to the user the reservation failed 
        # as part of the model
        self.block.reserve_block(TROOP_NUM_1)
        self.assertNotEqual(self.block.booth_block_current_troop_owner, TROOP_NUM_1)
        self.assertFalse(self.block.booth_block_reserved)

    def test_block_enabled_attempt_reserve(self):
        # Case 2 - block is enabled, allowed to reserve
        # Observe that the block is reserved
        self._enable_and_reserve_booth_block(TROOP_NUM_1)
        self.assertEqual(self.block.booth_block_current_troop_owner, TROOP_NUM_1)
        self.assertTrue(self.block.booth_block_reserved)

    def test_block_enabled_already_reserved_attempt_reserve(self):
        # Case 3 - block is enabled, already reserved. A new troop cannot reserve it
        # Observe that the block remains reserved to TROOP_NUM_1
        self._enable_and_reserve_booth_block(TROOP_NUM_1)
        self.block.reserve_block(TROOP_NUM_2)
        self.assertEqual(self.block.booth_block_current_troop_owner, TROOP_NUM_1)
        self.assertTrue(self.block.booth_block_reserved)

    def _enable_and_reserve_booth_block(self, TROOP_NUM):
        self.block.booth_block_enabled = True
        self.block.reserve_block(TROOP_NUM)

