# Generated by Django 3.2.6 on 2021-12-15 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cookie_booths", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="boothblock",
            name="booth_block_current_troop_owner",
            field=models.IntegerField(default=0),
        ),
    ]
