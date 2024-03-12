# import numpy as np
from gym_open_poker.envs.poker_util.action_choices import (
    call,
    all_in,
    fold,
    raise_bet,
    bet,
    check,
)

from card_utility_actions import get_best_hand

# from itertools import combinations
from agent_helper_function import (
    format_float_precision,
    get_out_probability,
)

# from collections import Counter

"""
This agent only care its own hand.

In pre-flop, 
Case1: if it has A, K, Q pair
    if raise_bet in allowable_actions: raise_bet
    else: call/chcek
Case2: if it has pair or same suit:
    call
Case3: otherwise, fold


In flop, turn
Case1: if it has the hand ahead to three_of_a_kind, then it believe 100% win, so it will bet/raise_bet.
Case2: if the out_probability >= 2/47
    it will call/check
Case3: if the out_probability < 2/47
    if check in allowable_actions: check
    else: fold



In river:
Case1: if it has the hand ahead to three_of_a_kind, then it believe 100% win,
    so it will bet/raise_bet.
Case2: nothing in hands
    if check in allowable_actions: check
    else: fold



"""

DESIRED_PAIR = [[1, 1], [13, 13], [12, 12]]
DESIRED_OUT_PRABABILITY_THRESHOLD = format_float_precision(2 / 47)


def make_pre_flop_moves(player, current_gameboard, allowable_actions):
    """Strategies for agent in pre-flop round
    In pre-flop,
    Case1: if it has A, K, Q pair
        if raise_bet in allowable_actions: raise_bet
        else: call/chcek
    Case2: if it has pair or same suit:
        call
    Case3: otherwise, fold

    Args:
        player
        current_gameboard
        allowable_actions

    Returns:
        function
    """

    # hole cards
    hole_card = player.hole_cards
    values = [card.number for card in hole_card]
    suits = [card.suit for card in hole_card]

    has_desired_pair = True if values in DESIRED_PAIR else False
    has_pair = True if len(set(values)) == 1 else False
    has_suit = True if len(set(suits)) == 1 else False

    # parameters the agent need to take actions with
    params = dict()
    params["current_gameboard"] = current_gameboard
    params["player"] = player

    # Case 1
    if has_desired_pair:
        if all_in in allowable_actions:
            return all_in, params
        elif raise_bet in allowable_actions:
            return raise_bet, params
        elif call in allowable_actions:
            return call, params
        elif check in allowable_actions:
            return check, params

    # Case 2
    if has_pair or has_suit:
        if all_in in allowable_actions:
            return all_in, params
        elif call in allowable_actions:
            return call, params
        elif check in allowable_actions:
            return check, params

    # Case 3
    return fold, params


def make_flop_moves(player, current_gameboard, allowable_actions):
    """Strategies for agent in flop round

    Case1: if it has the hand ahead to three_of_a_kind, then it believe 100% win, so it will bet/raise_bet.
    Case2: if the out_probability >= 2/47
        it will call/check
    Case3: if the out_probability < 2/47
        if check in allowable_actions: check
        else: fold

    Args:
        player
        current_gameboard
        allowable_actions

    Returns:
        function
    """
    # board info
    hand_rank_type = current_gameboard["hand_rank_type"]

    # card info
    total_hand = player.hole_cards + current_gameboard["board"].community_cards

    cur_rank_type, _ = get_best_hand(current_gameboard, total_hand)
    out_probability = get_out_probability(current_gameboard, total_hand, desired_hand="three_of_a_kind")

    if hand_rank_type[cur_rank_type] >= hand_rank_type["three_of_a_kind"]:
        has_winnable_hand = True
    else:
        has_winnable_hand = False

    # parameters for take actions
    params = dict()
    params["current_gameboard"] = current_gameboard
    params["player"] = player

    # Case1: if it has the hand ahead to three_of_a_kind, then it believe 100% win, so it will bet/raise_bet.
    if has_winnable_hand:
        if all_in in allowable_actions:
            return all_in, params
        elif raise_bet in allowable_actions:
            return raise_bet, params
        elif bet in allowable_actions:
            return bet, params
        elif call in allowable_actions:
            return call, params
        elif check in allowable_actions:
            return check, params
        else:
            return fold, params

    if out_probability >= DESIRED_OUT_PRABABILITY_THRESHOLD:
        # Case2: if the out_probability >= 2/47
        if all_in in allowable_actions:
            return all_in, params
        elif call in allowable_actions:
            return call, params
        elif check in allowable_actions:
            return check, params
        else:
            return fold, params

    else:
        # Case3: if the out_probability < 2/47
        if check in allowable_actions:
            return check, params
        else:
            return fold, params


