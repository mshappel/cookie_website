from django.test import TestCase
from django.utils import timezone

from .models import BoothHours, BoothLocation, BoothDay, BoothBlock

import datetime
import pytz


class BoothBlockTestCase(TestCase):
    def test_reserve_block(self):
        location = BoothLocation.objects.create()
        day = BoothDay.objects.create(booth=location)
        block = BoothBlock.objects.create(booth_day=day,
                                          booth_block_enabled=False)

        troop_id_1 = 5
        troop_id_2 = 6

        # TODO: Add confirmation?

        # Case 1 - block is disabled, trying to reserve
        block.reserve_block(troop_id_1)
        self.assertTrue(block.booth_block_current_troop_owner != troop_id_1)
        self.assertTrue(block.booth_block_reserved == False)

        # Case 2 - block is enabled, allowed to reserve
        block.booth_block_enabled = True
        block.reserve_block(troop_id_1)
        self.assertTrue(block.booth_block_current_troop_owner == troop_id_1)
        self.assertTrue(block.booth_block_reserved == True)

        # Case 3 - block is enabled, already reserved. A new troop cannot reserve it
        block.reserve_block(troop_id_2)
        self.assertTrue(block.booth_block_current_troop_owner == troop_id_1)
        self.assertTrue(block.booth_block_reserved == True)


class BoothDayTestCase(TestCase):
    def test_add_or_update_hours(self):
        # Setup
        location = BoothLocation.objects.create()
        date = datetime.date(2021, 10, 22)

        day = BoothDay.objects.create(booth=location,
                                      booth_day_date=date,
                                      booth_day_hours_set=False,
                                      booth_day_enabled=False)

        open_time = datetime.datetime(2021, 10, 22, 8, 0, 0, 0)
        close_time = datetime.datetime(2021, 10, 22, 12, 0, 0, 0)

        # Pre-conditions - we have no BoothBlocks that have been created
        self.assertTrue(BoothBlock.objects.count() == 0)

        # Case 1 - we have no hours set.
        # We're setting a 4 hour block, so in 2 hour increments, this should result in two blocks created
        day.add_or_update_hours(open_time, close_time)
        self.assertEqual(BoothBlock.objects.count(), 2)
        # One should be 8-10, the other 10-12
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 8, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0)))

        # Case 2 - hours already set. We're moving to hours totally exclusive of the current hours
        # All blocks currently there should be deleted, and we should have two new blocks created
        open_time = datetime.datetime(2021, 10, 22, 14, 0, 0, 0)
        close_time = datetime.datetime(2021, 10, 22, 18, 0, 0, 0)

        day.add_or_update_hours(open_time, close_time)
        # Confirm we still have two blocks present
        self.assertEqual(BoothBlock.objects.count(), 2)
        # And confirm that the time ranges are what we expected - 14-16, 16-18
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 16, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 16, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 18, 0, 0, 0)))

        # Case 3 - hours already set. We're going to extend the closing time. We expect a new block added on the end
        close_time = datetime.datetime(2021, 10, 22, 20, 0, 0, 0)

        day.add_or_update_hours(open_time, close_time)
        # Confirm we now have three blocks
        self.assertEqual(BoothBlock.objects.count(), 3)
        # The existing blocks should not have been modified, and we'll have one new one
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 16, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 16, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 18, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 18, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 20, 0, 0, 0)))

        # Case 4 - hours already set. Extend the closing by a not clean amount (3 hours)
        close_time = datetime.datetime(2021, 10, 22, 23, 0, 0, 0)

        day.add_or_update_hours(open_time, close_time)
        # We should now have four blocks, with some extra dangling time at the end
        self.assertEqual(BoothBlock.objects.count(), 4)
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 20, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 22, 0, 0, 0)))

        # Case 5 - hours already set. Move the closing hours in. We expect that block we added on the end to get deleted
        close_time = datetime.datetime(2021, 10, 22, 21, 0, 0, 0)

        day.add_or_update_hours(open_time, close_time)
        # Confirm that block was removed
        self.assertEqual(BoothBlock.objects.count(), 3)
        self.assertFalse(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 20, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 22, 0, 0, 0)))

        # Case 6 - hours already set. Make the opening time earlier. We expect a block added on that side
        open_time = datetime.datetime(2021, 10, 22, 12, 0, 0, 0)

        day.add_or_update_hours(open_time, close_time)
        # Confirm a block was added
        self.assertEqual(BoothBlock.objects.count(), 4)
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 14, 0, 0, 0)))

        # Case 7 - hours already set. Make the opening time earlier, in an odd increment. We expect one block to be added
        open_time = datetime.datetime(2021, 10, 22, 9, 0, 0, 0)

        day.add_or_update_hours(open_time, close_time)
        # Confirm a block was added
        self.assertEqual(BoothBlock.objects.count(), 5)
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0)))

        # Case 8 - hours already set. Make the opening time later. We expect a block to be deleted to move in
        open_time = datetime.datetime(2021, 10, 22, 11, 0, 0, 0)

        day.add_or_update_hours(open_time, close_time)
        # Confirm a block was removed
        self.assertEqual(BoothBlock.objects.count(), 4)
        self.assertFalse(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0)))

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

        open_time_1 = datetime.datetime(2021, 10, 22, 8, 0, 0, 0)
        close_time_1 = datetime.datetime(2021, 10, 22, 12, 0, 0, 0)

        day_1.add_or_update_hours(open_time_1, close_time_1)

        open_time_2 = datetime.datetime(2021, 10, 23, 8, 0, 0, 0)
        close_time_2 = datetime.datetime(2021, 10, 23, 12, 0, 0, 0)

        day_2.add_or_update_hours(open_time_2, close_time_2)

        # Verify that they are all disabled by default
        self.assertFalse(day_1.booth_day_enabled)
        self.assertFalse(day_2.booth_day_enabled)
        self.assertFalse(day_1.booth_day_freeforall_enabled)
        self.assertFalse(day_2.booth_day_freeforall_enabled)

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_enabled)
            self.assertFalse(block.booth_block_freeforall_enabled)

        # Enable blocks for this location up until and including day_1
        day_1.enable_day()

        self.assertTrue(day_1.booth_day_enabled)
        self.assertFalse(day_2.booth_day_enabled)
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

        self.assertFalse(day_1.booth_day_enabled)
        self.assertFalse(day_2.booth_day_enabled)
        self.assertFalse(day_1.booth_day_freeforall_enabled)
        self.assertFalse(day_2.booth_day_freeforall_enabled)

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_enabled)
            self.assertFalse(block.booth_block_freeforall_enabled)

        # Enabling FFA will enable the booth blocks and FFA
        day_1.enable_freeforall()

        self.assertTrue(day_1.booth_day_enabled)
        self.assertFalse(day_2.booth_day_enabled)
        self.assertTrue(day_1.booth_day_freeforall_enabled)
        self.assertFalse(day_2.booth_day_freeforall_enabled)

        for block in BoothBlock.objects.filter(booth_day=day_1):
            self.assertTrue(block.booth_block_enabled)
            self.assertTrue(block.booth_block_freeforall_enabled)
        for block in BoothBlock.objects.filter(booth_day=day_2):
            self.assertFalse(block.booth_block_enabled)
            self.assertFalse(block.booth_block_freeforall_enabled)

        # Disabling FFA will disable blocks and FFA
        day_1.disable_freeforall()

        self.assertFalse(day_1.booth_day_enabled)
        self.assertFalse(day_2.booth_day_enabled)
        self.assertFalse(day_1.booth_day_freeforall_enabled)
        self.assertFalse(day_2.booth_day_freeforall_enabled)

        for block in BoothBlock.objects.all():
            self.assertFalse(block.booth_block_enabled)
            self.assertFalse(block.booth_block_freeforall_enabled)


