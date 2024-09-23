from django.db import models

from accounts.models import CustomUser as User
from cookie_booths.mixins import SaveReservationMixin
from cookie_booths.models.managers.daisy_reservation_manager import (
    DaisyBoothReservationManager,
)
from cookie_booths.models.reservations import BoothReservation


class DaisyBoothReservation(models.Model, SaveReservationMixin):
    """Contains information specific to Daisy Troop reservations"""

    booth_reservation = models.ForeignKey(BoothReservation, on_delete=models.CASCADE)
    daisy_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    daisy_owner_troop_number = models.IntegerField(null=True, blank=True, default=None)

    objects: DaisyBoothReservationManager = DaisyBoothReservationManager()

    def __str__(self):
        return f"{self.booth_reservation} reserved by {self.daisy_owner}"

    def get_owner(self):
        return self.daisy_owner
