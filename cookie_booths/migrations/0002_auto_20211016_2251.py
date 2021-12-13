# Generated by Django 3.2.6 on 2021-10-17 03:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cookie_booths', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booths',
            options={'verbose_name': 'booth', 'verbose_name_plural': 'booths'},
        ),
        migrations.CreateModel(
            name='Booth_Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booth_day_enabled', models.BooleanField()),
                ('booth_day_date', models.DateField()),
                ('booth', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cookie_booths.booths')),
            ],
        ),
        migrations.CreateModel(
            name='Booth_Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booth_block_reserved', models.BooleanField()),
                ('booth_block_is_golden_ticket', models.BooleanField()),
                ('booth_block_enabled', models.BooleanField()),
                ('booth_day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cookie_booths.booths')),
            ],
        ),
    ]