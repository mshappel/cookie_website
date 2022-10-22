# Generated by Django 3.2.6 on 2022-10-09 18:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cookie_booths", "0004_auto_20221009_0036"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="boothblock",
            options={
                "permissions": (
                    ("block_reservation", "Reserve/Cancel a booth"),
                    ("reserve_block", "Reserve a booth"),
                    (
                        "cookie_captain_reserve_block",
                        "Reserve a block for a daisy scout",
                    ),
                    (
                        "block_reservation_admin",
                        "Administrator reserve/cancel any booth, or hold booths for cookie captains to reserve",
                    ),
                )
            },
        ),
    ]
