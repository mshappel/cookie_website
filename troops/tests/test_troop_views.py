# Troop View Tests
from django.contrib.auth.models import Permission
from django.urls import reverse

from troops.models import Troop
from troops.tests.troop_class_reference import TroopTestCase

PERMISSION_NAME_ADD = "Can add troop"
PERMISSION_NAME_DELETE = "Can delete troop"
PERMISSION_NAME_UPDATE = "Can change troop"


class TroopViewTestCase(TroopTestCase):
    # # # TroopListView # # #
    def test_url_exists_at_correct_location_troops(self):
        # Validate that we can access the troops page. We only test log-in case, since django handles the non-login
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get("/troops/")
        self.assertEqual(response.status_code, 200)

    def test_troops_view_displays_correctly_without_permissions(self):
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("troops:troops"))

        # Is the correct data displayed?
        # - Is the correct template being used?
        # - Does the response contain TCCs?
        # - Does the response contain Troop IDs?
        # - Since we do not have permissions, we should not see add, edit or delete
        self.assertTemplateUsed(response, "troops.html")
        self.assertContains(response, self.MEDIUM_TROOP["tcc"])
        self.assertContains(response, self.SMALL_TROOP["number"])
        self.assertNotContains(response, "Add New Troop")
        self.assertNotContains(response, "Edit Troop")
        self.assertNotContains(response, "Delete Troop")

    def test_troops_view_displays_correctly_with_permissions(self):
        self._add_permissions(PERMISSION_NAME_ADD)
        self._add_permissions(PERMISSION_NAME_UPDATE)
        self._add_permissions(PERMISSION_NAME_DELETE)

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("troops:troops"))

        # Is the correct data displayed?
        # - Is the correct template being used?
        # - Does the response contain TCCs?
        # - Does the response contain Troop IDs?
        # - Since we do not have permissions, we should see add, edit and delete
        self.assertTemplateUsed(response, "troops.html")
        self.assertContains(response, self.SMALL_TROOP["tcc"])
        self.assertContains(response, self.MEDIUM_TROOP["number"])
        self.assertContains(response, "Add New Troop")
        self.assertContains(response, "Edit Troop")
        self.assertContains(response, "Delete Troop")

    # # # TroopCreateView # # #
    def test_troops_create_without_permissions(self):
        # Test if users without correct permissions get denied
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("troops:create_troop"))
        self.assertEqual(response.status_code, 403)

    def test_troops_create_displays_correctly(self):
        # This will also test create with permissions
        # Add permission to user
        self._add_permissions(PERMISSION_NAME_ADD)

        # Test if user successfully accesses the page
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(reverse("troops:create_troop"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "new_troop.html")

    def test_troops_form_data_submission(self):
        # This will also test create with permissions
        # Add permission to user
        self._add_permissions(PERMISSION_NAME_ADD)

        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        # Provide valid data
        form_data = {
            "troop_number": self.LARGE_TROOP["number"],
            "troop_cookie_coordinator": self.LARGE_TROOP["tcc"],
            "troop_level": self.LARGE_TROOP["level"],
            "troop_size": self.LARGE_TROOP["troop_size"],
        }

        # We expect that this data should be valid, and we should be re-directed back to troops/
        response = self.client.post("/troops/new/", data=form_data)
        self.assertRedirects(
            response, reverse("troops:troops"), status_code=302, target_status_code=200
        )

        # It should also have posted this data to the troop table
        self.assertEqual(Troop.objects.last().troop_number, self.LARGE_TROOP["number"])
        self.assertEqual(
            Troop.objects.last().troop_cookie_coordinator, self.LARGE_TROOP["tcc"]
        )
        self.assertEqual(Troop.objects.last().troop_level, self.LARGE_TROOP["level"])
        self.assertEqual(
            Troop.objects.last().troop_size, self.LARGE_TROOP["troop_size"]
        )

    # # # TroopUpdateView # # #
    def test_troops_update_without_permissions(self):
        # Test if users without correct permissions get denied
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get("/troops/edit/" + str(self.small_troop.pk) + "/")
        self.assertEqual(response.status_code, 403)

    def test_troops_update_displays_correctly(self):
        # Test if users with permissions are able to correctly access the page
        # Also ensure that the page displays correctly
        # Give the user permissions
        self._add_permissions(PERMISSION_NAME_UPDATE)

        # Do we successfully access the page?
        print(str(self.medium_troop.pk))
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get("/troops/edit/" + str(self.medium_troop.pk) + "/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("edit_troop.html")

        # Check if all the data we expect exists on the page; for the super troop item we check to see if the item
        # is checked. Additionally, make sure parts of the model that should not be exposed are not.
        self.assertContains(response, self.MEDIUM_TROOP["number"])
        self.assertContains(response, self.MEDIUM_TROOP["tcc"])
        self.assertContains(response, self.MEDIUM_TROOP["level"])
        self.assertContains(response, self.MEDIUM_TROOP["troop_size"])
        self.assertNotContains(response, "total_booth_tickets_per_week")

    def test_troops_update_updates_data(self):
        # Test if users with permissions are able to correctly access the page
        # Also ensure that the page displays correctly

        # Give the user permissions
        self._add_permissions(PERMISSION_NAME_UPDATE)

        # Provide valid data, see if it redirects correctly after posting?
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        form_data = {
            "troop_number": self.MEDIUM_TROOP["number"],
            "troop_cookie_coordinator": self.LARGE_TROOP["tcc"],
            "troop_level": self.MEDIUM_TROOP["level"],
            "troop_size": self.MEDIUM_TROOP["troop_size"],
        }

        response = self.client.post(
            "/troops/edit/" + str(self.medium_troop.pk) + "/", form_data
        )
        self.assertRedirects(
            response, reverse("troops:troops"), status_code=302, target_status_code=200
        )

        # Check that the data has been added to the DB
        self.assertEqual(Troop.objects.last().troop_number, self.MEDIUM_TROOP["number"])
        self.assertEqual(
            Troop.objects.last().troop_cookie_coordinator, self.LARGE_TROOP["tcc"]
        )
        self.assertEqual(Troop.objects.last().troop_level, self.MEDIUM_TROOP["level"])
        self.assertEqual(
            Troop.objects.last().troop_size, self.MEDIUM_TROOP["troop_size"]
        )

    def test_troops_update_gives_404(self):
        # Test if users with permissions that provide incorrect pk get a 404 error
        self._add_permissions(PERMISSION_NAME_UPDATE)

        # Do we get a 404 error when attempting to access the page with erroneous pk number?
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get("/troops/edit/5000/")
        self.assertEqual(response.status_code, 404)

    # # # TroopDeleteView # # #
    def test_troops_delete_without_permissions(self):
        # Test if users without correct permissions get denied
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(
            "/troops/confirm_delete/" + str(self.small_troop.pk) + "/"
        )
        self.assertEqual(response.status_code, 403)

    def test_troops_delete_view_get(self):
        # Test if users with permissions are able to correctly access the page
        # Also ensure that the page displays correctly
        # Give the user permissions
        self._add_permissions(PERMISSION_NAME_DELETE)

        # Get the page and ensure that we use the correct template, it contains the information it should and it
        # is accessible.
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.get(
            "/troops/confirm_delete/" + str(self.medium_troop.pk) + "/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("troop_confirm_delete.html")
        self.assertContains(response, "Are you sure you want to delete")

    def test_troops_delete_view_post(self):
        # Test if the user with permissions can delete troops
        # Give the user permissions
        self._add_permissions(PERMISSION_NAME_DELETE)

        # Follow-through with the deletion, and check if it redirects correctly
        self.client.login(
            email=self.NORMAL_USER["email"], password=self.NORMAL_USER["password"]
        )
        response = self.client.post(
            "/troops/confirm_delete/" + str(self.medium_troop.pk) + "/"
        )
        self.assertRedirects(
            response, reverse("troops:troops"), status_code=302, target_status_code=200
        )

        # Check to see if the data has been deleted
        null_response = self.client.get(
            "/troops/confirm_delete/" + str(self.medium_troop.pk) + "/"
        )
        self.assertEqual(null_response.status_code, 404)

    # -----------------------------------------------------------------------
    # Internal
    # -----------------------------------------------------------------------
    def _add_permissions(self, permission_name):
        # Add permission to user
        permission = Permission.objects.get(name=permission_name)
        self.normal_user.user_permissions.add(permission)
        self.normal_user.save()
