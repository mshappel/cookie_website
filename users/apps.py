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

    from cookie_booths.models import BoothBlock, BoothLocation, BoothDay
    from .models import Troop

    # Common permissions for most groups
    content_type = ContentType.objects.get_for_model(BoothBlock)
    cancel_perm, created = Permission.objects.get_or_create(
        codename='cancel_block',
        content_type=content_type
    )
    reserve_perm, created = Permission.objects.get_or_create(
        codename='reserve_block',
        content_type=content_type
    )

    # Normal users can reserve and cancel booth blocks.
    group, created = Group.objects.get_or_create(name='Users')
    group.permissions.add(cancel_perm)
    group.permissions.add(reserve_perm)

    # TCCs can also reserve and cancel booth blocks, BUT it should only be added after the draft
    group, created = Group.objects.get_or_create(name='Troop Cookie Coordinator')
    #group.permissions.add(cancel_perm)
    #group.permissions.add(reserve_perm)

    # SUCMs can do everything except for deleting troops or booths
    group, created = Group.objects.get_or_create(name='SUCM')
    # Booth Block Permissions
    cancel_perm_admin, created = Permission.objects.get_or_create(
        codename='reserve_block_admin',
        content_type=content_type
    )
    reserve_perm_admin, created = Permission.objects.get_or_create(
        codename='reserve_block_admin',
        content_type=content_type
    )

    group.permissions.add(cancel_perm)
    group.permissions.add(reserve_perm)
    group.permissions.add(cancel_perm_admin)
    group.permissions.add(reserve_perm_admin)

    # Booth Day Permissions
    content_type = ContentType.objects.get_for_model(BoothDay)
    enable_day_perm, created = Permission.objects.get_or_create(
        codename='enable_day',
        content_type=content_type
    )
    disable_day_perm, created = Permission.objects.get_or_create(
        codename='disable_day',
        content_type=content_type
    )
    update_hours_perm, created = Permission.objects.get_or_create(
        codename='add_or_update_hours',
        content_type=content_type
    )
    make_golden_perm, created = Permission.objects.get_or_create(
        codename='make_golden_booth',
        content_type=content_type
    )
    enable_ffa_perm, created = Permission.objects.get_or_create(
        codename='enable_freeforall',
        content_type=content_type
    )
    disable_ffa_perm, created = Permission.objects.get_or_create(
        codename='disable_freeforall',
        content_type=content_type
    )

    group.permissions.add(enable_day_perm)
    group.permissions.add(disable_day_perm)
    group.permissions.add(update_hours_perm)
    group.permissions.add(make_golden_perm)
    group.permissions.add(enable_ffa_perm)
    group.permissions.add(disable_ffa_perm)

    # Booth Location Permissions
    content_type = ContentType.objects.get_for_model(BoothLocation)
    create_loc_perm, created = Permission.objects.get_or_create(
        codename='booth_loc_creation',
        content_type=content_type
    )
    update_loc_perm, created = Permission.objects.get_or_create(
        codename='booth_loc_updates',
        content_type=content_type
    )

    group.permissions.add(create_loc_perm)
    group.permissions.add(update_loc_perm)

    # Troop Permissions
    content_type = ContentType.objects.get_for_model(Troop)
    create_troop_perm, created = Permission.objects.get_or_create(
        codename='troop_creation',
        content_type=content_type
    )
    update_troop_perm, created = Permission.objects.get_or_create(
        codename='troop_updates',
        content_type=content_type
    )

    group.permissions.add(create_troop_perm)
    group.permissions.add(update_troop_perm)

