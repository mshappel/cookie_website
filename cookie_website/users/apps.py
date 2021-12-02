from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_migrate.connect(create_groups, sender=self)


def create_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    from cookie_booths.models import BoothBlock

    Group.objects.get_or_create(name='Troop Cookie Coordinator')
    # TODO: Add TCC permissions?

    # Normal users can reserve and cancel booth blocks. That's it.
    group, created = Group.objects.get_or_create(name='Users')
    content_type = ContentType.objects.get_for_model(BoothBlock)
    cancel_perm = Permission.objects.get(
        codename='cancel_block',
        content_type=content_type
    )
    reserve_perm = Permission.objects.get(
        codename='reserve_block',
        content_type=content_type
    )

    group.permissions.add(cancel_perm)
    group.permissions.add(reserve_perm)


