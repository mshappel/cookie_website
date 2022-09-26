# Troop Model Tests
from troops.models import TicketParameters
from troops.tests.troop_class_reference import TroopTestCase


SMALL_TROOP_GOLDEN_TICKETS_PER_WEEK = TicketParameters.SMALL_TROOP_GOLDEN_TICKETS_PER_WEEK
MEDIUM_TROOP_GOLDEN_TICKETS_PER_WEEK = TicketParameters.MEDIUM_TROOP_GOLDEN_TICKETS_PER_WEEK
LARGE_TROOP_GOLDEN_TICKETS_PER_WEEK = TicketParameters.LARGE_TROOP_GOLDEN_TICKETS_PER_WEEK

SMALL_TROOP_TOTAL_TICKETS_PER_WEEK = TicketParameters.SMALL_TROOP_TOTAL_TICKETS_PER_WEEK
MEDIUM_TROOP_TOTAL_TICKETS_PER_WEEK = TicketParameters.MEDIUM_TROOP_TOTAL_TICKETS_PER_WEEK
LARGE_TROOP_TOTAL_TICKETS_PER_WEEK = TicketParameters.LARGE_TROOP_TOTAL_TICKETS_PER_WEEK
    
class TroopModelTestCase(TroopTestCase):    
    def test_troop_model(self):
        # Validate the database contains the expected data

        # Normal
        self.assertEqual(self.small_troop.troop_number, self.SMALL_TROOP['number'])
        self.assertEqual(self.small_troop.troop_cookie_coordinator, self.SMALL_TROOP['tcc'])
        self.assertEqual(self.small_troop.troop_level, self.SMALL_TROOP['level'])
        self.assertEqual(self.small_troop.troop_size, self.SMALL_TROOP['troop_size'])
        self.assertEqual(self.small_troop.total_booth_tickets_per_week, SMALL_TROOP_TOTAL_TICKETS_PER_WEEK)
        self.assertEqual(self.small_troop.booth_golden_tickets_per_week, SMALL_TROOP_GOLDEN_TICKETS_PER_WEEK)

        # Super
        self.assertEqual(self.medium_troop.troop_number, self.MEDIUM_TROOP['number'])
        self.assertEqual(self.medium_troop.troop_cookie_coordinator, self.MEDIUM_TROOP['tcc'])
        self.assertEqual(self.medium_troop.troop_level, self.MEDIUM_TROOP['level'])
        self.assertEqual(self.medium_troop.troop_size, self.MEDIUM_TROOP['troop_size'])
        self.assertEqual(self.medium_troop.total_booth_tickets_per_week, MEDIUM_TROOP_TOTAL_TICKETS_PER_WEEK)
        self.assertEqual(self.medium_troop.booth_golden_tickets_per_week, MEDIUM_TROOP_GOLDEN_TICKETS_PER_WEEK)