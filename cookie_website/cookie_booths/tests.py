from django.test import TestCase
from django.utils import timezone

from cookie_booths.models import Booth_Location, Booth_Day, Booth_Block

import datetime
import pytz

class BoothBlockTestCase(TestCase):
    def test_reserve_block(self):
        location = Booth_Location.objects.create()
        day = Booth_Day.objects.create(booth=location)
        block = Booth_Block.objects.create(booth_day=day, \
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
        location = Booth_Location.objects.create()
        date = datetime.date(2021, 10, 22)

        day = Booth_Day.objects.create(booth=location, \
                                       booth_day_date=date, \
                                       booth_day_hours_set=False, \

                                       booth_day_enabled=False)

        open_time = datetime.datetime(2021, 10, 22, 8, 0, 0, 0, pytz.UTC)
        close_time = datetime.datetime(2021, 10, 22, 12, 0, 0, 0, pytz.UTC)

        # Pre-conditions - we have no Booth_Blocks that have been created
        self.assertTrue(Booth_Block.objects.count() == 0)

        # Case 1 - we have no hours set.
        # We're setting a 4 hour block, so in 2 hour increments, this should result in two blocks created
        day.add_or_update_hours(open_time, close_time)
        self.assertEqual(Booth_Block.objects.count(), 2)
        # One should be 8-10, the other 10-12
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 8, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0, pytz.UTC)))
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0, pytz.UTC)))

        # Case 2 - hours already set. We're moving to hours totally exclusive of the current hours
        # All blocks currently there should be deleted, and we should have two new blocks created
        open_time = datetime.datetime(2021, 10, 22, 14, 0, 0, 0, pytz.UTC)
        close_time = datetime.datetime(2021, 10, 22, 18, 0, 0, 0, pytz.UTC)

        day.add_or_update_hours(open_time, close_time)
        # Confirm we still have two blocks present
        self.assertEqual(Booth_Block.objects.count(), 2)
        # And confirm that the time ranges are what we expected - 14-16, 16-18
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 14, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 16, 0, 0, 0, pytz.UTC)))
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 16, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 18, 0, 0, 0, pytz.UTC)))

        # Case 3 - hours already set. We're going to extend the closing time. We expect a new block added on the end
        close_time = datetime.datetime(2021, 10, 22, 20, 0, 0, 0, pytz.UTC)

        day.add_or_update_hours(open_time, close_time)
        # Confirm we now have three blocks
        self.assertEqual(Booth_Block.objects.count(), 3)
        # The existing blocks should not have been modified, and we'll have one new one
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 14, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 16, 0, 0, 0, pytz.UTC)))
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 16, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 18, 0, 0, 0, pytz.UTC)))
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 18, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 20, 0, 0, 0, pytz.UTC)))

        # Case 4 - hours already set. Extend the closing by a not clean amount (3 hours)
        close_time = datetime.datetime(2021, 10, 22, 23, 0, 0, 0, pytz.UTC)

        day.add_or_update_hours(open_time, close_time)
        # We should now have four blocks, with some extra dangling time at the end
        self.assertEqual(Booth_Block.objects.count(), 4)
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 20, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 22, 0, 0, 0, pytz.UTC)))

        # Case 5 - hours already set. Move the closing hours in. We expect that block we added on the end to get deleted
        close_time = datetime.datetime(2021, 10, 22, 21, 0, 0, 0, pytz.UTC)

        day.add_or_update_hours(open_time, close_time)
        # Confirm that block was removed
        self.assertEqual(Booth_Block.objects.count(), 3)
        self.assertFalse(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 20, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 22, 0, 0, 0, pytz.UTC)))

        # Case 6 - hours already set. Make the opening time earlier. We expect a block added on that side
        open_time = datetime.datetime(2021, 10, 22, 12, 0, 0, 0, pytz.UTC)

        day.add_or_update_hours(open_time, close_time)
        # Confirm a block was added
        self.assertEqual(Booth_Block.objects.count(), 4)
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 14, 0, 0, 0, pytz.UTC)))

        # Case 7 - hours already set. Make the opening time earlier, in an odd increment. We expect one block to be added
        open_time = datetime.datetime(2021, 10, 22, 9, 0, 0, 0, pytz.UTC)

        day.add_or_update_hours(open_time, close_time)
        # Confirm a block was added
        self.assertEqual(Booth_Block.objects.count(), 5)
        self.assertTrue(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0, pytz.UTC)))

        # Case 8 - hours already set. Make the opening time later. We expect a block to be deleted to move in
        open_time = datetime.datetime(2021, 10, 22, 11, 0, 0, 0, pytz.UTC)

        day.add_or_update_hours(open_time, close_time)
        # Confirm a block was removed
        self.assertEqual(Booth_Block.objects.count(), 4)
        self.assertFalse(
            Booth_Block.objects.filter(booth_block_start_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0, pytz.UTC), \
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0, pytz.UTC)))

class BoothLocationTestCase(TestCase):
    def test_add_or_update_day(self):
        # The block creation was tested up in BoothDayTestCase.
        # But this is just testing that this all cascades down properly from Booth_Location - creating a day,
        # which in turn should create a number of blocks
        location = Booth_Location.objects.create(booth_location="Walmart", \
                                                 booth_address="123 Feels Pretty Good Kay St", \
                                                 booth_enabled=False, \
                                                 booth_is_golden_ticket=False, \
                                                 booth_requires_masks=True, \
                                                 booth_is_outside=True,
                                                 booth_notes="You can sell cookies here")

        date = datetime.datetime(2021, 10, 22)
        date_open_time = datetime.datetime(2021, 10, 22, 8, 0, 0, 0, pytz.UTC)
        date_close_time = datetime.datetime(2021, 10, 22, 12, 0, 0, 0, pytz.UTC)

        # Case 1 - Try adding a date with hours
        location.add_or_update_day(date, date_open_time, date_close_time)

        # Confirm what was constructed as a result.
        # One Booth_Day, with the open and close times we have specified
        self.assertEqual(Booth_Day.objects.count(), 1)
        self.assertTrue(
            Booth_Day.objects.filter(booth_day_date=date, \
                                     booth_day_hours_set=True, \
                                     booth_day_open_time=date_open_time, \
                                     booth_day_close_time=date_close_time))

        # Two Booth_Blocks, based on the open/close times
        self.assertEqual(Booth_Block.objects.count(), 2)

        # Case 2 - Edit the exiting date with updated open/close times
        # We want to confirm the existing day was updated and a new one was not created
        date_open_time = datetime.datetime(2021, 10, 22, 6, 0, 0, 0, pytz.UTC)
        location.add_or_update_day(date, date_open_time, date_close_time)

        # Confirm the updates - one Booth_Day still, with the parameters we expect. 3 Booth_Blocks
        self.assertEqual(Booth_Day.objects.count(), 1)
        self.assertTrue(
            Booth_Day.objects.filter(booth_day_date=date, \
                                     booth_day_hours_set=True, \
                                     booth_day_open_time=date_open_time, \
                                     booth_day_close_time=date_close_time))
        self.assertEqual(Booth_Block.objects.count(), 3)

        # Case 3 - add a new date. Confirm it was added separately
        date = datetime.datetime(2021, 10, 23)
        location.add_or_update_day(date, date_open_time, date_close_time)

        # Confirm we now have two days, and six blocks (3 for each day)
        self.assertEqual(Booth_Day.objects.count(), 2)
        self.assertEqual(Booth_Block.objects.count(), 6)


