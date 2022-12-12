from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "first_name",
        "last_name"
    ]
    list_filter = ["groups"]
    fieldsets = (
        (None, {'fields': ('email', 'password', "first_name", "last_name")}),
        ('Permissions', {'fields': ('groups', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', "first_name", "last_name", 'password1', 'password2', 'groups', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email','first_name', 'last_name')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
