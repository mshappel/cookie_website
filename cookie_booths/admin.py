from django.contrib import admin

from cookie_booths.models.time_block import BoothTimeBlock
from cookie_booths.models.day import BoothDay
from cookie_booths.models.location import BoothLocation
from cookie_booths.models.schedule import BoothSchedule
from cookie_booths.models.season import CookieSeason

admin.site.register(BoothSchedule)
admin.site.register(BoothLocation)
admin.site.register(BoothDay)
admin.site.register(BoothTimeBlock)
admin.site.register(CookieSeason)
