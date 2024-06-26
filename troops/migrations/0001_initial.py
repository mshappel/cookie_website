# Generated by Django 3.2.6 on 2022-02-26 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Troop",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("troop_number", models.IntegerField(unique=True)),
                (
                    "troop_cookie_coordinator",
                    models.CharField(max_length=300, null=True),
                ),
                ("super_troop", models.BooleanField(default=False)),
                (
                    "troop_level",
                    models.SmallIntegerField(
                        choices=[
                            (0, "None"),
                            (1, "Daisies"),
                            (2, "Brownies"),
                            (3, "Juniors"),
                            (4, "Cadettes"),
                            (5, "Seniors"),
                            (6, "Ambassadors"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "total_booth_tickets_per_week",
                    models.PositiveSmallIntegerField(default=0),
                ),
                (
                    "booth_golden_tickets_per_week",
                    models.PositiveSmallIntegerField(default=0),
                ),
            ],
            options={
                "verbose_name": "troop",
                "verbose_name_plural": "troops",
            },
        ),
    ]
