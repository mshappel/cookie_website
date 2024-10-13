import logging

from django.db import models

from accounts.models import CustomUser as User
from cookie_booths.mixins import SaveReservationMixin
from cookie_booths.models.managers.reservation_manager import BoothReservationManager
from cookie_booths.models.time_block import BoothTimeBlock

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothReservation(models.Model, SaveReservationMixin):
    """Contains information specific to a reservation"""

    time_block: "BoothTimeBlock" = models.ForeignKey(
        BoothTimeBlock,
        on_delete=models.CASCADE,
        related_name="boothreservations",
    )
    held_for_cookie_captains = models.BooleanField(default=False)
    current_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    current_owner_troop_number = models.IntegerField(null=True, blank=True, default=None)

    objects: BoothReservationManager = BoothReservationManager()

    class Meta:
        permissions = (
            ("reserve_block_tcc", "Reserve a booth"),
            ("reserve_block_captain", "Reserve a block for a daisy troop"),
            ("reserve_block_admin", "Reserve/cancel any booth or hold booths for captains"),
        )

    def __str__(self):
        return f"{self.time_block} reserved by {self.current_owner}"

    def save(self, *args, **kwargs):
        """
        Override the save method to enforce that held_for_cookie_captains is False
        if current_owner or current_owner_troop_number is set.
        """
        if self.current_owner or self.current_owner_troop_number:
            self.held_for_cookie_captains = False
        super().save(*args, **kwargs)
    
    def get_owner(self):
        return self.current_owner
