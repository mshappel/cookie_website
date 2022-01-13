import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from .models import Troop, TroopTicketParameters
from cookie_booths.models import BoothLocation, BoothDay, BoothBlock


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
