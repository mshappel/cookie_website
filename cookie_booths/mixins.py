from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import models

from cookie_booths.models.reservation_history import ReservationHistory
from utils.constants import ReservationAction


class SaveReservationMixin:
    reserved = models.BooleanField(default=False)

    class Meta:
        abstract = True    
    
    def get_owner(self):
        raise NotImplementedError("Subclasses must implement get_owner method")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        content_type = ContentType.objects.get_for_model(self)
        action = ReservationAction.RESERVED if self.reserved else ReservationAction.UNRESERVED
        ReservationHistory.objects.create(
            content_type=content_type,
            object_id=self.id,
            user=self.get_owner(),
            timestamp=timezone.now(),
            action=action,
        )
