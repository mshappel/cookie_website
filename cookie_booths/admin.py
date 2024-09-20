from django.contrib import admin

from cookie_booths.models.daily_attributes import BoothDailyAttributes
from cookie_booths.models.blocks import BoothBlock
from cookie_booths.models.day import BoothDay
from cookie_booths.models.location import BoothLocation
from cookie_booths.models.season import CookieSeason

admin.site.register(BoothDailyAttributes)
admin.site.register(BoothLocation)
admin.site.register(BoothDay)
admin.site.register(BoothBlock)
admin.site.register(CookieSeason)
