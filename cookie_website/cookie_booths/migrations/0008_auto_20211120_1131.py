# Generated by Django 3.2.8 on 2021-11-20 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cookie_booths', '0007_auto_20211106_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='boothblock',
            name='booth_block_freeforall_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='boothday',
            name='booth_day_freeforall_enabled',
            field=models.BooleanField(default=False),
        ),
    ]