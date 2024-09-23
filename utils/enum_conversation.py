from enum import Enum
from typing import List, Tuple


def enum_choices_to_tuple(enum_class: Enum) -> List[Tuple[str, str]]:
    """
    Generate a list of choices from an enumeration class.

    Args:
        enum_class (Enum): The enumeration class to generate choices from.

    Returns:
        List[Tuple[str, str]]: A list of tuples where each tuple contains the value and name of an
        enumeration member.
    """
    choices: List[Tuple[str, str]] = []
    tag: Enum
    for tag in enum_class:
        choice: Tuple[str, str] = (tag.value, tag.name)
        choices.append(choice)
    return choices
