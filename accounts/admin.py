from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ChangeUserPreferences, CustomUserChangeForm, CustomUserCreationForm
from .models import Configuration, CustomUser, UserPreferences


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "first_name", "last_name"]
    list_filter = ["groups"]
    fieldsets = (
        (None, {"fields": ("email", "password", "first_name", "last_name")}),
        ("Permissions", {"fields": ("groups", "is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "groups",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ["tickets_per_week"]


class UserPreferencesAdmin(admin.ModelAdmin):

    form = ChangeUserPreferences
    model = UserPreferences
    list_display = ["email", "phone_number", "communication_preference"]
    fieldsets = ((None, {"fields": ("email", "phone_number", "communication_preference")}),)
    add_fieldsets = (
        (
            None,
            {"classes": ("wide",), "fields": ("email", "phone_number", "communication_preference")},
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
