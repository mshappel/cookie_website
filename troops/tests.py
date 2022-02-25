from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .forms import TroopForm
from .models import Troop, TicketParameters

NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK = TicketParameters.NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK
SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK = TicketParameters.SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK
NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK = TicketParameters.NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK
SUPER_TROOP_TOTAL_TICKETS_PER_WEEK = TicketParameters.SUPER_TROOP_TOTAL_TICKETS_PER_WEEK

PERMISSION_NAME_ADD = 'Can add troop'
PERMISSION_NAME_DELETE = 'Can delete troop'
PERMISSION_NAME_UPDATE = 'Can change troop'


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

    ADDITIONAL_TROOP = {
        'number': 450,
        'tcc': 'nevergonna@giveyou.up',
        'level': 4,
        'super_troop': False,
    }

    NORMAL_USER = {
        'username': NORMAL_TROOP['tcc'],
        'email': NORMAL_TROOP['tcc'],
        'password': 'secret',
    }

    @classmethod
    def setUpTestData(cls):
        cls.normal_user = get_user_model().objects.create_user(
            username=cls.NORMAL_USER['username'],
            email=cls.NORMAL_USER['email'],
            password=cls.NORMAL_USER['password']
        )

        cls.normal_troop = Troop.objects.create(troop_number=cls.NORMAL_TROOP['number'],
                                                troop_cookie_coordinator=cls.NORMAL_TROOP['tcc'],
                                                troop_level=cls.NORMAL_TROOP['level'])

        cls.super_troop = Troop.objects.create(troop_number=cls.SUPER_TROOP['number'],
                                               troop_cookie_coordinator=cls.SUPER_TROOP['tcc'],
                                               troop_level=cls.SUPER_TROOP['level'],
                                               super_troop=cls.SUPER_TROOP['super_troop'])

    # -----------------------------------------------------------------------
    # Troop Model Tests
    # -----------------------------------------------------------------------
    def test_troop_model(self):
        # Validate the database contains the expected data

        # Normal
        self.assertEqual(self.normal_troop.troop_number, self.NORMAL_TROOP['number'])
        self.assertEqual(self.normal_troop.troop_cookie_coordinator, self.NORMAL_TROOP['tcc'])
        self.assertEqual(self.normal_troop.troop_level, self.NORMAL_TROOP['level'])
        self.assertFalse(self.normal_troop.super_troop)
        self.assertEqual(self.normal_troop.total_booth_tickets_per_week, NORMAL_TROOP_TOTAL_TICKETS_PER_WEEK)
        self.assertEqual(self.normal_troop.booth_golden_tickets_per_week, NORMAL_TROOP_GOLDEN_TICKETS_PER_WEEK)

        # Super
        self.assertEqual(self.super_troop.troop_number, self.SUPER_TROOP['number'])
        self.assertEqual(self.super_troop.troop_cookie_coordinator, self.SUPER_TROOP['tcc'])
        self.assertEqual(self.super_troop.troop_level, self.SUPER_TROOP['level'])
        self.assertTrue(self.super_troop.super_troop)
        self.assertEqual(self.super_troop.total_booth_tickets_per_week, SUPER_TROOP_TOTAL_TICKETS_PER_WEEK)
        self.assertEqual(self.super_troop.booth_golden_tickets_per_week, SUPER_TROOP_GOLDEN_TICKETS_PER_WEEK)

    # -----------------------------------------------------------------------
    # Troop Form Tests
    # -----------------------------------------------------------------------
    def test_troops_form_with_valid_data(self):
        # Provide valid data and check if the form declares it is valid
        form_data = {
            'troop_number': self.ADDITIONAL_TROOP['number'],
            'troop_cookie_coordinator': self.ADDITIONAL_TROOP['tcc'],
            'troop_level': self.ADDITIONAL_TROOP['level'],
            'super_troop': self.ADDITIONAL_TROOP['super_troop'],
        }
        form = TroopForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_troops_form_with_invalid_data(self):
        # Test to be sure that troop numbers are unique; check if the user receives the correct error message
        form_data = {
            'troop_number': self.NORMAL_TROOP['number'],
            'troop_cookie_coordinator': self.ADDITIONAL_TROOP['tcc'],
            'troop_level': self.ADDITIONAL_TROOP['level'],
            'super_troop': self.ADDITIONAL_TROOP['super_troop'],
        }
        form = TroopForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['troop_number'],
                         ["Troop number is already taken. Please choose a unique troop number."])

    # -----------------------------------------------------------------------
    # Troop View Tests
    # -----------------------------------------------------------------------
    # # # TroopListView # # #
    def test_url_exists_at_correct_location_troops(self):
        # Validate that we can access the troops page. We only test log-in case, since django handles the non-login
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get('/troops/')
        self.assertEqual(response.status_code, 200)

    def test_troops_view_displays_correctly_without_permissions(self):
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('troops:troops'))

        # Is the correct data displayed?
        # - Is the correct template being used?
        # - Does the response contain TCCs?
        # - Does the response contain Troop IDs?
        # - Since we do not have permissions, we should not see add, edit or delete
        self.assertTemplateUsed(response, 'troops.html')
        self.assertContains(response, self.SUPER_TROOP['tcc'])
        self.assertContains(response, self.NORMAL_TROOP['number'])
        self.assertNotContains(response, "Add New Troop")
        self.assertNotContains(response, "Edit Troop")
        self.assertNotContains(response, "Delete Troop")

    def test_troops_view_displays_correctly_with_permissions(self):
        self._add_permissions(PERMISSION_NAME_ADD)
        self._add_permissions(PERMISSION_NAME_UPDATE)
        self._add_permissions(PERMISSION_NAME_DELETE)

        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('troops:troops'))

        # Is the correct data displayed?
        # - Is the correct template being used?
        # - Does the response contain TCCs?
        # - Does the response contain Troop IDs?
        # - Since we do not have permissions, we should see add, edit and delete
        self.assertTemplateUsed(response, 'troops.html')
        self.assertContains(response, self.NORMAL_TROOP['tcc'])
        self.assertContains(response, self.SUPER_TROOP['number'])
        self.assertContains(response, "Add New Troop")
        self.assertContains(response, "Edit Troop")
        self.assertContains(response, "Delete Troop")

    # # # TroopCreateView # # #
    def test_troops_create_without_permissions(self):
        # Test if users without correct permissions get denied
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('troops:create_troop'))
        self.assertEqual(response.status_code, 403)

    def test_troops_create_displays_correctly(self):
        # This will also test create with permissions
        # Add permission to user
        self._add_permissions(PERMISSION_NAME_ADD)

        # Test if user successfully accesses the page
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get(reverse('troops:create_troop'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_troop.html')

    def test_troops_form_data_submission(self):
        # This will also test create with permissions
        # Add permission to user
        self._add_permissions(PERMISSION_NAME_ADD)

        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        # Provide valid data
        form_data = {
            'troop_number': self.ADDITIONAL_TROOP['number'],
            'troop_cookie_coordinator': self.ADDITIONAL_TROOP['tcc'],
            'troop_level': self.ADDITIONAL_TROOP['level'],
            'super_troop': self.ADDITIONAL_TROOP['super_troop'],
        }

        # We expect that this data should be valid, and we should be re-directed back to troops/
        response = self.client.post('/troops/new/', data=form_data)
        self.assertRedirects(response, reverse('troops:troops'), status_code=302, target_status_code=200)

        # It should also have posted this data to the troop table
        self.assertEqual(Troop.objects.last().troop_number, self.ADDITIONAL_TROOP['number'])
        self.assertEqual(Troop.objects.last().troop_cookie_coordinator, self.ADDITIONAL_TROOP['tcc'])
        self.assertEqual(Troop.objects.last().troop_level, self.ADDITIONAL_TROOP['level'])
        self.assertEqual(Troop.objects.last().super_troop, self.ADDITIONAL_TROOP['super_troop'])

    # # # TroopUpdateView # # #
    def test_troops_update_without_permissions(self):
        # Test if users without correct permissions get denied
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get('/troops/edit/' + str(self.normal_troop.pk) + '/')
        self.assertEqual(response.status_code, 403)

    def test_troops_update_displays_correctly(self):
        # Test if users with permissions are able to correctly access the page
        # Also ensure that the page displays correctly
        # Give the user permissions
        self._add_permissions(PERMISSION_NAME_UPDATE)

        # Do we successfully access the page?
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get('/troops/edit/' + str(self.super_troop.pk) + '/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('edit_troop.html')

        # Check if all the data we expect exists on the page; for the super troop item we check to see if the item
        # is checked. Additionally, make sure parts of the model that should not be exposed are not.
        self.assertContains(response, self.SUPER_TROOP['number'])
        self.assertContains(response, self.SUPER_TROOP['tcc'])
        self.assertContains(response, self.SUPER_TROOP['level'])
        self.assertContains(response, 'checked')
        self.assertNotContains(response, 'total_booth_tickets_per_week')

    def test_troops_update_updates_data(self):
        # Test if users with permissions are able to correctly access the page
        # Also ensure that the page displays correctly

        # Give the user permissions
        self._add_permissions(PERMISSION_NAME_UPDATE)

        # Provide valid data, see if it redirects correctly after posting?
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        form_data = {
            'troop_number': self.SUPER_TROOP['number'],
            'troop_cookie_coordinator': self.ADDITIONAL_TROOP['tcc'],
            'troop_level': self.SUPER_TROOP['level'],
            'super_troop': self.SUPER_TROOP['super_troop'],
        }

        response = self.client.post('/troops/edit/' + str(self.super_troop.pk) + '/', form_data)
        self.assertRedirects(response, reverse('troops:troops'), status_code=302, target_status_code=200)

        # Check that the data has been added to the DB
        self.assertEqual(Troop.objects.last().troop_number, self.SUPER_TROOP['number'])
        self.assertEqual(Troop.objects.last().troop_cookie_coordinator, self.ADDITIONAL_TROOP['tcc'])
        self.assertEqual(Troop.objects.last().troop_level, self.SUPER_TROOP['level'])
        self.assertEqual(Troop.objects.last().super_troop, self.SUPER_TROOP['super_troop'])

    def test_troops_update_gives_404(self):
        # Test if users with permissions that provide incorrect pk get a 404 error
        self._add_permissions(PERMISSION_NAME_UPDATE)

        # Do we get a 404 error when attempting to access the page with erroneous pk number?
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get('/troops/edit/5000/')
        self.assertEqual(response.status_code, 404)

    # # # TroopDeleteView # # #
    def test_troops_delete_without_permissions(self):
        # Test if users without correct permissions get denied
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get('/troops/confirm_delete/' + str(self.normal_troop.pk) + '/')
        self.assertEqual(response.status_code, 403)

    def test_troops_delete_view_get(self):
        # Test if users with permissions are able to correctly access the page
        # Also ensure that the page displays correctly
        # Give the user permissions
        self._add_permissions(PERMISSION_NAME_DELETE)

        # Get the page and ensure that we use the correct template, it contains the information it should and it
        # is accessible.
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.get('/troops/confirm_delete/' + str(self.super_troop.pk) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('troop_confirm_delete.html')
        self.assertContains(response, 'Are you sure you want to delete')

    def test_troops_delete_view_post(self):
        # Test if the user with permissions can delete troops
        # Give the user permissions
        self._add_permissions(PERMISSION_NAME_DELETE)

        # Follow-through with the deletion, and check if it redirects correctly
        self.client.login(username=self.NORMAL_USER['username'], password=self.NORMAL_USER['password'])
        response = self.client.post('/troops/confirm_delete/' + str(self.super_troop.pk) + '/')
        self.assertRedirects(response, reverse('troops:troops'), status_code=302, target_status_code=200)

        # Check to see if the data has been deleted
        null_response = self.client.get('/troops/confirm_delete/' + str(self.super_troop.pk) + '/')
        self.assertEqual(null_response.status_code, 404)

    # -----------------------------------------------------------------------
    # Internal
    # -----------------------------------------------------------------------
    def _add_permissions(self, permission_name):
        # Add permission to user
        permission = Permission.objects.get(name=permission_name)
        self.normal_user.user_permissions.add(permission)
        self.normal_user.save()

