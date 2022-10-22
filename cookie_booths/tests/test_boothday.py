# Runs pytest on the BoothDay model
import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from cookie_booths.models import BoothLocation, BoothDay, BoothBlock


TEST_DATE = datetime.date(2021, 10, 22)
TEST_DATE_2 = datetime.date(2021, 10, 23)
DEFAULT_OPEN_TIME = make_aware(datetime.datetime(2021, 10, 22, 8, 0, 0, 0))
DEFAULT_MIDDLE_TIME = make_aware(datetime.datetime(2021, 10, 22, 10, 0, 0, 0))
DEFAULT_CLOSE_TIME = make_aware(datetime.datetime(2021, 10, 22, 12, 0, 0, 0))
DEFAULT_OPEN_TIME_2 = make_aware(datetime.datetime(2021, 10, 23, 8, 0, 0, 0))
DEFAULT_CLOSE_TIME_2 = make_aware(datetime.datetime(2021, 10, 23, 12, 0, 0, 0))


class AddOrUpdateHours(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.location = BoothLocation.objects.create()

        cls.day = BoothDay.objects.create(
            booth=cls.location,
            booth_day_date=TEST_DATE,
            booth_day_hours_set=False,
            booth_day_enabled=False,
        )

        return super().setUpTestData()

    def test_pre_condition(self):
        self.assertEqual(BoothBlock.objects.count(), 0)

    def test_add_with_no_hours_set(self):
        # Case 1 - we have no hours set.
        # Set booth time for 4 hours, results in 2 booths created (booth are 2 hours each)

        _init_booth_hours(self.day)
        self.assertTrue(self.day.booth_day_hours_set)
        self.assertEqual(BoothBlock.objects.count(), 2)

        # One should be 8-10, the other 10-12
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=DEFAULT_OPEN_TIME,
                booth_block_end_time=DEFAULT_MIDDLE_TIME,
            )
        )
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=DEFAULT_MIDDLE_TIME,
                booth_block_end_time=DEFAULT_CLOSE_TIME,
            )
        )

    def test_update_open_and_close_time(self):
        # Case 2 - hours already set. We're moving to hours totally exclusive of the current hours
        # All blocks currently there should be deleted, and we should have two new blocks created
        _init_booth_hours(self.day)

        # Change hours
        NEW_OPEN_TIME = make_aware(datetime.datetime(2021, 10, 22, 14, 0, 0, 0))
        NEW_CLOSE_TIME = make_aware(datetime.datetime(2021, 10, 22, 18, 0, 0, 0))
        NEW_MIDDLE_TIME = make_aware(datetime.datetime(2021, 10, 22, 16, 0, 0, 0))

        self.day.add_or_update_hours(NEW_OPEN_TIME, NEW_CLOSE_TIME)

        # Confirm we still have two blocks present
        self.assertEqual(BoothBlock.objects.count(), 2)

        # And confirm that the time ranges are what we expected - 14-16, 16-18
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=NEW_OPEN_TIME,
                booth_block_end_time=NEW_MIDDLE_TIME,
            )
        )
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=NEW_MIDDLE_TIME,
                booth_block_end_time=NEW_CLOSE_TIME,
            )
        )

    def test_update_later_close_time_even(self):
        # Case 3 - hours already set. We're going to extend the closing time.
        # We expect a new block added on the end
        _init_booth_hours(self.day)

        NEW_CLOSE_TIME = make_aware(datetime.datetime(2021, 10, 22, 14, 0, 0, 0))
        self.day.add_or_update_hours(DEFAULT_OPEN_TIME, NEW_CLOSE_TIME)

        # Confirm we now have three blocks
        self.assertEqual(BoothBlock.objects.count(), 3)

        # The existing blocks should not have been modified, and we'll have one new one
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=DEFAULT_OPEN_TIME,
                booth_block_end_time=DEFAULT_MIDDLE_TIME,
            )
        )
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=DEFAULT_MIDDLE_TIME,
                booth_block_end_time=DEFAULT_CLOSE_TIME,
            )
        )
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=DEFAULT_CLOSE_TIME,
                booth_block_end_time=NEW_CLOSE_TIME,
            )
        )

    def test_update_later_close_time_odd(self):
        # Case 4 - hours already set. Extend the closing by a not clean amount (3 hours)
        _init_booth_hours(self.day)
        NEW_CLOSE_TIME = make_aware(datetime.datetime(2021, 10, 22, 15, 0, 0, 0))
        NEW_CLOSE_TIME_EVEN = make_aware(datetime.datetime(2021, 10, 22, 14, 0, 0, 0))

        self.day.add_or_update_hours(DEFAULT_OPEN_TIME, NEW_CLOSE_TIME)
        # We should now have four blocks, with some extra dangling time at the end
        self.assertEqual(BoothBlock.objects.count(), 3)
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=DEFAULT_CLOSE_TIME,
                booth_block_end_time=NEW_CLOSE_TIME_EVEN,
            )
        )

    def test_update_earlier_close_time_even(self):
        # Case 5 - hours already set. Move the closing hours in.
        # We expect that only one block will remain
        _init_booth_hours(self.day)
        NEW_CLOSE_TIME = DEFAULT_MIDDLE_TIME

        self.day.add_or_update_hours(DEFAULT_OPEN_TIME, NEW_CLOSE_TIME)
        # Confirm that block was removed
        self.assertEqual(BoothBlock.objects.count(), 1)
        self.assertFalse(
            BoothBlock.objects.filter(
                booth_block_start_time=DEFAULT_MIDDLE_TIME,
                booth_block_end_time=DEFAULT_CLOSE_TIME,
            )
        )

    def test_update_earlier_open_time_even(self):
        # Case 6 - hours already set. Make the opening time earlier.
        # We expect a block added on that side
        _init_booth_hours(self.day)
        NEW_OPEN_TIME = make_aware(datetime.datetime(2021, 10, 22, 6, 0, 0, 0))

        self.day.add_or_update_hours(NEW_OPEN_TIME, DEFAULT_CLOSE_TIME)
        # Confirm a block was added
        self.assertEqual(BoothBlock.objects.count(), 3)
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=NEW_OPEN_TIME,
                booth_block_end_time=DEFAULT_OPEN_TIME,
            )
        )

    def test_update_earlier_open_time_odd(self):
        # Case 7 - hours already set. Make the opening time earlier, in an odd increment.
        # We expect one block to be added
        _init_booth_hours(self.day)
        NEW_OPEN_TIME = make_aware(datetime.datetime(2021, 10, 22, 5, 0, 0, 0))
        NEW_OPEN_TIME_EVEN = make_aware(datetime.datetime(2021, 10, 22, 6, 0, 0, 0))

        self.day.add_or_update_hours(NEW_OPEN_TIME, DEFAULT_CLOSE_TIME)
        # Confirm a block was added
        self.assertEqual(BoothBlock.objects.count(), 3)
        self.assertTrue(
            BoothBlock.objects.filter(
                booth_block_start_time=NEW_OPEN_TIME_EVEN,
                booth_block_end_time=DEFAULT_OPEN_TIME,
            )
        )

    def test_update_later_open_time(self):
        # Case 8 - hours already set. Make the opening time later.
        # We expect a block to be deleted to move in
        _init_booth_hours(self.day)
        NEW_OPEN_TIME = DEFAULT_MIDDLE_TIME

        self.day.add_or_update_hours(NEW_OPEN_TIME, DEFAULT_CLOSE_TIME)
        # Confirm a block was removed
        self.assertEqual(BoothBlock.objects.count(), 1)
        self.assertFalse(
            BoothBlock.objects.filter(
                booth_block_start_time=DEFAULT_OPEN_TIME,
                booth_block_end_time=NEW_OPEN_TIME,
            )
        )


