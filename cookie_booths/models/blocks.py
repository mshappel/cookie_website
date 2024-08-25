from datetime import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from accounts.models import CustomUser as User
from cookie_booths.models.day import BoothDay
from cookie_booths.models.managers.blocks_manager import BoothBlockManager
from troops.models import Troop


class BoothBlock(models.Model):
    """Contains information for a particular booth block"""

    booth_day = models.ForeignKey(BoothDay, on_delete=models.CASCADE)

    booth_block_start_time = models.DateTimeField(blank=True, null=True)
    booth_block_end_time = models.DateTimeField(blank=True, null=True)

    booth_block_held_for_cookie_captains = models.BooleanField(default=False)

    owner_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, default=None, null=True
    )
    owner_object_id = models.PositiveIntegerField(default=0)
    booth_block_current_owner = GenericForeignKey("owner_content_type", "owner_object_id")

    booth_block_reserved = models.BooleanField(default=False)

    booth_block_daisy_troop_owner = models.IntegerField(default=0)
    booth_block_daisy_reserved = models.BooleanField(default=False)

    booth_block_enabled = models.BooleanField(default=False)
    booth_block_freeforall_enabled = models.BooleanField(default=False)

    objects: BoothBlockManager = BoothBlockManager()

    class Meta:
        permissions = (
            ("block_reservation", "Reserve/Cancel a booth"),
            ("reserve_block", "Reserve a booth"),
            ("cookie_captain_reserve_block", "Reserve a block for a daisy scout"),
            (
                "block_reservation_admin",
                "Administrator reserve/cancel any booth, or hold booths for reservation",
            ),
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

        if isinstance(owner, Troop):
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

    def is_owner_custom_user(self):
        custom_user_type = ContentType.objects.get_for_model(User)
        return self.owner_content_type == custom_user_type

    # helpers
    def _is_block_enabled(self):
        return self.booth_block_enabled

    def _is_block_reserved(self):
        return self.booth_block_reserved

    def _is_daisy_reserved(self):
        return self.booth_block_daisy_reserved

    def _update_reservation(self, should_reserve, owner=None):
        """
        Updates the reservation status and owner of the booth block.

        Args:
            reserved (bool): The reservation status of the booth block.
            owner (Troop or User, optional): The owner of the booth block. Defaults to None.

        Returns:
            bool: True if the update is successful, False otherwise.
        """
        self.booth_block_reserved = should_reserve
        if owner:
            if isinstance(owner, Troop):
                self.owner_content_type = ContentType.objects.get_for_model(Troop)
                self.owner_object_id = owner.id
            elif isinstance(owner, User):
                self.owner_content_type = ContentType.objects.get_for_model(User)
                self.owner_object_id = owner.id
            else:
                return False  # Invalid owner type
        else:
            self.owner_content_type = None
            self.owner_object_id = 0
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
            return True

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
