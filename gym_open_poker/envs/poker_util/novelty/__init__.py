"""
from gym_open_poker.envs.poker_util.novelty.action1 import Action1
from gym_open_poker.envs.poker_util.novelty.card_dist_high import CardDistHigh
from gym_open_poker.envs.poker_util.novelty.card_dist_low import CardDistLow
from gym_open_poker.envs.poker_util.novelty.card1 import Card1


# from gym_open_poker.envs.poker_util.novelty import conclude_game
from gym_open_poker.envs.poker_util.novelty.environment2 import Environment2
from gym_open_poker.envs.poker_util.novelty.agent1 import Agent1
from gym_open_poker.envs.poker_util.novelty.agent2 import Agent2
from gym_open_poker.envs.poker_util.novelty.agent3 import Agent3
from gym_open_poker.envs.poker_util.novelty.event1 import Event1

# from .rule1 import Rule1
from gym_open_poker.envs.poker_util.novelty.rule2 import Rule2
from gym_open_poker.envs.poker_util.novelty.rule3 import Rule3
from gym_open_poker.envs.poker_util.novelty.event2 import Event2
from gym_open_poker.envs.poker_util.novelty.rule4 import Rule4
from gym_open_poker.envs.poker_util.novelty.card2 import Card2
from gym_open_poker.envs.poker_util.novelty.card3 import Card3
"""

import os


# card
from gym_open_poker.envs.poker_util.novelty.card.card_dist_high import CardDistHigh
from gym_open_poker.envs.poker_util.novelty.card.card_dist_low import CardDistLow
from gym_open_poker.envs.poker_util.novelty.card.card_dist_suit import CardDistSuit
from gym_open_poker.envs.poker_util.novelty.card.card_dist_odd import CardDistOdd
from gym_open_poker.envs.poker_util.novelty.card.card_dist_color import CardDistColor

# conclude_game
from gym_open_poker.envs.poker_util.novelty.conclude_game.incentive import Incentive
from gym_open_poker.envs.poker_util.novelty.conclude_game.tipping import Tipping
from gym_open_poker.envs.poker_util.novelty.conclude_game.seat_changing import SeatChanging
from gym_open_poker.envs.poker_util.novelty.conclude_game.lucky_seven import LuckySeven
from gym_open_poker.envs.poker_util.novelty.conclude_game.hidden_card import HiddenCard

# game_element
from gym_open_poker.envs.poker_util.novelty.game_element.all_odd import AllOdd
from gym_open_poker.envs.poker_util.novelty.game_element.big_blind_change import BigBlindChange
from gym_open_poker.envs.poker_util.novelty.game_element.big_bet_change import BigBetChange
from gym_open_poker.envs.poker_util.novelty.game_element.buy_in import BuyIn
from gym_open_poker.envs.poker_util.novelty.game_element.tournament_length import TournamentLength

# agent
from gym_open_poker.envs.poker_util.novelty.agent.agent_exchange import AgentExchange
from gym_open_poker.envs.poker_util.novelty.agent.agent_add_r import AddAgentR
from gym_open_poker.envs.poker_util.novelty.agent.agent_add_conservative import AddAgentConservative
from gym_open_poker.envs.poker_util.novelty.agent.agent_add_aggressive import AddAgentAggressive
from gym_open_poker.envs.poker_util.novelty.agent.agent_add_stirring import AddAgentStirring


# action
from gym_open_poker.envs.poker_util.novelty.action.game_fold_restrict import GameFoldRestrict
from gym_open_poker.envs.poker_util.novelty.action.no_free_lunch import NoFreeLunch
from gym_open_poker.envs.poker_util.novelty.action.action_hierarchy import ActionHierarchy
from gym_open_poker.envs.poker_util.novelty.action.wealth_tax import WealthTax
from gym_open_poker.envs.poker_util.novelty.action.round_action_restrict import RoundActionReStrict

import importlib

"""
novelty_category_list = ["conclude_game"]
NOVELTY_LIST = []
for nc in novelty_category_list:
    print(nc)
    module = importlib.import_module(nc)
    for member in dir(module):
        NOVELTY_LIST += [cls for cls in locals().values() if isinstance(cls, type)]
"""
# print(Environment1.__module__)
# print(Environment1.__module__.split(".")[-2])
# print(Environment1.__module__.__file__)

# NOVELTY_DICT = dict()
# NOVELTY_DICT = {"conclude_game": "Environment1"}
__all__ = []

locals_values = list(locals().values()).copy()
for cls in locals_values:
    if isinstance(cls, type):
        novelty_category = cls.__module__.split(".")[-2]
        novelty_string = cls.__name__
        __all__.append(f"{novelty_category}.{novelty_string}")

NOVELTY_LIST = __all__
# print(NOVELTY_LIST)
# print(NOVELTY_DICT)
"""

NOVELTY_LIST = [cls for cls in locals().values() if isinstance(cls, type)]
# NOVELTY_LIST.append("RANDOM")

#
    "Action1",
    "CardDistHigh",
    "CardDistLow",
    "Card1",
    "conclude_game.Environment1",
    "Environment2",
    "Agent1",
    "Agent2",
    "Agent3",
    "Event1",
    "Rule2",
    "Rule3",
    "Event2",
    "Rule4",
    "Card2",
    "Card3",
]
"""
