# Generated by Django 3.2.6 on 2022-12-11 21:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userpreferences'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userpreferences',
            old_name='user',
            new_name='email',
        ),
    ]
