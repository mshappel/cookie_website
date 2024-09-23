from typing import TYPE_CHECKING

from django.db import models

from accounts.models import AccountType
from utils.date_utils import get_one_week_ago

if TYPE_CHECKING:
    from cookie_booths.models.reservations import BoothReservation
    from troops.models import Troop


class BoothReservationManager(models.Manager):
    def has_cookie_captain_reservation(self, time_block):
        """
        Checks if there is a reservation held by a cookie captain for the given time block.

        Args:
            time_block (BoothTimeBlock): The time block to check.

        Returns:
            bool: True if there is a reservation held by a cookie captain, False otherwise.
        """
        return self.filter(
            time_block=time_block, owner__account_type=AccountType.COOKIE_CAPTAIN
        ).exists()

    def count_of_tickets_used(self, troop: "Troop"):
        one_week_ago = get_one_week_ago()
        used_tickets = self.filter(
            current_owner_troop_number=troop.troop_number,
            time_block__booth_day__date__gte=one_week_ago,
        ).count()

        return used_tickets

    def count_of_golden_tickets_used(self, troop: "Troop"):
        one_week_ago = get_one_week_ago()
        used_golden_tickets = self.filter(
            current_owner_troop_number=troop.troop_number,
            time_block__booth_day__date__gte=one_week_ago,
            time_block__booth_day__is_golden=True,
        ).count()

        return used_golden_tickets
