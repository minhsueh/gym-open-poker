from enum import Enum
from action_choices import call, bet, raise_bet, check, fold


class Action(Enum):
    NONE = -1
    CALL = 0
    BET = 1
    RAISE_BET = 2
    CHECK = 3
    FOLD = 4
    SMALL_BLIND = 5
    BIG_BLIND = 6


