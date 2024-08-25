from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Q

from accounts.models import CustomUser as User
from troops.models import Troop
from utils.date_utils import get_week_start_end_from_date


class BoothBlockManager(models.Manager):
    def get_block_to_reserve(self, block_id):
        block = self.select_related("booth_day__booth").get(id=block_id)
        return block

    def retrieve_booth_blocks(
        self, is_daisy_troop, is_cookie_captain, time_threshold, ordering_fields
    ):
        """
        Retrieve booth blocks based on user type, time threshold, and ordering fields.

        This method filters booth blocks based on whether the user is part of a Daisy troop,
        is a cookie captain, and an optional time threshold. It also allows for ordering
        the results based on specified fields.

        Args:
            is_daisy_troop (bool): Indicates if the user is part of a Daisy troop.
            is_cookie_captain (bool): Indicates if the user is a cookie captain.
            time_threshold (datetime): A datetime object to filter booth blocks starting after this time.
            ordering_fields (list): A list of fields to order the results by.

        Returns:
            QuerySet: A Django QuerySet of booth blocks that match the filter criteria.
        """
        booth_block_filter = self._get_booth_block_filter(
            is_daisy_troop, is_cookie_captain, time_threshold
        )
        return (
            self.filter(booth_block_filter, booth_block_enabled=True)
            .select_related("booth_day", "booth_day__booth")
            .order_by(*ordering_fields)
        )

    def total_booth_count_for_cookie_captain(self, cookie_captain_id, date):
        """
        Calculate the total number of booth blocks for a given cookie captain on a specified date.

        This method generates a base filter for the given date, applies an additional filter
        based on the cookie captain's ID, and then counts the total number of booth blocks
        that match the criteria.

        Args:
            cookie_captain_id (int): The ID of the cookie captain.
            date (datetime.date): The date for which to calculate the booth count.

        Returns:
            int: The total number of booth blocks for the specified cookie captain on the given date.
        """
        base_filter = self._get_base_ticket_filter(date)
        return self.filter(
            base_filter & Q(booth_block_current_cookie_captain_owner=cookie_captain_id)
        ).count()

    def aggregated_booth_count_for_troop(self, troop_id: Troop, date):
        """
        Calculate the aggregated booth counts for a given troop on a specified date.

        This method generates a base filter for the given date, applies additional filters
        based on the troop's level and number, and then aggregates the total booth count
        and the count of golden ticket booths.

        Args:
            troop_id (Troop): The troop object containing the troop's level and number.
            date (datetime.date): The date for which to calculate the booth counts.

        Returns:
            dict: A dictionary containing the aggregated booth counts with the following keys:
                - total_booth_count: The total number of booths for the troop.
                - golden_ticket_booth_count: The number of golden ticket booths for the troop.
        """
        base_filter = self._get_base_ticket_filter(date)
        if troop_id.troop_level == 1:
            troop_filter = Q(booth_block_daisy_troop_owner=troop_id.troop_number)
        else:
            troop_filter = Q(booth_block_current_troop_owner=troop_id.troop_number)

        blocks_aggregated = self.filter(base_filter & troop_filter).aggregate(
            total_booth_count=Count("id"),
            golden_ticket_booth_count=Count("id", filter=Q(booth_day__booth_day_is_golden=True)),
        )

        return blocks_aggregated

    def _get_booth_block_filter(self, is_daisy_troop, is_cookie_captain, time_threshold):
        """
        Generate a filter for booth blocks based on user type and time threshold.

        This method constructs a Q object to filter booth blocks based on whether the user
        is part of a Daisy troop, is a cookie captain, and an optional time threshold.

        Args:
            is_daisy_troop (bool): Indicates if the user is part of a Daisy troop.
            is_cookie_captain (bool): Indicates if the user is a cookie captain.
            time_threshold (datetime): A datetime object to filter booth blocks starting after this time.

        Returns:
            Q: A Django Q object representing the filter criteria.
        """
        custom_user_type = ContentType.objects.get_for_model(User)
        common_filter = Q(booth_block_enabled=True)

        if time_threshold:
            common_filter &= Q(booth_block_start_time__gt=time_threshold)

        if is_daisy_troop:
            return (
                common_filter
                & Q(owner_content_type=custom_user_type)
                & Q(booth_block_reserved=True)
            )
        elif is_cookie_captain:
            return common_filter
        else:
            return common_filter & ~Q(booth_block_held_for_cookie_captains=True)

    def _get_base_ticket_filter(self, date):
        """
        Generate a base filter for tickets based on the given date.

        This method calculates the start and end dates of the week containing the given date
        and returns a Q object that filters booth blocks which are reserved and fall within
        the specified date range.

        Args:
            date (datetime.date): The date for which to generate the filter.

        Returns:
            Q: A Django Q object representing the filter criteria.
        """
        start_date, end_date = get_week_start_end_from_date(date)
        return Q(
            booth_block_reserved=True,
            booth_day__booth_day_date__gte=start_date,
            booth_day__booth_day_date__lte=end_date,
        )
