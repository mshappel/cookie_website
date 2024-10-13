# from datetime import datetime
# from django.test import TestCase
# from cookie_booths.models.time_block import BoothTimeBlock
# from cookie_booths.models.season import CookieSeason
# from cookie_booths.models.day import BoothDay
# from troops.models import Troop
# from accounts.models import CustomUser as User


# class BoothTimeBlockTests(TestCase):

#     def setUp(self):
#         self.booth_day = BoothDay.objects.create(name="Test Day")
#         self.time_block = BoothTimeBlock.objects.create(
#             booth_day=self.booth_day,
#             booth_block_start_time=datetime(2023, 1, 1, 10, 0),
#             booth_block_end_time=datetime(2023, 1, 1, 12, 0),
#             booth_block_enabled=True,
#             booth_block_freeforall_enabled=False,
#         )
#         self.troop = Troop.objects.create(name="Test Troop", troop_level=1)
#         self.user = User.objects.create_user(email="test@example.com", password="password")

#     def test_str_method(self):
#         self.assertEqual(str(self.time_block), "Test Day from 10 to 12")

#     def test_is_reserved(self):
#         self.assertFalse(self.time_block.is_reserved())

#     def test_passes_level_restrictions(self):
#         self.booth_day.booth_location.booth_block_level_restrictions_start = 1
#         self.booth_day.booth_location.booth_block_level_restrictions_end = 3
#         self.assertTrue(self.time_block.passes_level_restrictions(troop_level=2))

#     def test_is_reservable_within_cookie_season(self):
#         cookie_season = CookieSeason.objects.create(name="Test Season", start_date="2023-01-01", end_date="2023-12-31")
#         self.assertTrue(self.time_block.is_reservable_within_cookie_season(cookie_season=cookie_season))

#     def test_can_be_reserved_by_troop(self):
#         self.assertTrue(self.time_block.can_be_reserved_by_troop(troop=self.troop))

#     def test_can_be_reserved_by_daisy_troop(self):
#         self.troop.is_daisy_troop = True
#         self.assertTrue(self.time_block.can_be_reserved_by_daisy_troop(troop=self.troop))

#     def test_can_be_reserved_by_cookie_captain(self):
#         self.user.is_cookie_captain = True
#         self.assertTrue(self.time_block.can_be_reserved_by_cookie_captain(user=self.user))

#     def test_create_reservation(self):
#         reservation = self.time_block.create_reservation(user=self.user, troop=self.troop)
#         self.assertIsNotNone(reservation)

#     def test_delete_reservation(self):
#         self.time_block.create_reservation(user=self.user, troop=self.troop)
#         self.assertTrue(self.time_block.delete_reservation(user=self.user, troop=self.troop))