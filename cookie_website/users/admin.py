from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Troop


class UserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ['groups']


admin.site.register(User, UserAdmin)
admin.site.register(Troop)
