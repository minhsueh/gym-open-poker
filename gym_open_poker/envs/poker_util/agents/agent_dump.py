import numpy as np
from action_choices import *
from card_utility_actions import *
from itertools import combinations
from agent_helper_function import *
from collections import Counter



def make_pre_flop_moves(player, current_gameboard, allowable_actions):


    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    if all_in in allowable_actions:
        return all_in, params
    elif check in allowable_actions:
        return check, params
    elif call in allowable_actions:
        return call, params
    else:
        return fold, params

    


def make_flop_moves(player, current_gameboard, allowable_actions):
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    if all_in in allowable_actions:
        return all_in, params
    elif check in allowable_actions:
        return check, params
    elif call in allowable_actions:
        return call, params
    else:
        return fold, params


def make_turn_moves(player, current_gameboard, allowable_actions):

    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    if all_in in allowable_actions:
        return all_in, params
    elif check in allowable_actions:
        return check, params
    elif call in allowable_actions:
        return call, params
    else:
        return fold, params


def make_river_moves(player, current_gameboard, allowable_actions):

    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    if all_in in allowable_actions:
        return all_in, params
    elif check in allowable_actions:
        return check, params
    elif call in allowable_actions:
        return call, params
    else:
        return fold, params



def _build_decision_agent_methods_dict():
    """
    This function builds the decision agent methods dictionary.
    :return: The decision agent dict. Keys should be exactly as stated in this example, but the functions can be anything
    as long as you use/expect the exact function signatures we have indicated in this document.
    """
    ans = dict()
    ans['make_pre_flop_moves'] = make_pre_flop_moves
    ans['make_flop_moves'] = make_flop_moves
    ans['make_turn_moves'] = make_turn_moves
    ans['make_river_moves'] = make_river_moves
    ans['strategy_type'] = "agent_dump"

    return ans


decision_agent_methods = _build_decision_agent_methods_dict()
