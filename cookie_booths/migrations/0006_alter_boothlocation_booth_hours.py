# Generated by Django 3.2.8 on 2021-11-06 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cookie_booths', '0005_alter_boothlocation_booth_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boothlocation',
            name='booth_hours',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cookie_booths.boothhours'),
        ),
    ]