from datetime import datetime
from typing import TYPE_CHECKING, Union

from django.apps import apps
from django.db import models
from django.db.models import QuerySet

from accounts.models import CustomUser as User
from cookie_booths.models.managers.time_block_manager import BoothTimeBlockManager
from cookie_booths.models.season import CookieSeason


if TYPE_CHECKING:
    from cookie_booths.models.daisy_reservations import DaisyBoothReservation
    from cookie_booths.models.day import BoothDay
    from cookie_booths.models.reservations import BoothReservation
    from troops.models import Troop


class BoothTimeBlock(models.Model):
    """Contains information for a particular booth time block"""

    booth_day: "BoothDay" = models.ForeignKey(
        "cookie_booths.BoothDay",
        on_delete=models.CASCADE,
    )

    booth_block_start_time = models.DateTimeField(blank=True, null=True)
    booth_block_end_time = models.DateTimeField(blank=True, null=True)

    booth_block_enabled = models.BooleanField(default=False)
    booth_block_freeforall_enabled = models.BooleanField(default=False)

    objects: BoothTimeBlockManager = BoothTimeBlockManager()

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

    @property
    def BoothReservationModel(self) -> "BoothReservation":
        return apps.get_model("cookie_booths", "BoothReservation")

    @property
    def DaisyBoothReservationModel(self) -> "DaisyBoothReservation":
        return apps.get_model("cookie_booths", "DaisyBoothReservation")

    def get_reservation_model(self, troop: "Troop"):
        """
        Returns the appropriate reservation model based on the troop level.

        Args:
            troop (Troop): The troop to check.

        Returns:
            Model: The appropriate reservation model.
        """
        if troop.is_daisy_troop:
            return self.DaisyBoothReservationModel
        else:
            return self.BoothReservationModel

    def is_reserved(self) -> bool:
        """
        Checks if the time block is reserved.

        Returns:
            bool: True if there are any booth reservations associated with this time block,
                False otherwise.
        """
        boothreservations: "QuerySet[BoothReservation]" = self.boothreservations
        return boothreservations.exists()

    def passes_level_restrictions(self, troop_level: int) -> bool:
        """
        Checks if the troop level passes the level restrictions for the time block.

        Args:
            troop_level (int): The level of the troop.

        Returns:
            bool: True if the troop level passes the level restrictions, False otherwise.
        """
        booth_location = self.booth_day.booth_location
        booth_restrictions_start = booth_location.booth_block_level_restrictions_start
        booth_restrictions_end = booth_location.booth_block_level_restrictions_end

        if booth_restrictions_start:
            return troop_level in range(booth_restrictions_start, booth_restrictions_end + 1)
        return True

    def is_reservable_within_cookie_season(
        self,
        cookie_season: CookieSeason,
        use_offset: bool = False,
    ) -> bool:
        """
        Checks if the time block is within the cookie season.

        Args:
            cookie_season (CookieSeason): The cookie season to check.

        Returns:
            bool: True if the time block is within the cookie season, False otherwise.
        """
        booth_date = self.booth_block_start_time.date()
        if use_offset:
            return cookie_season.is_daisy_booth_reservable(booth_date)
        return cookie_season.is_booth_reservable(booth_date)

    def is_booth_reservable_by_daisy_troop(self, troop_number: int) -> bool:
        """
        Checks if the booth time block can be reserved by a Daisy Troop.

        Args:
            troop_number (int): The troop number attempting to reserve the booth.

        Returns:
            bool: True if the booth can be reserved by the Daisy Troop, False otherwise.
        """
        cookie_captain_reservation = self.is_reserved_by_cookie_captain()

        if not cookie_captain_reservation:
            return False

        # Check if there is an existing reservation for another Daisy Troop
        existing_daisy_reservation = self.is_reserved_by_daisy_troop(troop_number=troop_number)

        return not existing_daisy_reservation

    def is_reserved_by_cookie_captain(self) -> bool:
        """
        Checks if the time block is reserved by a cookie captain.

        Returns:
            bool: True if the time block is reserved by a cookie captain, False otherwise.
        """
        is_reserved = self.BoothReservationModel.objects.has_cookie_captain_reservation(
            time_block=self
        )
        return is_reserved

    def is_reserved_by_daisy_troop(self, troop_number: int) -> bool:
        """
        Checks if the time block is reserved by a Daisy Troop.

        Returns:
            bool: True if the time block is reserved by a Daisy Troop, False otherwise.
        """

        is_reserved = self.DaisyBoothReservationModel.objects.has_existing_daisy_reservation(
            time_block=self,
            troop_number=troop_number,
        )
        return is_reserved

    def has_used_all_regular_tickets(self, troop: "Troop") -> bool:
        """
        Checks if the troop has used all of their allotted tickets within a week.

        Args:
            troop (Troop): The troop to check.

        Returns:
            bool: True if the troop has used all their tickets, False otherwise.
        """
        reservation_model = self.get_reservation_model(troop=troop)
        used_tickets = reservation_model.objects.count_of_tickets_used(troop=troop)

        return used_tickets >= troop.total_booth_tickets_per_week

    def has_used_all_golden_tickets(self, troop: "Troop") -> bool:
        """
        Checks if the troop has used all of their allotted golden tickets within a week.

        Args:
            troop (Troop): The troop to check.

        Returns:
            bool: True if the troop has used all their golden tickets, False otherwise.
        """
        reservation_model = self.get_reservation_model(troop=troop)
        used_golden_tickets = reservation_model.objects.count_of_golden_tickets_used(troop=troop)

        return used_golden_tickets >= troop.booth_golden_tickets_per_week

    def can_be_reserved_by_troop(self, troop: "Troop") -> bool:
        """
        Checks if the booth time block can be reserved by a troop.

        Returns:
            bool: True if the booth can be reserved by the troop, False otherwise.
        """
        cookie_season = CookieSeason.objects.first()

        if not self.booth_block_enabled:
            return False

        if self.is_reserved():
            self.BoothReservationModel.objects.get_reservation(time_block=self)
            return False

        if self.booth_block_freeforall_enabled:
            return True

        if not self.is_reservable_within_cookie_season(cookie_season=cookie_season):
            return False

        if not self.passes_level_restrictions(troop_level=troop.troop_level):
            return False

        if self.has_used_all_tickets(troop=troop):
            return False

        return True

    def can_be_reserved_by_daisy_troop(self, troop: "Troop") -> bool:
        """
        Checks if the booth time block can be reserved by a Daisy Troop.

        Returns:
            bool: True if the booth can be reserved by the Daisy Troop, False otherwise.
        """
        cookie_season = CookieSeason.objects.first()

        if not self.booth_block_enabled:
            return False

        if not self.is_booth_reservable_by_daisy_troop(troop_number=troop.troop_number):
            return False

        if self.booth_block_freeforall_enabled:
            return True

        if not self.is_reservable_within_cookie_season(
            cookie_season=cookie_season, use_offset=True
        ):
            return False

        if self.has_used_all_tickets(troop=troop):
            return False

    def can_be_reserved_by_cookie_captain(self, user: "User") -> bool:
        """
        Determines if the time block can be reserved by a cookie captain.
        Args:
            user (User): The user attempting to reserve the time block.
        Returns:
            bool: True if the time block can be reserved by the cookie captain, False otherwise.
        Conditions:
            - The booth block must be enabled.
            - If the booth block is in free-for-all mode, it can be reserved.
            - The time block must be reservable within the cookie season.
            - The booth does not have a reservation already, unless it is held for a cookie captain.
            - The user must not have used their cookie captain tickets.
        """
        cookie_season = CookieSeason.objects.first()
        if not self.booth_block_enabled:
            return False

        if self.booth_block_freeforall_enabled:
            return True

        if not self.is_reservable_within_cookie_season(
            cookie_season=cookie_season, use_offset=True
        ):
            return False

        if self.is_reserved():
            reservation = self.BoothReservationModel.objects.get_reservation(time_block=self)
            if reservation.held_for_cookie_captains:
                return True
            return False

        if self.has_used_cookie_captain_tickets(user=user):
            return False

    def has_used_all_tickets(self, troop: "Troop") -> bool:
        """
        Checks if the troop has used all of their allotted tickets within a week.

        Args:
            troop (Troop): The troop to check.

        Returns:
            bool: True if the troop has used all their tickets, False otherwise.
        """
        if self.booth_day.booth_day_is_golden:
            if self.has_used_all_golden_tickets(troop=troop):
                return False
        else:
            if self.has_used_all_regular_tickets(troop=troop):
                return False

        return True

    def has_used_cookie_captain_tickets(self, user: "User") -> bool:
        """
        Checks if the cookie captain has used all of their allotted tickets within a week.

        Args:
            user (User): The cookie captain to check.

        Returns:
            bool: True if the cookie captain has used all their tickets, False otherwise.
        """
        from accounts.models import Configuration

        used_tickets = self.BoothReservationModel.objects.count_of_tickets_used_by_user(user=user)
        return used_tickets >= Configuration.get_cookie_captain_tickets_per_week()

    def can_be_reserved(self, user: "User", troop: "Troop" = None) -> bool:
        """
        Determines if the booth time block can be reserved based on the user account type and troop level.

        Args:
            user (User): The user attempting to reserve the booth.
            troop (Troop): The troop attempting to reserve the booth (optional).

        Returns:
            bool: True if the booth can be reserved, False otherwise.
        """
        if user.is_cookie_captain:
            return self.can_be_reserved_by_cookie_captain(user=user)
        elif user.is_tcc or user.is_admin:
            if troop and troop.is_daisy_troop:
                return self.can_be_reserved_by_daisy_troop(troop=troop)
            else:
                return self.can_be_reserved_by_troop(troop=troop)
        else:
            return False

    def create_reservation(
        self,
        user: "User",
        troop: "Troop" = None,
    ) -> Union[bool, "BoothReservation", "DaisyBoothReservation"]:
        """
        Creates a reservation for the time block.

        Args:
            user (User): The user creating the reservation.
            troop (Troop): The troop creating the reservation (optional).

        Returns:
            BoothReservation: The reservation created.
        """
        if self.can_be_reserved(user=user, troop=troop):

            reservation_model = self.get_reservation_model(troop=troop)
            reservation: Union["BoothReservation", "DaisyBoothReservation"]
            created: bool
            reservation, created = reservation_model.objects.get_or_create(
                time_block=self,
                defaults={
                    "current_owner": user.email,
                    "current_owner_troop_number": troop.troop_number if troop else None,
                    "held_for_cookie_captains": False,
                },
            )
            if not created:
                reservation.current_owner = user
                reservation.current_owner_troop_number = troop.troop_number if troop else None
                reservation.save()
            return reservation
        else:
            return False

    def delete_reservation(self, user: "User", troop: "Troop" = None) -> bool:
        """
        Deletes a reservation for the time block if the conditions are met.

        Args:
            user (User): The user attempting to delete the reservation.
            troop (Troop): The troop attempting to delete the reservation (optional).

        Returns:
            bool: True if the reservation was deleted, False otherwise.
        """
        try:
            if troop:
                reservation_model = self.get_reservation_model(troop=troop)
                reservation: Union["BoothReservation", "DaisyBoothReservation"] = (
                    reservation_model.objects.get(time_block=self, current_owner=user.email)
                )
        except BoothReservation.DoesNotExist or DaisyBoothReservation.DoesNotExist:
            return False

        if user.is_cookie_captain:
            # Check if a Daisy reservation exists
            if DaisyBoothReservation.objects.filter(time_block=self).exists():
                return False

        # Delete the reservation
        reservation.delete()
        return True
