from datetime import datetime
from typing import TYPE_CHECKING, Optional

from django.db import models

from accounts.models import CustomUser as User
from cookie_booths.models.managers.blocks_manager import BoothBlockManager

if TYPE_CHECKING:
    from cookie_booths.models.day import BoothDay


class BoothBlock(models.Model):
    """Contains information for a particular booth block"""

    booth_day: "BoothDay" = models.ForeignKey(
        "cookie_booths.BoothDay",
        on_delete=models.CASCADE,
    )

    booth_block_start_time = models.DateTimeField(blank=True, null=True)
    booth_block_end_time = models.DateTimeField(blank=True, null=True)

    booth_block_held_for_cookie_captains = models.BooleanField(default=False)

    booth_block_current_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )

    booth_block_reserved = models.BooleanField(default=False)

    booth_block_daisy_troop_owner = models.IntegerField(default=0)
    booth_block_daisy_reserved = models.BooleanField(default=False)

    booth_block_enabled = models.BooleanField(default=False)
    booth_block_freeforall_enabled = models.BooleanField(default=False)

    objects: BoothBlockManager = BoothBlockManager()

    class Meta:
        permissions = (
            ("reserve_block_tcc", "Reserve a booth"),
            ("reserve_block_captain", "Reserve a block for a daisy troop"),
            ("reserve_block_admin", "Reserve/cancel any booth or hold booths for captains"),
        )

    def __str__(self):
        # More useful string in the admin
        start_hour = datetime.time(self.booth_block_start_time).hour
        end_hour = datetime.time(self.booth_block_end_time).hour
        return f"{self.booth_day} from {start_hour} to {end_hour}"

    def cancel_block(self):
        if not self._is_block_enabled():
            return False

        if not self._is_block_reserved():
            return False
        self._update_reservation(should_reserve=False)

        # TODO: Send email confirmation to both the main owner, as well as the daisy troop owner if affected
        return True

    def reserve_block(self, owner):
        if not self._is_block_enabled():
            return False

        if self._is_block_reserved():
            return False

        success = self._update_reservation(should_reserve=True, owner=owner)
        if not success:
            return False

        # TODO: Send email confirmation
        return True

    def cancel_daisy_reservation(self):
        if not self._is_block_enabled():
            return False

        if not self._is_daisy_reserved():
            return False

        self._update_daisy_reservation(should_reserve=False)
        # TODO: send email confirmation
        return True

    def reserve_daisy_block(self, daisy_troop_id):
        owner = self.booth_block_current_owner

        if not self._is_block_enabled():
            return False

        if self._is_daisy_reserved():
            return False

        if not owner.is_cookie_captain:
            return False

        self._update_daisy_reservation(should_reserve=True, daisy_troop_id=daisy_troop_id)
        return True

    def hold_for_cookie_captains(self):
        return self._set_hold_for_cookie_captains(True)

    def unhold_for_cookie_captains(self):
        return self._set_hold_for_cookie_captains(False)

    def enable_block(self):
        return self._set_block_enabled(True)

    def disable_block(self):
        return self._set_block_enabled(False)

    # helpers
    def _is_block_enabled(self):
        return self.booth_block_enabled

    def _is_block_reserved(self):
        return self.booth_block_reserved

    def _is_daisy_reserved(self):
        return self.booth_block_daisy_reserved

    def _update_reservation(self, should_reserve: bool, owner: Optional[User] = None) -> bool:
        """
        Updates the reservation status and owner of the booth block.

        Args:
            should_reserve (bool): The reservation status of the booth block.
            owner (User, optional): The owner of the booth block. Defaults to None.

        Returns:
            bool: True if the update is successful, False otherwise.
        """
        self.booth_block_reserved = should_reserve
        if owner:
            self.booth_block_current_owner = owner
        else:
            if self.booth_block_daisy_reserved:
                # If a Daisy Troop has reserved the booth, you cannot cancel the reservation
                return False
            else:
                self.booth_block_current_owner = None
                self.booth_block_daisy_reserved = False
                self.booth_block_daisy_troop_owner = 0
        self.save()
        return True

    def _update_daisy_reservation(self, should_reserve, daisy_troop_id=0):
        """
        Updates the reservation status and troop owner for a Daisy booth block.

        Args:
            reserved (bool): The reservation status of the booth block.
            daisy_troop_id (int, optional): The ID of the Daisy troop that owns the booth block. Defaults to 0.
        """
        self.booth_block_daisy_reserved = should_reserve
        self.booth_block_daisy_troop_owner = daisy_troop_id
        self.save()

    def _set_hold_for_cookie_captains(self, hold):
        """
        Sets the hold status for the booth block for cookie captains.

        Args:
            hold (bool): The hold status to be set.

        Returns:
            bool: True if the hold status was successfully set, False otherwise.
        """
        if self.booth_block_held_for_cookie_captains == hold:
            return False

        if hold and self.booth_block_reserved:
            return False

        if not hold:
            self.cancel_block()

        self.booth_block_held_for_cookie_captains = hold
        self.save()

        return True

    def _set_block_enabled(self, enabled):
        """
        Sets the enabled status of the booth block.

        Args:
            enabled (bool): The desired enabled status of the booth block.

        Returns:
            bool: True if the enabled status was successfully set, False otherwise.
        """
        if self.booth_block_enabled == enabled:
            return True

        self.booth_block_enabled = enabled
        self.save()
        return True
