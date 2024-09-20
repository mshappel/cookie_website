import logging

from django.db import models
from django.db.models.query import QuerySet

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothLocationManager(models.Manager):
    def order_booth_locations(self) -> QuerySet:
        return self.order_by("booth_location")
