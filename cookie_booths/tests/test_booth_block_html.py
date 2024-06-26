# Booth Blocks Views Tests
import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.dateformat import format
from django.utils.timezone import make_aware

from cookie_booths.models import BoothLocation, BoothDay, BoothBlock
from troops.models import Troop

PERMISSION_RESERVE_BOOTH = "Reserve/Cancel a booth"
PERMISSION_ADMIN_RESERVE_BOOTH = "Administrator reserve/cancel any booth, or hold booths for cookie captains to reserve"
PERMISSION_COOKIE_CAPTAIN_RESERVE_BOOTH = "Reserve a block for a daisy scout"


class BoothBlockHtmlTestCase(TestCase):

    TEST_DATE = make_aware(datetime.datetime.now()) + datetime.timedelta(days=1)
    TEST_OPEN_TIME = make_aware(datetime.datetime.combine(TEST_DATE.date(), datetime.time(8, 0, 0, 0)))
    TEST_CLOSE_TIME = make_aware(datetime.datetime.combine(TEST_DATE.date(), datetime.time(10, 0, 0, 0)))

    NORMAL_USER = {
        "email": "nevergonna@giveyou.up",
        "password": "secret",
    }

    COOKIE_CAPTAIN_USER = {
        "email": "cookies@monster.com",
        "password": "secret"
    }

    DAISY_USER = {
        "email": "nevergonna@run.around",
        "password": "secret",
    }

    SAME_TROOP_DETAILS = {
        "number": 300,
        "same_tcc": "nevergonna@giveyou.up",
        "level": 2,
        "troop_size": 3,
    }

    DIFF_TROOP_DETAILS = {
        "number": 301,
        "diff_tcc": "nevergonna@letyou.down",
        "level": 2,
        "troop_size": 3,
    }

    DAISY_TROOP_DETAILS = {
        "number": 302,
        "daisy_tcc": "nevergonna@run.around",
        "level": 1,
        "troop_size": 3,
    }

    BOOTH_DETAILS = {
        "booth_location": "Dunkin Donuts",
        "booth_open_date": format(TEST_DATE, "F jS, D"),
        "booth_open_time": "08:00 AM",
        "booth_close_time": "10:00 AM",
    }

    @classmethod
    def setUpTestData(cls) -> None:
        cls.normal_user = get_user_model().objects.create_user(
            email=cls.NORMAL_USER["email"],
            password=cls.NORMAL_USER["password"],
        )

        cls.daisy_user = get_user_model().objects.create_user(
            email=cls.DAISY_USER["email"],
            password=cls.DAISY_USER["password"]
        )

        cls.same_troop = Troop.objects.create(
            troop_number=cls.SAME_TROOP_DETAILS["number"],
            troop_cookie_coordinator=cls.SAME_TROOP_DETAILS["same_tcc"],
            troop_level=cls.SAME_TROOP_DETAILS["level"],
            troop_size=cls.SAME_TROOP_DETAILS["troop_size"],
        )

        cls.diff_troop = Troop.objects.create(
            troop_number=cls.DIFF_TROOP_DETAILS["number"],
            troop_cookie_coordinator=cls.DIFF_TROOP_DETAILS["diff_tcc"],
            troop_level=cls.DIFF_TROOP_DETAILS["level"],
            troop_size=cls.DIFF_TROOP_DETAILS["troop_size"],
        )

        cls.daisy_troop = Troop.objects.create(
            troop_number=cls.DAISY_TROOP_DETAILS["number"],
            troop_cookie_coordinator=cls.DAISY_TROOP_DETAILS["daisy_tcc"],
            troop_level=cls.DAISY_TROOP_DETAILS["level"],
            troop_size=cls.DAISY_TROOP_DETAILS["troop_size"]
        )

        cls.cookie_captain = get_user_model().objects.create_user(
            email=cls.COOKIE_CAPTAIN_USER["email"],
            password=cls.COOKIE_CAPTAIN_USER["password"]
        )

        cls.location = BoothLocation.objects.create(
            booth_location=cls.BOOTH_DETAILS["booth_location"]
        )
        cls.day = BoothDay.objects.create(
            booth=cls.location, booth_day_date=cls.TEST_DATE
        )

        cls.day.add_or_update_hours(cls.TEST_OPEN_TIME, cls.TEST_CLOSE_TIME)
        cls.day.enable_day()

        cls.block = BoothBlock.objects.first()

        return super().setUpTestData()

    def test_url_exists_at_correct_location_booth_blocks(self):
        # Validate that we can access the booth blocks page. We only test log-in case, since django handles the non-login
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get("/booths/blocks/")
        self.assertEqual(response.status_code, 200)

    def test_booth_blocks_html_displays_correctly_without_permissions(self):
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block available for reservation
        # - We should see the block details (location, date, times)
        # - We should not have any option to reserve because we have no permissions
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertNotContains(response, "Reserve Booth")

    def test_booth_blocks_html_displays_correctly_with_user_permissions(self):
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We SHOULD see a reservation button
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Reserve Booth")

    def test_booth_blocks_html_block_owned_same_troop(self):
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        self.block.reserve_block(self.same_troop.troop_number, 0)

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We SHOULD see a cancellation button
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Cancel Booth")

    def test_booth_blocks_html_block_owned_diff_troop(self):
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        self.block.reserve_block(self.diff_troop.troop_number, 0)

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - There should be no reservation button, since the block is owned by another troop
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertNotContains(response, "Reserve Booth")
        self.assertNotContains(response, "Cancel Booth")

    def test_booth_blocks_html_admin_reserve_troop(self):
        self._add_permissions(PERMISSION_ADMIN_RESERVE_BOOTH)

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should have the option to reserve, with a drop down to select a troop
        # - We should see the block details (location, date, times)
        # - We SHOULD see a reservation button
        # - We SHOULD see a button to hold the booth for cookie captains
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, "Select a Troop")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Hold for Cookie Captains")
        self.assertContains(response, "Reserve Booth")

    def test_booth_blocks_html_admin_cancel_troop(self):
        self._add_permissions(PERMISSION_ADMIN_RESERVE_BOOTH)

        self.block.reserve_block(self.diff_troop.troop_number, 0)

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should have the option to reserve, with a drop down to select a troop
        # - We should see the block details (location, date, times)
        # - We should see info for the troop that is currently reserving this booth
        # - We should see a cancellation button along with with a note of which troop owns this booth
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, "Select a Troop")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Reserved by 301")
        self.assertContains(response, "Cancel Booth")

    def test_booth_blocks_html_block_held_for_cc(self):
        self._add_permissions(PERMISSION_ADMIN_RESERVE_BOOTH)
        self._add_permissions(PERMISSION_COOKIE_CAPTAIN_RESERVE_BOOTH)

        # Flag the one booth available as only selectable by cookie captains
        self.block.booth_block_held_for_cookie_captains = True
        self.block.save()

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should have the option to reserve, with a drop down to select a troop
        # - We should see the block details (location, date, times)
        # - We should see a button to cancel holding the booth for cookie captains
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, "Select a Troop")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Cancel Hold for Cookie Captains")

    def test_booth_blocks_html_block_held_for_cc_and_reserved(self):
        self._add_permissions(PERMISSION_ADMIN_RESERVE_BOOTH)
        self._add_permissions(PERMISSION_COOKIE_CAPTAIN_RESERVE_BOOTH)

        # Flag the one booth available as held for cookie captains, and also reserved
        self.block.booth_block_held_for_cookie_captains = True
        self.block.save()
        self.block.reserve_block(
            self.diff_troop.troop_number, 0
        )

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should have the option to reserve, with a drop down to select a troop
        # - We should see the block details (location, date, times)
        # - We should see info for the troop that is currently reserving this booth
        # - We should see a button to cancel holding the booth for cookie captains
        # - We should see a button to cancel the active reservation for the booth
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, "Select a Troop")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Reserved by 301")
        self.assertContains(response, "Cancel Booth")
        self.assertContains(
            response, "Cancel Booth And Cancel Hold for Cookie Captains"
        )

    def test_booth_blocks_html_cc_see_normal_blocks(self):
        # Testing that a Cookie Captain will still be able to see/select booths not specifically being held
        # for them
        self._add_permissions(PERMISSION_RESERVE_BOOTH)
        self._add_permissions(PERMISSION_COOKIE_CAPTAIN_RESERVE_BOOTH)

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We should see a reservation button
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Reserve Booth")

    def test_booth_blocks_html_cc_see_blocks_held_for_cc(self):
        # Testing that a Cookie Captain will be able to see blocks held just for them to reserve
        self._add_permissions(PERMISSION_RESERVE_BOOTH)
        self._add_permissions(PERMISSION_COOKIE_CAPTAIN_RESERVE_BOOTH)

        # Flag the one booth available as held for cookie captains
        self.block.booth_block_held_for_cookie_captains = True
        self.block.save()

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We should see a reservation button
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Reserve Booth")

    def test_booth_blocks_html_user_blocks_held_for_cc_not_visible(self):
        # Testing that a normal user will not see booths that are held for CCs in their list of blocks
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        # Flag the one booth available as held for cookie captains
        self.block.booth_block_held_for_cookie_captains = True
        self.block.save()

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should see no blocks available for reservation
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertNotContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertNotContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertNotContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertNotContains(response, self.BOOTH_DETAILS["booth_close_time"])

    def test_booth_blocks_html_tcc_sees_daisy_and_cc_held_booth(self):
        # Testing that a third party user can see the daisy and cookie captain information associated with a booth
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        # Flag the booth as both held by a cookie captain and a daisy troop
        self.block.reserve_block(
            0, self.cookie_captain.id
        )
        self.block.reserve_daisy_block(self.daisy_troop.troop_number)

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We should see that the block is reserved by a Daisy Troop
        # - We should not see a button to reserve or cancel this block
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Reserved by Cookie Captain cookies@monster.com")
        self.assertContains(response, "Reserved by Daisy Troop 302")
        self.assertNotContains(response, "Reserve Booth")
        self.assertNotContains(response, "Cancel Booth")

    def test_booth_blocks_html_cc_sees_daisy_held_booth(self):
        # Testing that a cookie captain can see info for a daisy troop that is reserving the same booth as them
        self._add_permissions(PERMISSION_RESERVE_BOOTH)
        self._add_permissions(PERMISSION_COOKIE_CAPTAIN_RESERVE_BOOTH)

        # Flag the booth as both held by a cookie captain and a daisy troop
        self.block.reserve_block(
            0, self.cookie_captain.id
        )
        self.block.reserve_daisy_block(self.daisy_troop.troop_number)

        self.client.login(
            email=self.COOKIE_CAPTAIN_USER["email"], password=self.COOKIE_CAPTAIN_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We should see that the block is reserved by a Daisy Troop
        # - We should see a button to cancel this block (though it will not work)
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Reserved by Daisy Troop 302")
        self.assertContains(response, "Cancel Booth")

    def test_booth_blocks_html_daisy_troop_no_booths_available(self):
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        self.client.login(
            email=self.DAISY_USER["email"], password=self.DAISY_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should see no blocks available for reservation
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertNotContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertNotContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertNotContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertNotContains(response, self.BOOTH_DETAILS["booth_close_time"])

    def test_booth_blocks_html_daisy_troop_booth_available_not_reserved(self):
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        # Flag the one booth available as held for cookie captains, and also reserved by a cookie captain
        self.block.booth_block_held_for_cookie_captains = True
        self.block.save()
        self.block.reserve_block(
            0, self.cookie_captain.id
        )

        self.client.login(
            email=self.DAISY_USER["email"], password=self.DAISY_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We should see that the block is reserved by a cookie captain
        # - We should see a button for the daisy troop to reserve the block
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Reserved by Cookie Captain cookies@monster.com")
        self.assertContains(response, "Reserve Booth")

    def test_booth_blocks_html_daisy_troop_booth_reserved(self):
        self._add_permissions(PERMISSION_RESERVE_BOOTH)

        # Flag the one booth available as held for cookie captains, and also reserved by a cookie captain
        self.block.booth_block_held_for_cookie_captains = True
        self.block.save()
        self.block.reserve_block(
            0, self.cookie_captain.id
        )
        # Flag that same booth as owned by this daisy troop
        self.block.reserve_daisy_block(self.daisy_troop.troop_number)

        self.client.login(
            email=self.DAISY_USER["email"], password=self.DAISY_USER["password"]
        )
        response = self.client.get(reverse("cookie_booths:booth_blocks"))

        # Is the correct data displayed?
        # - We should have a block listed
        # - We should see the block details (location, date, times)
        # - We should see that the block is reserved by a cookie captain
        # - We should see a button for the daisy troop to cancel the reservation
        self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
        self.assertContains(response, self.BOOTH_DETAILS["booth_location"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_date"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_open_time"])
        self.assertContains(response, self.BOOTH_DETAILS["booth_close_time"])
        self.assertContains(response, "Reserved by Cookie Captain cookies@monster.com")
        self.assertContains(response, "Cancel Booth")

    # Disable for temporary fix
    # def test_booth_blocks_html_removed_because_old(self):
    #     BAD_DATE = make_aware(datetime.datetime.now()) - datetime.timedelta(minutes=30)
    #     BAD_OPEN_TIME = make_aware(datetime.datetime.combine(BAD_DATE.date(), BAD_DATE.time()))
    #     BAD_CLOSE_TIME = make_aware(datetime.datetime.combine(BAD_DATE.date(), (BAD_DATE + datetime.timedelta(hours=2)).time()))
        
    #     self._add_permissions(PERMISSION_RESERVE_BOOTH)

    #     self.client.login(
    #         email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
    #         )
    #     self.block.booth_day.add_or_update_hours(
    #         open_time=BAD_OPEN_TIME,
    #         close_time=BAD_CLOSE_TIME,
    #         )
    #     self.block.booth_day.save()

    #     response = self.client.get(reverse("cookie_booths:booth_blocks"))

    #     # Is the correct data displayed?
    #     # - We should not have a block listed
    #     # - We should not see the block details (location, date, times)
    #     # - We SHOULD not see a reservation button
    #     self.assertTemplateUsed(response, "cookie_booths/booth_blocks.html")
    #     self.assertNotContains(response, self.BOOTH_DETAILS["booth_location"])
    #     self.assertNotContains(response, self.BOOTH_DETAILS["booth_open_date"])
    #     self.assertNotContains(response, self.BOOTH_DETAILS["booth_open_time"])
    #     self.assertNotContains(response, self.BOOTH_DETAILS["booth_close_time"])
    # -----------------------------------------------------------------------
    # Internal
    # -----------------------------------------------------------------------
    def _add_permissions(self, permission_name):
        # Add permission to both users
        permission = Permission.objects.get(name=permission_name)
        self.normal_user.user_permissions.add(permission)
        self.normal_user.save()

        self.daisy_user.user_permissions.add(permission)
        self.daisy_user.save()

        self.cookie_captain.user_permissions.add(permission)
        self.cookie_captain.save()
