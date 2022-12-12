from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


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
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


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
        return reverse('user_preferences', kwargs={'pk': self.email.pk})

    def clean(self):
        if not self.phone_number:
            if self.communication_preference:
                raise ValidationError({'communication_preference': "Can only select Text if Phone Number Exists."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

@receiver(post_save, sender=CustomUser)
def generate_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(email=instance)
    else:
        return
