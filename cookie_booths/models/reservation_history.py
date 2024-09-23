import logging

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from utils.constants import ReservationAction
from utils.enum_conversation import enum_choices_to_tuple

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class ReservationHistory(models.Model):
    """Contains history of reservations"""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    reservation = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    action = models.CharField(max_length=10, choices=[enum_choices_to_tuple(ReservationAction)])

    def __str__(self):
        return f"{self.user} {self.action} {self.reservation} on {self.timestamp}"