class BoothLocationTestCase(TestCase):
    def test_add_or_update_day(self):
        # The block creation was tested up in BoothDayTestCase.
        # But this is just testing that this all cascades down properly from BoothLocation - creating a day,
        # which in turn should create a number of blocks
        location = BoothLocation.objects.create(booth_location="Walmart",
                                                booth_address="123 Feels Pretty Good Kay St",
                                                booth_enabled=False,
                                                booth_is_golden_ticket=False,
                                                booth_requires_masks=True,
                                                booth_is_outside=True,
                                                booth_notes="You can sell cookies here")

        date = datetime.datetime(2021, 10, 22)
        date_open_time = datetime.datetime(2021, 10, 22, 8, 0, 0, 0)
        date_close_time = datetime.datetime(2021, 10, 22, 12, 0, 0, 0)

        # Case 1 - Try adding a date with hours
        location.add_or_update_day(date, date_open_time, date_close_time)

        # Confirm what was constructed as a result.
        # One BoothDay, with the open and close times we have specified
        self.assertEqual(BoothDay.objects.count(), 1)
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=date,
                                    booth_day_hours_set=True,
                                    booth_day_open_time=date_open_time,
                                    booth_day_close_time=date_close_time))

        # Two BoothBlocks, based on the open/close times
        self.assertEqual(BoothBlock.objects.count(), 2)

        # Case 2 - Edit the exiting date with updated open/close times
        # We want to confirm the existing day was updated and a new one was not created
        date_open_time = datetime.datetime(2021, 10, 22, 6, 0, 0, 0)
        location.add_or_update_day(date, date_open_time, date_close_time)

        # Confirm the updates - one BoothDay still, with the parameters we expect. 3 BoothBlocks
        self.assertEqual(BoothDay.objects.count(), 1)
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=date,
                                    booth_day_hours_set=True,
                                    booth_day_open_time=date_open_time,
                                    booth_day_close_time=date_close_time))
        self.assertEqual(BoothBlock.objects.count(), 3)

        # Case 3 - add a new date. Confirm it was added separately
        date = datetime.datetime(2021, 10, 23)
        location.add_or_update_day(date, date_open_time, date_close_time)

        # Confirm we now have two days, and six blocks (3 for each day)
        self.assertEqual(BoothDay.objects.count(), 2)
        self.assertEqual(BoothBlock.objects.count(), 6)

    def test_set_or_update_hours(self):
        # This tests setting or updating complex hour schedules for a location, and making sure days and blocks are
        # updated correctly
        location = BoothLocation.objects.create(booth_location="Walmart",
                                                booth_address="123 Feels Pretty Good Kay St",
                                                booth_enabled=False,
                                                booth_is_golden_ticket=False,
                                                booth_requires_masks=True,
                                                booth_is_outside=True,
                                                booth_notes="You can sell cookies here")

        # We're going to create a two week hours block.
        # Starting from Sunday, October 17, 2021 until Saturday, October 30, 2021.
        # The business will be open on Sunday and Saturday, 12pm to 5pm
        open_date = datetime.datetime(2021, 10, 17, 0, 0, 0, 0)
        close_date = datetime.datetime(2021, 10, 30, 0, 0, 0, 0)

        open_time = datetime.time(12, 0, 0, 0)
        close_time = datetime.time(17, 0, 0, 0)

        hours = BoothHours.objects.get(booth_location=location)
        hours.booth_start_date = open_date
        hours.booth_end_date = close_date
        hours.sunday_open = True
        hours.sunday_open_time = open_time
        hours.sunday_close_time = close_time
        hours.saturday_open = True
        hours.saturday_open_time = open_time
        hours.saturday_close_time = close_time

        # Saving the hours will trigger the location to update its days/blocks
        hours.save()

        # We should see four days generated over the two week period:
        # Saturday, October 23/30
        # Sunday, October 17/24
        self.assertEqual(BoothDay.objects.count(), 4)

        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=datetime.datetime(2021, 10, 17, 0, 0, 0, 0)))
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=datetime.datetime(2021, 10, 23, 0, 0, 0, 0)))
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=datetime.datetime(2021, 10, 24, 0, 0, 0, 0)))
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=datetime.datetime(2021, 10, 30, 0, 0, 0, 0)))

        # We'd expect 2 blocks per day to be generated, so 8 blocks total
        # Each day will have a 12-2pm, and a 2pm-4pm block
        self.assertEqual(BoothBlock.objects.count(), 8)
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 17, 12, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 17, 14, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 17, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 17, 16, 0, 0, 0)))

        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 23, 12, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 23, 14, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 23, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 23, 16, 0, 0, 0)))

        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 24, 12, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 24, 14, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 24, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 24, 16, 0, 0, 0)))

        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 30, 12, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 30, 14, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 30, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 30, 16, 0, 0, 0)))

        # NOW, update the open/close dates, as well as hours and make sure everything updates okay.
        # Shifting from
        # Sunday, October 17 to Saturday, October 30, to
        # Sunday, October 24 to Saturday, November 6
        open_date = datetime.datetime(2021, 10, 24, 0, 0, 0, 0)
        close_date = datetime.datetime(2021, 11, 6, 0, 0, 0, 0)

        # Hours will change from 12-5pm to 2pm-6pm
        open_time = datetime.time(14, 0, 0, 0)
        close_time = datetime.time(18, 0, 0, 0)

        hours.booth_start_date = open_date
        hours.booth_end_date = close_date
        hours.sunday_open = True
        hours.sunday_open_time = open_time
        hours.sunday_close_time = close_time
        hours.saturday_open = True
        hours.saturday_open_time = open_time
        hours.saturday_close_time = close_time

        # Saving the hours will trigger the location to update its days/blocks
        hours.save()

        # We should still only have 4 days, but they have shifted one week
        # Saturday, October 30/November 6
        # Sunday, October 24/31
        self.assertEqual(BoothDay.objects.count(), 4)
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=datetime.datetime(2021, 10, 24, 0, 0, 0, 0)))
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=datetime.datetime(2021, 10, 30, 0, 0, 0, 0)))
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=datetime.datetime(2021, 10, 31, 0, 0, 0, 0)))
        self.assertTrue(
            BoothDay.objects.filter(booth_day_date=datetime.datetime(2021, 11, 6, 0, 0, 0, 0)))

        # We'll still only have two blocks per day, but they've shifted by two hours
        self.assertEqual(BoothBlock.objects.count(), 8)
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 24, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 24, 16, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 24, 16, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 24, 18, 0, 0, 0)))

        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 30, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 30, 16, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 30, 16, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 30, 18, 0, 0, 0)))

        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 31, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 31, 16, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 31, 16, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 10, 31, 18, 0, 0, 0)))

        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 11, 6, 14, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 11, 6, 16, 0, 0, 0)))
        self.assertTrue(
            BoothBlock.objects.filter(booth_block_start_time=datetime.datetime(2021, 11, 6, 16, 0, 0, 0),
                                      booth_block_end_time=datetime.datetime(2021, 11, 6, 18, 0, 0, 0)))
