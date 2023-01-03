# Troop Model Tests
from troops.tests.troop_class_reference import TroopTestCase


class TroopModelTestCase(TroopTestCase):

    def test_troop_model(self):
        # Validate the database contains the expected data

        # Normal
        self.assertEqual(self.small_troop.troop_number, self.SMALL_TROOP["number"])
        self.assertEqual(
            self.small_troop.troop_cookie_coordinator, self.SMALL_TROOP["tcc"]
        )
        self.assertEqual(self.small_troop.troop_level, self.SMALL_TROOP["level"])
        self.assertEqual(self.small_troop.troop_size, self.SMALL_TROOP["troop_size"])
        self.assertEqual(
            self.small_troop.total_booth_tickets_per_week,
            self.ticket_parameters.get_small_troop_total_tickets_per_week,
        )
        self.assertEqual(
            self.small_troop.booth_golden_tickets_per_week,
            self.ticket_parameters.get_small_troop_golden_tickets_per_week,
        )

        # Super
        self.assertEqual(self.medium_troop.troop_number, self.MEDIUM_TROOP["number"])
        self.assertEqual(
            self.medium_troop.troop_cookie_coordinator, self.MEDIUM_TROOP["tcc"]
        )
        self.assertEqual(self.medium_troop.troop_level, self.MEDIUM_TROOP["level"])
        self.assertEqual(self.medium_troop.troop_size, self.MEDIUM_TROOP["troop_size"])
        self.assertEqual(
            self.medium_troop.total_booth_tickets_per_week,
            self.ticket_parameters.get_medium_troop_total_tickets_per_week,
        )
        self.assertEqual(
            self.medium_troop.booth_golden_tickets_per_week,
            self.ticket_parameters.get_medium_troop_golden_tickets_per_week,
        )
