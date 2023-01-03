from django.contrib.auth import get_user_model
from django.test import TestCase

from troops.models import Troop, TroopSize, TicketParameters


class TroopTestCase(TestCase):
    SMALL_TROOP = {
        "number": 300,
        "tcc": "test@test.com",
        "level": 2,
        "troop_size": 7,
    }

    MEDIUM_TROOP = {
        "number": 400,
        "tcc": "example@example.com",
        "level": 1,
        "troop_size": 8,
    }

    LARGE_TROOP = {
        "number": 450,
        "tcc": "nevergonna@giveyou.up",
        "level": 4,
        "troop_size": 10,
    }

    NORMAL_USER = {
        "email": SMALL_TROOP["tcc"],
        "password": "secret",
    }

    @classmethod
    def setUpTestData(cls):
        cls.troop_size = TroopSize.objects.create()
        cls.ticket_parameters = TicketParameters.objects.create()
        
        cls.normal_user = get_user_model().objects.create_user(
            email=cls.NORMAL_USER["email"],
            password=cls.NORMAL_USER["password"],
        )

        cls.small_troop = Troop.objects.create(
            troop_number=cls.SMALL_TROOP["number"],
            troop_cookie_coordinator=cls.SMALL_TROOP["tcc"],
            troop_level=cls.SMALL_TROOP["level"],
            troop_size=cls.SMALL_TROOP["troop_size"],
        )

        cls.medium_troop = Troop.objects.create(
            troop_number=cls.MEDIUM_TROOP["number"],
            troop_cookie_coordinator=cls.MEDIUM_TROOP["tcc"],
            troop_level=cls.MEDIUM_TROOP["level"],
            troop_size=cls.MEDIUM_TROOP["troop_size"],
        )