class EnableAndDisableDay(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.location = BoothLocation.objects.create()

        cls.day_1 = BoothDay.objects.create(
            booth=cls.location,
            booth_day_date=TEST_DATE,
            booth_day_hours_set=False,
            booth_day_enabled=False,
        )
        cls.day_2 = BoothDay.objects.create(
            booth=cls.location,
            booth_day_date=TEST_DATE_2,
            booth_day_hours_set=False,
            booth_day_enabled=False,
        )

        return super().setUpTestData()

    def test_enable_day(self):
        # Enable one block, keep the other disabled
        # Ensure that the blocks are disabled by default
        self._init_both_booth_hours

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_enabled)

        # Enable day_1, keep day_2 disabled
        self.day_1.enable_day()

        # Make sure all blocks are either enabled or disabled
        for block in BoothBlock.objects.all():
            self.assertTrue(block.booth_block_enabled)
        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_enabled)

    def test_disable_day(self):
        self._init_both_booth_hours

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_enabled)

        # Enable day_1, keep day_2 disabled
        self.day_1.enable_day()

        # Make sure it is enabled
        for block in BoothBlock.objects.all():
            self.assertTrue(block.booth_block_enabled)

        # Disable, then make sure it disabled for all blocks
        self.day_1.disable_day()

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_enabled)

    def _init_both_booth_hours(self):
        # Initialization for booth_hours on both booths
        _init_booth_hours(self.day_1)
        _init_booth_hours(self.day_2)


class EnableAndDisableFFA(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.location = BoothLocation.objects.create()

        cls.day_1 = BoothDay.objects.create(
            booth=cls.location,
            booth_day_date=TEST_DATE,
            booth_day_hours_set=False,
            booth_day_enabled=False,
        )
        cls.day_2 = BoothDay.objects.create(
            booth=cls.location,
            booth_day_date=TEST_DATE_2,
            booth_day_hours_set=False,
            booth_day_enabled=False,
        )

        return super().setUpTestData()

    def test_enable_ffa(self):
        # Enable one block, keep the other disabled
        # Ensure that the blocks are disabled by default
        self._init_both_booth_hours

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_day_freeforall_enabled)

        # Enable day_1, keep day_2 disabled
        self.day_1.enable_freeforall()

        # Make sure all blocks are either enabled or disabled
        for block in BoothBlock.objects.all():
            self.assertTrue(block.booth_day_freeforall_enabled)
        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_day_freeforall_enabled)

    def test_disable_day(self):
        self._init_both_booth_hours

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_day_freeforall_enabled)

        # Enable day_1, keep day_2 disabled
        self.day_1.enable_freeforall()

        # Make sure it is enabled
        for block in BoothBlock.objects.all():
            self.assertTrue(block.booth_day_freeforall_enabled)

        # Disable, then make sure it disabled for all blocks
        self.day_1.disable_freeforall()

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_day_freeforall_enabled)

    def _init_both_booth_hours(self):
        # Initialization for booth_hours on both booths
        _init_booth_hours(self.day_1)
        _init_booth_hours(self.day_2)


def _init_booth_hours(day: BoothDay):
    open_time = DEFAULT_OPEN_TIME
    close_time = DEFAULT_CLOSE_TIME

    day.add_or_update_hours(open_time, close_time)
    return
