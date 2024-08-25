import logging

from django.db import models

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BoothLocationManager(models.Manager):
    def order_booth_locations(self):
        return self.order_by("booth_location")
