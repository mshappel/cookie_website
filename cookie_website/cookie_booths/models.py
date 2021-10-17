from django.db import models


class Booths(models.Model):
    """Contains data relevant for booths"""
    # TODO Add Hours of Operation
    booth_location = models.CharField(max_length=300)
    booth_requires_masks = models.BooleanField()
    booth_is_outside = models.BooleanField()
    booth_free_text = models.CharField(max_length=100)
    booth_enabled = models.BooleanField()

    class Meta:
        verbose_name_plural = "booths"
        verbose_name = "booth"

    def __str__(self):
        return self.booth_location


class Booth_Day(models.Model):
    """Contains data relevant for a day of a booth"""
    booth = models.ForeignKey(Booths, on_delete=models.CASCADE)
    booth_day_enabled = models.BooleanField()
    booth_day_date = models.DateField()


class Booth_Block(models.Model):
    """Contains information for a particular booth block"""
    booth_day = models.ForeignKey(Booths, on_delete=models.CASCADE)
    booth_block_reserved = models.BooleanField()
    # TODO Determine if CharField is correct, we may need to change this to something else for the user accounts
    # booth_block_current_troop_owner = models.CharField(max_length=10)
    # Need time period
    booth_block_is_golden_ticket = models.BooleanField()
    booth_block_enabled = models.BooleanField()
