import numpy as np

# from action_choices import call, all_in, fold, raise_bet, bet, check
# from card_utility_actions import *
# from itertools import combinations
# from agent_helper_function import (format_float_precision, get_out_probability, is_out_in_hand)
# from collections import Counter

"""
This agent randomly select one action from allowable_actions.
"""
RANDOM_SEED = 15
rng = np.random.default_rng(RANDOM_SEED)

def make_pre_flop_moves(player, current_gameboard, allowable_actions):
    """Strategies for agent in pre-flop round
    Args:
        player
        current_gameboard
        allowable_actions

    Returns:
        function
    """
    aa_list = list(allowable_actions)
    aa_list.sort(key = lambda x: x.value)
    return rng.choice(aa_list)


def make_flop_moves(player, current_gameboard, allowable_actions):
    """Strategies for agent in flop round

    Args:
        player
        current_gameboard
        allowable_actions

    Returns:
        function
    """
    aa_list = list(allowable_actions)
    aa_list.sort(key = lambda x: x.value)
    return rng.choice(aa_list)


def make_turn_moves(player, current_gameboard, allowable_actions):
    """Strategies for agent in flop round
    Args:
        player
        current_gameboard
        allowable_actions

    Returns:
        function
    """
    aa_list = list(allowable_actions)
    aa_list.sort(key = lambda x: x.value)
    return rng.choice(aa_list)


def make_river_moves(player, current_gameboard, allowable_actions):
    """Strategies of agent in river round

    Args:
        player
        current_gameboard
        allowable_actions

    Returns:
        function
    """
    aa_list = list(allowable_actions)
    aa_list.sort(key = lambda x: x.value)
    return rng.choice(aa_list)


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
    ans["strategy_type"] = "agent_random"

    return ans


decision_agent_methods = _build_decision_agent_methods_dict()
