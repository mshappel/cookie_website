from typing import TYPE_CHECKING, Optional

from django.db import models

if TYPE_CHECKING:
    from troops.models import Troop


class TroopManager(models.Manager):
    def get_troop_model_by_email(self, email: str) -> Optional["Troop"]:
        return self.filter(troop_cookie_coordinator=email).first()

    def troops_ordered_by_troop_number(self):
        return self.order_by("troop_number")

    def is_daisy_troop_by_email(self, email: str) -> bool:
        troop = self.get_troop_model_by_email(email)
        return troop.is_daisy_troop if troop else False
