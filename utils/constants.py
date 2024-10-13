from enum import Enum

# Project Level Constants
GIRL_SCOUT_TROOP_LEVELS_WITH_NONE = [
    (0, "None"),
    (1, "Daisies"),
    (2, "Brownies"),
    (3, "Juniors"),
    (4, "Cadettes"),
    (5, "Seniors"),
    (6, "Ambassadors"),
]
DAYS_OF_WEEK = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]

GOLDEN_TICKET_DAYS = [5, 6]  # Saturday and Sunday

WEEKDAY_MAPPING = [day.lower() for _, day in DAYS_OF_WEEK]

NO_COOKIE_CAPTAIN_ID = 0
NO_DAISY_TROOP = 0


class ReservationAction(Enum):
    RESERVED = "reserved"
    UNRESERVED = "unreserved"


class GirlScoutTroopLevel(Enum):
    NONE = 0
    DAISIES = 1
    BROWNIES = 2
    JUNIORS = 3
    CADETTES = 4
    SENIORS = 5
    AMBASSADORS = 6


class DayOfWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


GOLDEN_TICKET_LIST = [DayOfWeek.SATURDAY.name.lower(), DayOfWeek.SUNDAY.name.lower()]
