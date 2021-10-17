from django.contrib import admin

from .models import Booths, Booth_Day, Booth_Block

admin.site.register(Booths)
admin.site.register(Booth_Day)
admin.site.register(Booth_Block)