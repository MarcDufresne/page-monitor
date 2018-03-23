from enum import Enum
from typing import NamedTuple


class CONDITION_TYPE(Enum):
    TEXT = 'text'
    ADDED_TEXT = 'added_text'
    PREVIOUS_TEXT = 'removed_text'


class CONDITION(Enum):
    NOT_EMPTY = 'not_empty'
    HAS = 'has'
    DOES_NOT_HAVE = 'does_not_have'
    MATCHES_REGEX = 'matches_regex'


class Condition(NamedTuple):
    cond_type: str
    cond: str
    rule: str
