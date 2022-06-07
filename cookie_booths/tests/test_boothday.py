from email.policy import default
from django.test import TestCase
from django.utils.timezone import make_aware

from cookie_booths.models import BoothLocation, BoothDay, BoothBlock

import datetime


class AddOrUpdateHours(TestCase):
    
    TEST_DATE = datetime.date(2021, 10, 22)
    DEFAULT_OPEN_TIME = make_aware(datetime.datetime(2021, 10, 22, 8, 0, 0, 0))
    DEFAULT_MIDDLE_TIME = make_aware(datetime.datetime(2021, 10, 22, 10, 0, 0, 0))
    DEFAULT_CLOSE_TIME = make_aware(datetime.datetime(2021, 10, 22, 12, 0, 0, 0))
    
    @classmethod
    def setUpTestData(cls) -> None:
        cls.location = BoothLocation.objects.create()
        
        cls.day = BoothDay.objects.create(booth=cls.location,
                                          booth_day_date=cls.TEST_DATE,
                                          booth_day_hours_set=False,
                                          booth_day_enabled=False)

        return super().setUpTestData()
    
    def test_pre_condition(self):
        self.assertEqual(BoothBlock.objects.count(), 0)
       
    def test_add_with_no_hours_set(self):
        # Case 1 - we have no hours set.
        # Set booth time for 4 hours, results in 2 booths created (booth are 2 hours each)

        self._init_booth_hours()
        self.assertTrue(self.day.booth_day_hours_set)
        self.assertEqual(BoothBlock.objects.count(), 2)
        
        # One should be 8-10, the other 10-12
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=self.DEFAULT_OPEN_TIME,
                                                  booth_block_end_time=self.DEFAULT_MIDDLE_TIME))
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=self.DEFAULT_MIDDLE_TIME,
                                                  booth_block_end_time=self.DEFAULT_CLOSE_TIME))

    def test_update_open_and_close_time(self):
        # Case 2 - hours already set. We're moving to hours totally exclusive of the current hours
        # All blocks currently there should be deleted, and we should have two new blocks created
        self._init_booth_hours()
        
        # Change hours
        NEW_OPEN_TIME = make_aware(datetime.datetime(2021, 10, 22, 14, 0, 0, 0))
        NEW_CLOSE_TIME = make_aware(datetime.datetime(2021, 10, 22, 18, 0, 0, 0))
        NEW_MIDDLE_TIME = make_aware(datetime.datetime(2021, 10, 22, 16, 0, 0, 0))

        self.day.add_or_update_hours(NEW_OPEN_TIME, NEW_CLOSE_TIME)

        # Confirm we still have two blocks present
        self.assertEqual(BoothBlock.objects.count(), 2)

        # And confirm that the time ranges are what we expected - 14-16, 16-18
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=NEW_OPEN_TIME,
                                                  booth_block_end_time=NEW_MIDDLE_TIME))
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=NEW_MIDDLE_TIME,
                                                  booth_block_end_time=NEW_CLOSE_TIME))
    
    def test_update_later_close_time_even(self):
        # Case 3 - hours already set. We're going to extend the closing time. 
        # We expect a new block added on the end
        self._init_booth_hours()
        
        NEW_CLOSE_TIME = make_aware(datetime.datetime(2021, 10, 22, 14, 0, 0, 0))
        self.day.add_or_update_hours(self.DEFAULT_OPEN_TIME, NEW_CLOSE_TIME)

        # Confirm we now have three blocks
        self.assertEqual(BoothBlock.objects.count(), 3)
        
        # The existing blocks should not have been modified, and we'll have one new one
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=self.DEFAULT_OPEN_TIME,
                                                  booth_block_end_time=self.DEFAULT_MIDDLE_TIME))
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=self.DEFAULT_MIDDLE_TIME,
                                                  booth_block_end_time=self.DEFAULT_CLOSE_TIME))
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=self.DEFAULT_CLOSE_TIME,
                                                  booth_block_end_time=NEW_CLOSE_TIME))        
    
    def test_update_later_close_time_odd(self):
        # Case 4 - hours already set. Extend the closing by a not clean amount (3 hours)
        self._init_booth_hours()
        NEW_CLOSE_TIME = make_aware(datetime.datetime(2021, 10, 22, 15, 0, 0, 0))
        NEW_CLOSE_TIME_EVEN = make_aware(datetime.datetime(2021, 10, 22, 14, 0, 0, 0))

        self.day.add_or_update_hours(self.DEFAULT_OPEN_TIME, NEW_CLOSE_TIME)
        # We should now have four blocks, with some extra dangling time at the end
        self.assertEqual(BoothBlock.objects.count(), 3)
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=self.DEFAULT_CLOSE_TIME,
                                                  booth_block_end_time=NEW_CLOSE_TIME_EVEN))

    def test_update_earlier_close_time_even(self):
        # Case 5 - hours already set. Move the closing hours in. 
        # We expect that only one block will remain
        self._init_booth_hours()
        NEW_CLOSE_TIME = self.DEFAULT_MIDDLE_TIME

        self.day.add_or_update_hours(self.DEFAULT_OPEN_TIME, NEW_CLOSE_TIME)
        # Confirm that block was removed
        self.assertEqual(BoothBlock.objects.count(), 1)
        self.assertFalse(BoothBlock.objects.filter(booth_block_start_time=self.DEFAULT_MIDDLE_TIME,
                                                   booth_block_end_time=self.DEFAULT_CLOSE_TIME))

    def test_update_earlier_open_time_even(self):
        # Case 6 - hours already set. Make the opening time earlier. 
        # We expect a block added on that side
        self._init_booth_hours()
        NEW_OPEN_TIME = make_aware(datetime.datetime(2021, 10, 22, 6, 0, 0, 0))

        self.day.add_or_update_hours(NEW_OPEN_TIME, self.DEFAULT_CLOSE_TIME)
        # Confirm a block was added
        self.assertEqual(BoothBlock.objects.count(), 3)
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=NEW_OPEN_TIME,
                                                  booth_block_end_time=self.DEFAULT_OPEN_TIME))

    def test_update_earlier_open_time_odd(self):
        # Case 7 - hours already set. Make the opening time earlier, in an odd increment. 
        # We expect one block to be added
        self._init_booth_hours()
        NEW_OPEN_TIME = make_aware(datetime.datetime(2021, 10, 22, 5, 0, 0, 0))
        NEW_OPEN_TIME_EVEN = make_aware(datetime.datetime(2021, 10, 22, 6, 0, 0, 0))

        self.day.add_or_update_hours(NEW_OPEN_TIME, self.DEFAULT_CLOSE_TIME)
        # Confirm a block was added
        self.assertEqual(BoothBlock.objects.count(), 3)
        self.assertTrue(BoothBlock.objects.filter(booth_block_start_time=NEW_OPEN_TIME_EVEN,
                                                  booth_block_end_time=self.DEFAULT_OPEN_TIME))
    
    def test_update_later_open_time(self):
        # Case 8 - hours already set. Make the opening time later. 
        # We expect a block to be deleted to move in
        self._init_booth_hours()
        NEW_OPEN_TIME = self.DEFAULT_MIDDLE_TIME

        self.day.add_or_update_hours(NEW_OPEN_TIME, self.DEFAULT_CLOSE_TIME)
        # Confirm a block was removed
        self.assertEqual(BoothBlock.objects.count(), 1)
        self.assertFalse(
            BoothBlock.objects.filter(booth_block_start_time=self.DEFAULT_OPEN_TIME,
                                      booth_block_end_time=NEW_OPEN_TIME))

    def _init_booth_hours(self):
        open_time = self.DEFAULT_OPEN_TIME
        close_time = self.DEFAULT_CLOSE_TIME

        self.day.add_or_update_hours(open_time, close_time)
        return


