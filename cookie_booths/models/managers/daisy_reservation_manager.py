from typing import TYPE_CHECKING

from django.db import models

from utils.date_utils import get_one_week_ago

if TYPE_CHECKING:
    from troops.models import Troop


class DaisyBoothReservationManager(models.Manager):
    def has_existing_daisy_reservation(self, time_block, troop_number):
        """
        Checks if there is an existing reservation for another Daisy Troop for the given time block.

        Args:
            time_block (BoothTimeBlock): The time block to check.
            troop_number (int): The troop number attempting to reserve the booth.

        Returns:
            bool: True if there is an existing reservation for another Daisy Troop, False otherwise.
        """
        return (
            self.filter(
                booth_reservation__time_block=time_block, daisy_owner_troop_number__isnull=False
            )
            .exclude(daisy_owner_troop_number=troop_number)
            .exists()
        )

    def count_of_tickets_used(self, troop: "Troop"):
        one_week_ago = get_one_week_ago()
        used_tickets = self.filter(
            daisy_owner_troop_number=troop.troop_number,
            time_block__booth_day__date__gte=one_week_ago,
        ).count()

        return used_tickets

    def count_of_golden_tickets_used(self, troop: "Troop"):
        one_week_ago = get_one_week_ago()
        used_golden_tickets = self.filter(
            daisy_owner_troop_number=troop.troop_number,
            time_block__booth_day__date__gte=one_week_ago,
            time_block__booth_day__is_golden=True,
        ).count()

        return used_golden_tickets
