#Booth Blocks Views Tests
import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from cookie_booths.models import BoothLocation, BoothDay, BoothBlock
from troops.models import Troop

PERMISSION_RESERVE_BOOTH = 'Reserve/Cancel a booth'
PERMISSION_ADMIN_RESERVE_BOOTH = 'Administrator reserve/cancel any booth, or hold booths for cookie captains to reserve'

class BoothBlockHtmlTestCase(TestCase):

    TEST_DATE = datetime.date(2021, 10, 22)
    TEST_OPEN_TIME = make_aware(datetime.datetime(2021, 10, 22, 8, 0, 0, 0))
    TEST_CLOSE_TIME = make_aware(datetime.datetime(2021, 10, 22, 10, 0, 0, 0))

    NORMAL_USER = {
        'username': 'nevergonna@giveyou.up',
        'email': 'nevergonna@giveyou.up',
        'password': 'secret',
    }

    SAME_TROOP_DETAILS = {
        'number': 300,
        'same_tcc': 'nevergonna@giveyou.up',
        'level': 2,
        'troop_size': 3,
    }

    DIFF_TROOP_DETAILS = {
        'number': 301,
        'diff_tcc': 'nevergonna@letyou.down',
        'level': 2,
        'troop_size': 3,
    }

    BOOTH_DETAILS = {
        'booth_location': 'Dunkin Donuts',
        'booth_open_date': 'October 22nd, Fri',
        'booth_open_time': '08:00 AM',
        'booth_close_time': '10:00 AM'
    }

    @classmethod
    def setUpTestData(cls) -> None:
        cls.normal_user = get_user_model().objects.create_user(
            username=cls.NORMAL_USER['username'],
            email=cls.NORMAL_USER['email'],
            password=cls.NORMAL_USER['password']
        )

        cls.same_troop = Troop.objects.create(troop_number=cls.SAME_TROOP_DETAILS['number'],
                                              troop_cookie_coordinator=cls.SAME_TROOP_DETAILS['same_tcc'],
                                              troop_level=cls.SAME_TROOP_DETAILS['level'],
                                              troop_size=cls.SAME_TROOP_DETAILS['troop_size'])

        cls.diff_troop = Troop.objects.create(troop_number=cls.DIFF_TROOP_DETAILS['number'],
                                              troop_cookie_coordinator=cls.DIFF_TROOP_DETAILS['diff_tcc'],
                                              troop_level=cls.DIFF_TROOP_DETAILS['level'],
                                              troop_size=cls.DIFF_TROOP_DETAILS['troop_size'])

        cls.location = BoothLocation.objects.create(booth_location=cls.BOOTH_DETAILS['booth_location'])
        cls.day = BoothDay.objects.create(booth=cls.location, 
                                          booth_day_date=cls.TEST_DATE)

        cls.day.add_or_update_hours(cls.TEST_OPEN_TIME, cls.TEST_CLOSE_TIME)
        cls.day.enable_day()

        cls.block = BoothBlock.objects.first()

        return super().setUpTestData()

    def test_url_exists_at_correct_location_booth_blocks(self):
        # Validate that we can access the booth blocks page. We only test log-in case, since django handles the non-login
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get('/booths/blocks/')
        self.assertEqual(response.status_code, 200)

    def test_booth_blocks_html_displays_correctly_without_permissions(self):
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('cookie_booths:booth_blocks'))

        # Is the correct data displayed?
        # - We should have a block available for reservation
        # - We should see the block details (location, date, times)
        # - We should not have any option to reserve because we have no permissions
        self.assertTemplateUsed(response, 'cookie_booths/booth_blocks.html')
        self.assertContains(response, self.BOOTH_DETAILS['booth_location'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_date'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_time'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_close_time'])
        self.assertNotContains(response, "Reserve Booth")

    def test_booth_blocks_html_displays_correctly_with_user_permissions(self):
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('cookie_booths:booth_blocks'))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We SHOULD see a reservation button
        self.assertTemplateUsed(response, 'cookie_booths/booth_blocks.html')
        self.assertContains(response, self.BOOTH_DETAILS['booth_location'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_date'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_time'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_close_time'])
        self.assertContains(response, "Reserve Booth")

    def test_booth_blocks_html_block_owned_same_troop(self):
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        self.block.reserve_block(self.same_troop.troop_number, 0)

        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('cookie_booths:booth_blocks'))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We SHOULD see a cancellation button
        self.assertTemplateUsed(response, 'cookie_booths/booth_blocks.html')
        self.assertContains(response, self.BOOTH_DETAILS['booth_location'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_date'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_time'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_close_time'])
        self.assertContains(response, "Cancel Booth")

    def test_booth_blocks_html_block_owned_diff_troop(self):
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        self.block.reserve_block(self.diff_troop.troop_number, 0)

        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('cookie_booths:booth_blocks'))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - There should be no reservation button, since the block is owned by another troop
        self.assertTemplateUsed(response, 'cookie_booths/booth_blocks.html')
        self.assertContains(response, self.BOOTH_DETAILS['booth_location'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_date'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_time'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_close_time'])
        self.assertNotContains(response, "Reserve Booth")
        self.assertNotContains(response, "Cancel Booth")

    def test_booth_blocks_html_admin_reserve_troop(self):
        self._add_permissions(PERMISSION_ADMIN_RESERVE_BOOTH)

        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('cookie_booths:booth_blocks'))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should have the option to reserve, with a drop down to select a troop
        # - We should see the block details (location, date, times)
        # - We SHOULD see a reservation button
        # - We SHOULD see a button to hold the booth for cookie captains
        self.assertTemplateUsed(response, 'cookie_booths/booth_blocks.html')
        self.assertContains(response, "Select a Troop")
        self.assertContains(response, self.BOOTH_DETAILS['booth_location'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_date'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_time'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_close_time'])
        self.assertContains(response, "Hold for Cookie Captains")
        self.assertContains(response, "Reserve Booth")

    def test_booth_blocks_html_admin_cancel_troop(self):
        self._add_permissions(PERMISSION_ADMIN_RESERVE_BOOTH)

        self.block.reserve_block(self.diff_troop.troop_number, 0)

        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('cookie_booths:booth_blocks'))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should have the option to reserve, with a drop down to select a troop
        # - We should see the block details (location, date, times)
        # - We should see a cancellation button along with with a note of which troop owns this booth
        self.assertTemplateUsed(response, 'cookie_booths/booth_blocks.html')
        self.assertContains(response, "Select a Troop")
        self.assertContains(response, self.BOOTH_DETAILS['booth_location'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_date'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_open_time'])
        self.assertContains(response, self.BOOTH_DETAILS['booth_close_time'])
        self.assertContains(response, "Reserved by 301")
        self.assertContains(response, "Cancel Booth")

    # -----------------------------------------------------------------------
    # Internal
    # -----------------------------------------------------------------------
    def _add_permissions(self, permission_name):
        # Add permission to user
        permission = Permission.objects.get(name=permission_name)
        self.normal_user.user_permissions.add(permission)
        self.normal_user.save()