from enum import Enum
from action_choices import call, bet, raise_bet, check, fold


class Action(Enum):
    NONE = -1
    CALL = 0
    BET = 1
    RAISE_BET = 2
    CHECK = 3
    FOLD = 4
    ALL_IN = 5
    SMALL_BLIND = 6
    BIG_BLIND = 7
    LOST = 8



