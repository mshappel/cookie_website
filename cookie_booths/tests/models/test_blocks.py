from datetime import date

from django.test import TestCase

from accounts.models import AccountType
from accounts.models import CustomUser as User
from cookie_booths.models import (
    BoothDailyAttributes,
    BoothLocation,
)


class BaseBoothBlockTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
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
        cls.booth_daily_attributes = BoothDailyAttributes.objects.create(
            booth_location=cls.booth_location,
        )

        cls.user_tcc = User.objects.create(
            email="tcc@test.com",
            account_type=AccountType.TCC,
        )
        cls.user_cc = User.objects.create(
            email="cc@test.com",
            account_type=AccountType.COOKIE_CAPTAIN,
        )


class BoothBlockTestCase(BaseBoothBlockTestCase):
    def test_cancel_block(self):
        self.block.reserve_block(self.user_tcc)
        self.assertEqual(self.block.booth_block_current_owner, self.user_tcc)
        self.assertTrue(self.block.cancel_block())
        self.assertFalse(self.block.booth_block_reserved)
        self.assertIsNone(self.block.booth_block_current_owner)

    def test_reserve_block(self):
        owner = self.user_tcc
        self.assertTrue(self.block.reserve_block(owner))
        self.assertTrue(self.block.booth_block_reserved)
        self.assertEqual(self.block.booth_block_current_owner, owner)

    def test_cancel_daisy_reservation(self):
        owner = self.user_cc
        self.block.reserve_block(owner)
        self.block.reserve_daisy_block(1)
        self.assertTrue(self.block.cancel_daisy_reservation())
        self.assertFalse(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, 0)

    def test_reserve_daisy_block(self):
        owner = self.user_cc
        self.block.reserve_block(owner)
        self.assertTrue(self.block.reserve_daisy_block(1))
        self.assertTrue(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, 1)

    def test_enable_block(self):
        self.block.disable_block()
        self.assertTrue(self.block.enable_block())
        self.assertTrue(self.block.booth_block_enabled)

    def test_disable_block(self):
        self.assertTrue(self.block.disable_block())
        self.assertFalse(self.block.booth_block_enabled)


class BoothBlockHelperFunctionsTestCase(BaseBoothBlockTestCase):
    def test_is_block_enabled(self):
        self.block.enable_block()
        self.assertTrue(self.block._is_block_enabled())
        self.block.disable_block()
        self.assertFalse(self.block._is_block_enabled())

    def test_is_block_reserved(self):
        owner = self.user_tcc
        self.assertFalse(self.block._is_block_reserved())
        self.block.reserve_block(owner)
        self.assertTrue(self.block._is_block_reserved())

    def test_update_reservation(self):
        owner = self.user_tcc
        self.block._update_reservation(should_reserve=True, owner=owner)
        self.assertTrue(self.block.booth_block_reserved)
        self.assertEqual(self.block.booth_block_current_owner, owner)
        self.block._update_reservation(should_reserve=False)
        self.assertFalse(self.block.booth_block_reserved)
        self.assertIsNone(self.block.booth_block_current_owner)

    def test_update_daisy_reservation(self):
        self.assertFalse(self.block._is_daisy_reserved())
        self.block._update_daisy_reservation(should_reserve=True, daisy_troop_id=1)
        self.assertTrue(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, 1)
        self.block._update_daisy_reservation(should_reserve=False)
        self.assertFalse(self.block.booth_block_daisy_reserved)
        self.assertEqual(self.block.booth_block_daisy_troop_owner, 0)

    def test_set_hold_for_cookie_captains(self):
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)
        self.assertTrue(self.block._set_hold_for_cookie_captains(True))
        self.assertTrue(self.block.booth_block_held_for_cookie_captains)

    def test_set_hold_for_cookie_captains_already_held(self):
        self.block.booth_block_held_for_cookie_captains = True
        self.block.save()
        self.assertTrue(self.block.booth_block_held_for_cookie_captains)
        self.assertFalse(self.block._set_hold_for_cookie_captains(True))
        self.assertTrue(self.block.booth_block_held_for_cookie_captains)

    def test_set_hold_for_cookie_captains_with_reserved_block(self):
        self.block.reserve_block(self.user_tcc)
        self.assertTrue(self.block.booth_block_reserved)
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)
        self.assertFalse(self.block._set_hold_for_cookie_captains(True))
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)

    def test_unset_hold_for_cookie_captains(self):
        self.block.booth_block_held_for_cookie_captains = True
        self.block.save()
        self.assertTrue(self.block.booth_block_held_for_cookie_captains)
        self.assertTrue(self.block._set_hold_for_cookie_captains(False))
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)

    def test_unset_hold_for_cookie_captains_already_unset(self):
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)
        self.assertFalse(self.block._set_hold_for_cookie_captains(False))
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)

    def test_unset_hold_for_cookie_captains_with_reserved_block(self):
        self.block.reserve_block(self.user_tcc)
        self.assertTrue(self.block.booth_block_reserved)
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)
        self.assertFalse(self.block._set_hold_for_cookie_captains(False))
        self.assertFalse(self.block.booth_block_held_for_cookie_captains)

    def test_set_block_enabled(self):
        self.assertTrue(self.block.booth_block_enabled)
        self.assertTrue(self.block._set_block_enabled(False))
        self.assertFalse(self.block.booth_block_enabled)
        self.assertTrue(self.block._set_block_enabled(True))
        self.assertTrue(self.block.booth_block_enabled)
