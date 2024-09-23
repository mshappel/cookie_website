from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class AccountType(models.TextChoices):
    COOKIE_CAPTAIN = "cookie_captain", _("Cookie Captain")
    COOKIE_ADMIN = "cookie_admin", _("Cookie Admin")
    COOKIE_STAFF = "cookie_staff", _("Cookie Staff")
    TCC = "tcc", _("TCC")
    UNASSIGNED = "unassigned", _("Unassigned")


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.UNASSIGNED,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_permission(self, permission):
        permissions = {
            AccountType.COOKIE_CAPTAIN: ["reserve_block_captain"],
            AccountType.COOKIE_ADMIN: ["reserve_block_admin", "manage_users", "update_booth_day"],
            AccountType.TCC: ["reserve_block_tcc", "edit_tcc_data"],
            AccountType.COOKIE_STAFF: ["update_booth_day"],
        }
        return permission in permissions.get(self.account_type, [])

    @cached_property
    def cached_account_type(self):
        return self.account_type

    @property
    def is_cookie_captain(self):
        return self.cached_account_type == AccountType.COOKIE_CAPTAIN

    @property
    def is_admin(self):
        return self.cached_account_type == AccountType.COOKIE_ADMIN

    @property
    def is_tcc(self):
        return self.cached_account_type == AccountType.TCC

    @property
    def is_cookie_staff(self):
        return self.cached_account_type == AccountType.COOKIE_STAFF

    @property
    def can_edit_booths(self):
        return self.is_admin or self.is_cookie_staff


class CookieCaptain(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    tickets = models.IntegerField(default=3)

    class Meta:
        verbose_name = "Cookie Captain"
        verbose_name_plural = "Cookie Captains"

    # Add any additional fields or methods specific to Cookie Captain


class CookieAdmin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name = "Cookie Admin"
        verbose_name_plural = "Cookie Admins"

    # Add any additional fields or methods specific to Cookie Admin


class TCC(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name = "TCC"
        verbose_name_plural = "TCCs"

    # Add any additional fields or methods specific to TCC


class CookieStaff(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name = "Cookie Staff"
        verbose_name_plural = "Cookie Staff"

    # Add any additional fields or methods specific to Cookie Staff


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance: CustomUser, created, **kwargs):
    if created:
        if instance.is_cookie_captain:
            CookieCaptain.objects.create(user=instance)
        elif instance.is_admin:
            CookieAdmin.objects.create(user=instance)
        elif instance.is_tcc:
            TCC.objects.create(user=instance)
        elif instance.is_cookie_staff:
            CookieStaff.objects.create(user=instance)
    else:
        if instance.is_cookie_captain:
            CookieCaptain.objects.get_or_create(user=instance)
        elif instance.is_admin:
            CookieAdmin.objects.get_or_create(user=instance)
        elif instance.is_tcc:
            TCC.objects.get_or_create(user=instance)
        elif instance.is_cookie_staff:
            CookieStaff.objects.get_or_create(user=instance)


class UserPreferences(models.Model):
    class Meta:
        verbose_name_plural = "User Preferences"

    email = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    phone_number = PhoneNumberField(region="US", blank=True, default=None, null=True)
    communication_preference = models.SmallIntegerField(
        choices=[(0, "Email"), (1, "Text")], default=0
    )

    def __str__(self) -> str:
        return self.email.email

    def get_absolute_url(self):
        return reverse("user_preferences", kwargs={"pk": self.email.pk})

    def clean(self):
        if not self.phone_number:
            if self.communication_preference:
                raise ValidationError(
                    {"communication_preference": "Can only select Text if Phone Number Exists."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


@receiver(post_save, sender=CustomUser)
def generate_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(email=instance)
    else:
        return
