from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save


# User-related Models
class User(AbstractUser):
    pass

    @property
    def full_name(self):
        """Returns the person's full name"""
        return '%s %s' % (self.first_name, self.last_name)


class Troop(models.Model):
    troop_cookie_coordinator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    troop_number = models.PositiveSmallIntegerField(unique=True)
    super_troop = models.BooleanField(default=False)
    daisy_troop = models.BooleanField(default=False)

    booth_tickets_per_week = models.PositiveSmallIntegerField(default=0)
    booth_golden_tickets_per_week = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return 'Troop ' + str(self.troop_number)


def default_group(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(Group.objects.get(name='Troop Cookie Coordinator'))


post_save.connect(default_group, sender=User)
# Groups
# Administrators
# Service Unit Cookie Coordinator
# Service Unit Booth Coordinator
# Service Unit Cookie Captain Coordinator
# Troop Cookie Coordinator
