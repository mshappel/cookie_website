from troops.tests.troop_class_reference import TroopTestCase
from troops.forms import TroopForm

class TroopFormsTestCases(TroopTestCase):
    def test_troops_form_with_valid_data(self):
        # Provide valid data and check if the form declares it is valid
        form_data = {
            'troop_number': self.LARGE_TROOP['number'],
            'troop_cookie_coordinator': self.LARGE_TROOP['tcc'],
            'troop_level': self.LARGE_TROOP['level'],
            'troop_size': self.LARGE_TROOP['troop_size'],
        }
        form = TroopForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_troops_form_with_invalid_data(self):
        # Test to be sure that troop numbers are unique; check if the user receives the correct error message
        form_data = {
            'troop_number': self.SMALL_TROOP['number'],
            'troop_cookie_coordinator': self.LARGE_TROOP['tcc'],
            'troop_level': self.LARGE_TROOP['level'],
            'troop_size': self.LARGE_TROOP['troop_size'],
        }
        form = TroopForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['troop_number'],
                            ["Troop number is already taken. Please choose a unique troop number."])