from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Troop, TicketParameters

NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK = TicketParameters.NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK
SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK = TicketParameters.SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK
NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK = TicketParameters.NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK
SUPER_TROOP_TOTAL_TICKETS_PER_WEEK = TicketParameters.SUPER_TROOP_TOTAL_TICKETS_PER_WEEK


class TroopTestCase(TestCase):

    NORMAL_TROOP = {
        'number': 300,
        'tcc': 'test@test.com',
        'level': 2,
        'super_troop': False,
    }

    SUPER_TROOP = {
        'number': 400,
        'tcc': 'example@example.com',
        'level': 1,
        'super_troop': True,
    }

    TEST_USER = {
        'username': NORMAL_TROOP['tcc'],
        'email': NORMAL_TROOP['tcc'],
        'password': 'secret',
    }

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username=cls.TEST_USER['username'],
            email=cls.TEST_USER['email'],
            password=cls.TEST_USER['password']
        )

        cls.normal_troop = Troop.objects.create(troop_number=cls.NORMAL_TROOP['number'],
                                                troop_cookie_coordinator=cls.NORMAL_TROOP['tcc'],
                                                troop_level=cls.NORMAL_TROOP['level'])

        cls.super_troop = Troop.objects.create(troop_number=cls.SUPER_TROOP['number'],
                                               troop_cookie_coordinator=cls.SUPER_TROOP['tcc'],
                                               troop_level=cls.SUPER_TROOP['level'],
                                               super_troop=cls.SUPER_TROOP['super_troop'])

    def test_troop_model(self):
        # Validate the user can see the listed troops
        # Normal
        self.assertEqual(self.normal_troop.troop_number, self.NORMAL_TROOP['number'])
        self.assertEqual(self.normal_troop.troop_cookie_coordinator, self.NORMAL_TROOP['tcc'])
        self.assertEqual(self.normal_troop.troop_level, self.NORMAL_TROOP['level'])
        self.assertFalse(self.normal_troop.super_troop)

        # Super
        self.assertEqual(self.super_troop.troop_number, self.SUPER_TROOP['number'])
        self.assertEqual(self.super_troop.troop_cookie_coordinator, self.SUPER_TROOP['tcc'])
        self.assertEqual(self.super_troop.troop_level, self.SUPER_TROOP['level'])
        self.assertTrue(self.super_troop.super_troop)

    def test_ticket_allocation(self):
        # Validate the ticket allocation of both super and regular troops
        self.assertTrue(self.normal_troop.total_booth_tickets_per_week == NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK)
        self.assertTrue(self.normal_troop.booth_golden_tickets_per_week == NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK)

        self.assertTrue(self.super_troop.total_booth_tickets_per_week == SUPER_TROOP_TOTAL_TICKETS_PER_WEEK)
        self.assertTrue(self.super_troop.booth_golden_tickets_per_week == SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK)

    def test_url_exists_at_correct_location_troops(self):
        # Validate that we can access the troops page. We only test log-in case, since django handles the non-login
        self.client.login(username=self.TEST_USER['username'], password=self.TEST_USER['password'])
        response = self.client.get('/troops/')
        self.assertEqual(response.status_code, 200)

    def test_troops_view_displays_correctly(self):
        self.client.login(username=self.TEST_USER['username'], password=self.TEST_USER['password'])
        response = self.client.get(reverse('troops:troops'))

        # Is the correct data displayed?
        # - Is the correct template being used?
        # - Does the response contain TCCs?
        # - Does the response contain Troop IDs?
        self.assertTemplateUsed(response, 'troops.html')
        self.assertContains(response, self.SUPER_TROOP['tcc'])
        self.assertContains(response, self.NORMAL_TROOP['number'])

    # TODO: Add tests for create_troop and edit_troop views, then change them over to class based


