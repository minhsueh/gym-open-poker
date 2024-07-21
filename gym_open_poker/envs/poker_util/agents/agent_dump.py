from action import Action

# from gym_open_poker.envs.poker_util.card_utility_actions import *
# from itertools import combinations
# from gym_open_poker.envs.poker_util.agent_helper_function import *
# from collections import Counter


def make_pre_flop_moves(player, current_gameboard, allowable_actions):
    if Action.ALL_IN in allowable_actions:
        return Action.ALL_IN
    elif Action.CHECK in allowable_actions:
        return Action.CHECK
    elif Action.CALL in allowable_actions:
        return Action.CALL
    else:
        return Action.FOLD


def make_flop_moves(player, current_gameboard, allowable_actions):
    if Action.ALL_IN in allowable_actions:
        return Action.ALL_IN
    elif Action.CHECK in allowable_actions:
        return Action.CHECK
    elif Action.CALL in allowable_actions:
        return Action.CALL
    else:
        return Action.FOLD


def make_turn_moves(player, current_gameboard, allowable_actions):
    if Action.ALL_IN in allowable_actions:
        return Action.ALL_IN
    elif Action.CHECK in allowable_actions:
        return Action.CHECK
    elif Action.CALL in allowable_actions:
        return Action.CALL
    else:
        return Action.FOLD


def make_river_moves(player, current_gameboard, allowable_actions):
    if Action.ALL_IN in allowable_actions:
        return Action.ALL_IN
    elif Action.CHECK in allowable_actions:
        return Action.CHECK
    elif Action.CALL in allowable_actions:
        return Action.CALL
    else:
        return Action.FOLD


def _build_decision_agent_methods_dict():
    """
    This function builds the decision agent methods dictionary.
    :return: The decision agent dict. Keys should be exactly as stated in this example, but the functions can be anything
    as long as you use/expect the exact function signatures we have indicated in this document.
    """
    ans = dict()
    ans["make_pre_flop_moves"] = make_pre_flop_moves
    ans["make_flop_moves"] = make_flop_moves
    ans["make_turn_moves"] = make_turn_moves
    ans["make_river_moves"] = make_river_moves
    ans["strategy_type"] = "agent_dump"

    return ans


decision_agent_methods = _build_decision_agent_methods_dict()
