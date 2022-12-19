from django.contrib import admin

from .models import BoothHours, BoothLocation, BoothDay, BoothBlock, CookieSeason

admin.site.register(BoothHours)
admin.site.register(BoothLocation)
admin.site.register(BoothDay)
admin.site.register(BoothBlock)
admin.site.register(CookieSeason)