class EnableDayFFA(TestCase):

    def test_enable_day_ffa(self):
        # Testing that enable_day, disable_day, enable_freeforall, disable_freeforall work as expected
        # Setup - two dates for a location, with the same time
        location = BoothLocation.objects.create()
        date_1 = datetime.date(2021, 10, 22)
        date_2 = datetime.date(2021, 10, 23)

        day_1 = BoothDay.objects.create(booth=location,
                                        booth_day_date=date_1,
                                        booth_day_hours_set=False,
                                        booth_day_enabled=False)
        day_2 = BoothDay.objects.create(booth=location,
                                        booth_day_date=date_2,
                                        booth_day_hours_set=False,
                                        booth_day_enabled=False)

        open_time_1 = make_aware(datetime.datetime(2021, 10, 22, 8, 0, 0, 0))
        close_time_1 = make_aware(datetime.datetime(2021, 10, 22, 12, 0, 0, 0))

        day_1.add_or_update_hours(open_time_1, close_time_1)

        open_time_2 = make_aware(datetime.datetime(2021, 10, 23, 8, 0, 0, 0))
        close_time_2 = make_aware(datetime.datetime(2021, 10, 23, 12, 0, 0, 0))

        day_2.add_or_update_hours(open_time_2, close_time_2)

        # Verify that they are all disabled by default
        self.assertFalse(day_1.booth_day_freeforall_enabled)
        self.assertFalse(day_2.booth_day_freeforall_enabled)

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_enabled)
            self.assertFalse(block.booth_block_freeforall_enabled)

        # Enable blocks for this location up until and including day_1
        day_1.enable_day()

        self.assertFalse(day_1.booth_day_freeforall_enabled)
        self.assertFalse(day_2.booth_day_freeforall_enabled)

        for block in BoothBlock.objects.filter(booth_day=day_1):
            self.assertTrue(block.booth_block_enabled)
            self.assertFalse(block.booth_block_freeforall_enabled)
        for block in BoothBlock.objects.filter(booth_day=day_2):
            self.assertFalse(block.booth_block_enabled)
            self.assertFalse(block.booth_block_freeforall_enabled)

        # Disabling should disable all of the associated blocks
        day_1.disable_day()

        self.assertFalse(day_1.booth_day_freeforall_enabled)
        self.assertFalse(day_2.booth_day_freeforall_enabled)

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_enabled)
            self.assertFalse(block.booth_block_freeforall_enabled)

        # Enabling FFA will enable the booth blocks and FFA
        day_1.enable_freeforall()

        self.assertTrue(day_1.booth_day_freeforall_enabled)
        self.assertFalse(day_2.booth_day_freeforall_enabled)

        for block in BoothBlock.objects.filter(booth_day=day_1):
            self.assertTrue(block.booth_block_freeforall_enabled)
        for block in BoothBlock.objects.filter(booth_day=day_2):
            self.assertFalse(block.booth_block_freeforall_enabled)

        # Disabling FFA will disable blocks and FFA
        day_1.disable_freeforall()

        self.assertFalse(day_1.booth_day_freeforall_enabled)
        self.assertFalse(day_2.booth_day_freeforall_enabled)

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_freeforall_enabled)