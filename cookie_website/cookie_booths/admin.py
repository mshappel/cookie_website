from django.contrib import admin

from .models import Booth_Location, Booth_Day, Booth_Block

admin.site.register(Booth_Location)
admin.site.register(Booth_Day)
admin.site.register(Booth_Block)