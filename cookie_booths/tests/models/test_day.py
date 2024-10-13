# from datetime import datetime, time

# from django.test import TestCase

# from cookie_booths.models.day import BoothDay
# from cookie_booths.models.location import BoothLocation


# class BoothDayTestCase(TestCase):
#     def setUp(self):
#         self.location: BoothLocation = BoothLocation.objects.create(name="Test Location")
#         self.booth_day: BoothDay = BoothDay.objects.create(
#             booth_location=self.location, booth_day_date=datetime.now().date()
#         )

#     def test_update_golden_status(self):
#         self.booth_day.update_golden_status(True)
#         self.assertTrue(self.booth_day.booth_day_is_golden)
#         self.booth_day.update_golden_status(False)
#         self.assertFalse(self.booth_day.booth_day_is_golden)

#     def test_enable_day(self):
#         self.booth_day.enable_day()
#         self.assertTrue(self.booth_day.booth_day_enabled)

#     def test_disable_day(self):
#         self.booth_day.disable_day()
#         self.assertFalse(self.booth_day.booth_day_enabled)

#     def test_enable_freeforall(self):
#         self.booth_day.enable_freeforall()
#         self.assertTrue(self.booth_day.booth_day_freeforall_enabled)

#     def test_disable_freeforall(self):
#         self.booth_day.disable_freeforall()
#         self.assertFalse(self.booth_day.booth_day_freeforall_enabled)

#     def test_add_or_update_hours(self):
#         open_time = datetime.now()
#         close_time = datetime.now()
#         self.booth_day.add_or_update_hours(open_time, close_time)
#         self.assertEqual(self.booth_day.booth_day_open_time, open_time)
#         self.assertEqual(self.booth_day.booth_day_close_time, close_time)

#     def test_update_day(self):
#         open_time = time(9, 0)
#         close_time = time(17, 0)
#         self.booth_day.update_day(open_time, close_time, True)
#         self.assertTrue(self.booth_day.booth_day_is_golden)
#         self.assertEqual(self.booth_day.booth_day_open_time.time(), open_time)
#         self.assertEqual(self.booth_day.booth_day_close_time.time(), close_time)
