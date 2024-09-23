from typing import TYPE_CHECKING, List, Optional

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Q, QuerySet
from django.utils.timezone import datetime

from accounts.models import CustomUser as User
from troops.models import Troop
from utils.date_utils import get_week_start_end_from_date

if TYPE_CHECKING:
    from cookie_booths.models import BoothDay, BoothTimeBlock

ORDERING_FIELDS = ["booth_day__booth", "booth_day", "booth_block_start_time"]


class BoothTimeBlockManager(models.Manager):

    def get_booth_blocks_for_day(self, booth_day: "BoothDay"):
        """Returns the BoothBlock instances associated with the given BoothDay."""
        return self.filter(booth_day=booth_day)

    def order_booth_blocks(self) -> QuerySet:
        """
        Orders the booth blocks.

        Returns:
            QuerySet: The ordered booth blocks.
        """
        return self._select_and_order_booth_blocks(self)

    def get_block_to_reserve(self, block_id: int) -> "BoothTimeBlock":
        """
        Retrieves a booth block to reserve based on the given block ID.

        Parameters:
            block_id (int): The ID of the booth block to retrieve.

        Returns:
            BoothBlock: The booth block to reserve.
        """
        block = self.select_related("booth_day__booth").get(id=block_id)
        return block

    def is_owner_cookie_captain(self, block: "BoothTimeBlock") -> bool:
        """
        Check if the owner of the object is a cookie captain.

        Returns:
            bool: True if the owner is a custom user, False otherwise.
        """
        owner = block.booth_block_current_owner
        return owner.is_cookie_captain

    def get_current_owner_email(self, block: "BoothTimeBlock") -> str:
        """
        Get the email of the current owner of the booth block.

        Returns:
            str: The email of the current owner of the booth block.
        """
        return block.booth_block_current_owner.email

    def get_cookie_captain_name_and_email(self, block: "BoothTimeBlock") -> tuple:
        """
        Get the name and email of the cookie captain for the booth block.

        Returns:
            tuple: A tuple containing the name and email of the cookie captain.
        """
        captain: User = block.booth_block_current_owner
        return captain.get_full_name(), captain.email

    def get_cookie_captain_email_message(self, booth_block: "BoothTimeBlock"):
        cookie_captain_name, cookie_captain_email = self.get_cookie_captain_name_and_email(
            booth_block
        )
        return f"Cookie Captain: {cookie_captain_name} || " f"Contact: {cookie_captain_email}"

    def block_owned_by_requester(
        self,
        block: "BoothTimeBlock",
        request_user: User,
        is_daisy: Optional[bool] = False,
    ) -> bool:
        """
        Check if the booth block is owned by the requester.

        Returns:
            bool: True if the booth block is owned by the requester, False otherwise.
        """
        if is_daisy:
            return block.booth_block_daisy_troop_owner == request_user
        else:
            return block.booth_block_current_owner == request_user

    def retrieve_and_process_booth_information(
        self,
        time_threshold: datetime,
        request_user: User,
    ) -> list:
        """
        Retrieve booth blocks, create booth information list, and process each booth block.

        Args:
            is_daisy_troop (bool): Whether the user is part of a daisy troop.
            is_cookie_captain (bool): Whether the user is a cookie captain.
            time_threshold (datetime): The time threshold for filtering booth blocks.
            owner (User): The owner of the booth blocks.
            request_user (User): The user making the request.

        Returns:
            list: A list of processed booth information dictionaries.
        """
        requestor_email: str = request_user.email
        is_cookie_captain: bool = request_user.is_cookie_captain
        is_daisy_troop: bool = Troop.objects.is_daisy_troop_by_email(requestor_email)

        # Retrieve booth blocks with combined filters
        selected_booth_blocks = self.retrieve_booth_blocks(
            is_daisy_troop=is_daisy_troop,
            is_cookie_captain=is_cookie_captain,
            time_threshold=time_threshold,
        )

        # Initialize booth information list
        booth_information: List["BoothTimeBlock"] = self.create_booth_information_list(
            selected_booth_blocks=selected_booth_blocks,
            requestor_email=requestor_email,
            is_cookie_captain=is_cookie_captain,
        )

        # Process each booth block to determine its state and permissions
        processed_booth_information = []
        for block in booth_information:
            block_info = {
                "booth_block_information": block,
                "booth_block_reserved": block.booth_block_reserved,
                "booth_block_held_for_cookie_captains": block.booth_block_held_for_cookie_captains,
                "booth_owned_by_cookie_captain": block.objects.is_owner_cookie_captain(block),
                "booth_block_daisy_reserved": block.booth_block_daisy_reserved,
                "booth_block_daisy_troop_owner": block.booth_block_daisy_troop_owner,
                "booth_block_cookie_captain_email": block.objects.get_current_owner_email(block),
                "booth_owned_by_current_user": self.block_owned_by_requester(
                    block=block, request_user=request_user
                ),
            }
            processed_booth_information.append(block_info)

        return processed_booth_information

    def create_booth_information_list(
        self, selected_booth_blocks: QuerySet, requestor_email: str, is_cookie_captain: bool
    ):
        """
        Create a list of booth information from the selected booth blocks.

        Args:
            selected_booth_blocks (QuerySet): The selected booth blocks.
            owner (User): The owner of the booth blocks.
            is_cookie_captain (bool): Whether the user is a cookie captain.

        Returns:
            list: A list of booth information dictionaries.
        """
        booth_information = []
        for booth in selected_booth_blocks:
            current_booth_information = self.create_booth_information(
                booth_block=booth,
                requestor_email=requestor_email,
                is_cookie_captain=is_cookie_captain,
            )
            booth_information.append(current_booth_information)
        return booth_information

    def create_booth_information(
        self, booth_block: "BoothTimeBlock", requestor_email: str, is_cookie_captain: bool
    ):
        """
        Creates booth information dictionary.
        Args:
            booth_block (BoothBlock): The booth block object.
            owner: The owner of the booth.
            is_cookie_captain (bool): Indicates if the owner is a cookie captain.
        Returns:
            dict: A dictionary containing booth information with the following keys:
                - "booth_block_information": The booth block object.
                - "booth_owned_by_current_user": Indicates if the booth is owned by the current user.
                - "booth_owned_by_cookie_captain": Indicates if the booth is owned by a cookie captain.
                - "booth_block_cookie_captain_email": The email message of the cookie captain, if applicable.
        """
        booth_owned_by_current_user = self.is_booth_owned_by_current_user(
            booth_block, requestor_email, is_cookie_captain
        )
        booth_owned_by_cookie_captain = self.is_owner_cookie_captain(booth_block)
        if booth_owned_by_cookie_captain:
            cookie_cap_email_message = self.get_cookie_captain_email_message(booth_block)
        else:
            cookie_cap_email_message = None

        return {
            "booth_block_information": booth_block,
            "booth_owned_by_current_user": booth_owned_by_current_user,
            "booth_owned_by_cookie_captain": booth_owned_by_cookie_captain,
            "booth_block_cookie_captain_email": cookie_cap_email_message,
        }

    def is_booth_owned_by_current_user(
        self,
        booth: "BoothTimeBlock",
        owner,
        is_cookie_captain: bool,
    ) -> bool:
        """
        Determines if a booth is owned by the current user.
        Args:
            booth (BoothBlock): The booth to check ownership for.
            owner: The owner to compare against.
            is_cookie_captain (bool): Flag indicating if the owner is a cookie captain.
        Returns:
            bool: True if the booth is owned by the current user, False otherwise.
        """
        booth_owner = booth.booth_block_current_owner
        daisy_booth_owner = booth.booth_block_daisy_troop_owner
        is_owned_by_booth_owner = booth_owner == owner
        is_owned_by_daisy_troop_owner = daisy_booth_owner == owner

        if owner is None:
            return False
        elif is_cookie_captain:
            return is_owned_by_booth_owner
        else:
            return is_owned_by_booth_owner or is_owned_by_daisy_troop_owner

    def retrieve_booth_blocks(
        self,
        is_daisy_troop: bool,
        is_cookie_captain: bool,
        time_threshold: datetime,
    ) -> QuerySet:
        """
        Retrieve booth blocks based on user type, time threshold, and ordering fields.

        This method filters booth blocks based on whether the user is part of a Daisy troop,
        is a cookie captain, and an optional time threshold. It also allows for ordering
        the results based on specified fields.

        Args:
            is_daisy_troop (bool): Indicates if the user is part of a Daisy troop.
            is_cookie_captain (bool): Indicates if the user is a cookie captain.
            time_threshold (datetime): A datetime object to filter booth blocks starting after this time.

        Returns:
            QuerySet: A Django QuerySet of booth blocks that match the filter criteria.
        """

        booth_block_filter = self._get_booth_block_filter(
            is_daisy_troop, is_cookie_captain, time_threshold
        )
        queryset = self.filter(booth_block_filter, booth_block_enabled=True)
        queryset = queryset.select_related("booth_day", "owner_content_type")
        return self._select_and_order_booth_blocks(queryset)

    def total_booth_count_for_cookie_captain(
        self,
        cookie_captain_id: int,
        date: datetime.date,
    ) -> int:
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

    def aggregated_booth_count_for_troop(self, troop_id: Troop, date: datetime.date) -> dict:
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

    def _select_and_order_booth_blocks(self, queryset: QuerySet) -> QuerySet:
        return queryset.select_related("booth_day", "booth_day__booth").order_by(*ORDERING_FIELDS)

    def _get_booth_block_filter(
        self,
        is_daisy_troop: bool,
        is_cookie_captain: bool,
        time_threshold: datetime,
    ) -> Q:
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

    def _get_base_ticket_filter(self, date: datetime.date) -> Q:
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