def make_turn_moves(player, current_gameboard, allowable_actions):
    """Strategies for agent in flop round

    Case1: if it has the hand ahead to three_of_a_kind, then it believe 100% win, so it will bet/raise_bet.
    Case2: if the out_probability >= 2/47
        it will call/check
    Case3: if the out_probability < 2/47
        if check in allowable_actions: check
        else: fold

    Args:
        player
        current_gameboard
        allowable_actions

    Returns:
        function
    """

    # board info
    hand_rank_type = current_gameboard["hand_rank_type"]

    # card info
    total_hand = player.hole_cards + current_gameboard["board"].community_cards

    cur_rank_type, _ = get_best_hand(current_gameboard, total_hand)
    out_probability = get_out_probability(current_gameboard, total_hand, desired_hand="three_of_a_kind")

    if hand_rank_type[cur_rank_type] >= hand_rank_type["three_of_a_kind"]:
        has_winnable_hand = True
    else:
        has_winnable_hand = False

    # parameters for take actions
    params = dict()
    params["current_gameboard"] = current_gameboard
    params["player"] = player

    # Case1: if it has the hand ahead to three_of_a_kind, then it believe 100% win, so it will bet/raise_bet.
    if has_winnable_hand:
        if all_in in allowable_actions:
            return all_in, params
        elif raise_bet in allowable_actions:
            return raise_bet, params
        elif bet in allowable_actions:
            return bet, params
        elif call in allowable_actions:
            return call, params
        elif check in allowable_actions:
            return check, params
        else:
            return fold, params

    if out_probability >= DESIRED_OUT_PRABABILITY_THRESHOLD:
        # Case2: if the out_probability >= 2/47
        if all_in in allowable_actions:
            return all_in, params
        elif call in allowable_actions:
            return call, params
        elif check in allowable_actions:
            return check, params
        else:
            return fold, params

    else:
        # Case3: if the out_probability < 2/47
        if check in allowable_actions:
            return check, params
        else:
            return fold, params


def make_river_moves(player, current_gameboard, allowable_actions):
    """Strategies of agent in river round

    Case1: if it has the hand ahead to three_of_a_kind, then it believe 100% win,
        so it will bet/raise_bet.
    Case2: nothing in hands
        if check in allowable_actions: check
        else: fold


    Args:
        player
        current_gameboard
        allowable_actions

    Returns:
        function
    """

    # board info
    hand_rank_type = current_gameboard["hand_rank_type"]

    # card info
    total_hand = player.hole_cards + current_gameboard["board"].community_cards

    cur_rank_type, _ = get_best_hand(current_gameboard, total_hand)
    # out_probability = get_out_probability(current_gameboard, total_hand, desired_hand='three_of_a_kind')

    if hand_rank_type[cur_rank_type] >= hand_rank_type["three_of_a_kind"]:
        has_winnable_hand = True
    else:
        has_winnable_hand = False

    # parameters for take actions
    params = dict()
    params["current_gameboard"] = current_gameboard
    params["player"] = player

    if has_winnable_hand:
        # Case1: if it has the hand ahead to three_of_a_kind, then it believe 100% win, so it will bet/raise_bet.
        if all_in in allowable_actions:
            return all_in, params
        elif raise_bet in allowable_actions:
            return raise_bet, params
        elif bet in allowable_actions:
            return bet, params
        elif call in allowable_actions:
            return call, params
        elif check in allowable_actions:
            return check, params
        else:
            return fold, params

    else:
        # Case2: nothing in hands
        if check in allowable_actions:
            return check, params
        else:
            return fold, params


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
    ans["strategy_type"] = "agent_p"

    return ans


decision_agent_methods = _build_decision_agent_methods_dict()
