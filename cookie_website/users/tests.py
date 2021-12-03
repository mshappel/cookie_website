from datetime import date, datetime
from django.test import TestCase

from .models import Troop, TroopTicketParameters
from cookie_booths.models import BoothLocation, BoothDay, BoothBlock

import datetime
import pytz

# Create your tests here.
class TroopTestCase(TestCase):
    def test_ticket_allocation(self):
        normal_troop = Troop.objects.create(troop_number=3)
        super_troop = Troop.objects.create(troop_number=4,
                                           super_troop=True)

        # Validate the ticket allocation of both
        self.assertTrue(normal_troop.total_booth_tickets_per_week ==
                        TroopTicketParameters.NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK)
        self.assertTrue(normal_troop.booth_golden_tickets_per_week ==
                        TroopTicketParameters.NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK)

        self.assertTrue(super_troop.total_booth_tickets_per_week ==
                        TroopTicketParameters.SUPER_TROOP_TOTAL_TICKETS_PER_WEEK)
        self.assertTrue(super_troop.booth_golden_tickets_per_week ==
                        TroopTicketParameters.SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK)

        # Now create a booth day to test around - First a golden ticket
        golden_location = BoothLocation.objects.create()
        date = datetime.date(2021, 10, 22)

        golden_day = BoothDay.objects.create(booth=golden_location,
                                             booth_day_date=date,
                                             booth_day_hours_set=False,
                                             booth_day_enabled=True,
                                             booth_day_is_golden=True)

        # Going to allocate 5 blocks on this day
        open_time = datetime.datetime(2021, 10, 22, 4, 0, 0, 0)
        close_time = datetime.datetime(2021, 10, 22, 14, 0, 0, 0)
        golden_day.add_or_update_hours(open_time, close_time)

        # Now add our normal troop to one block (its golden ticket max), two for the super troop
        block = BoothBlock.objects.get(booth_day=golden_day,
                                       booth_block_start_time=datetime.datetime(2021, 10, 22, 8, 0, 0, 0),
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0))
        block.reserve_block(normal_troop.troop_number)

        block = BoothBlock.objects.get(booth_day=golden_day,
                                       booth_block_start_time=datetime.datetime(2021, 10, 22, 10, 0, 0, 0),
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0))
        block.reserve_block(super_troop.troop_number)

        block = BoothBlock.objects.get(booth_day=golden_day,
                                       booth_block_start_time=datetime.datetime(2021, 10, 22, 12, 0, 0, 0),
                                       booth_block_end_time=datetime.datetime(2021, 10, 22, 14, 0, 0, 0))
        block.reserve_block(super_troop.troop_number)

        # Now confirm the adds have been reflected in our counts that week
        self.assertTrue(
            normal_troop.get_num_tickets_remaining(datetime.date(2021, 10, 18), datetime.date(2021, 10, 24)) == (4,0))
        self.assertTrue(
            super_troop.get_num_tickets_remaining(datetime.date(2021, 10, 18), datetime.date(2021, 10, 24)) == (8,0))

        # Make sure the counts are still ok for a different week
        self.assertTrue(
            normal_troop.get_num_tickets_remaining(datetime.date(2021, 10, 25), datetime.date(2021, 10, 31)) == (5,1))
        self.assertTrue(
            super_troop.get_num_tickets_remaining(datetime.date(2021, 10, 25), datetime.date(2021, 10, 31)) == (10,2))

        # Now let's create a day sometime in that next week, at a normal location, same hours
        normal_location = BoothLocation.objects.create()
        date = datetime.date(2021, 10, 28)

        normal_day = BoothDay.objects.create(booth=normal_location,
                                             booth_day_date=date,
                                             booth_day_hours_set=False,
                                             booth_day_enabled=True)

        normal_day.add_or_update_hours(open_time, close_time)

        # Add all of these blocks to our normal troop
        for block in BoothBlock.objects.filter(booth_day=normal_day):
            block.reserve_block(normal_troop.troop_number)

        # Double check that the counts for the original week have not changed
        self.assertTrue(
            normal_troop.get_num_tickets_remaining(datetime.date(2021, 10, 18), datetime.date(2021, 10, 24)) == (4, 0))
        self.assertTrue(
            super_troop.get_num_tickets_remaining(datetime.date(2021, 10, 18), datetime.date(2021, 10, 24)) == (8, 0))

        # And then make sure the counts for the new week have
        self.assertTrue(
            normal_troop.get_num_tickets_remaining(datetime.date(2021, 10, 25), datetime.date(2021, 10, 31)) == (0, 1))
        self.assertTrue(
            super_troop.get_num_tickets_remaining(datetime.date(2021, 10, 25), datetime.date(2021, 10, 31)) == (10, 2))

