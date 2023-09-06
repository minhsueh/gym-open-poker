import numpy as np
from action_choices import *
from card_utility_actions import *
import numpy as np
"""
Strategy of this agent is to random
"""


def make_pre_flop_moves(player, current_gameboard, allowable_actions, code):

    if player.status != 'waiting_for_move':
        print(f'{player.player_name} is in the status {player.status}, something go wrong...')
        raise Exception

    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    action = np.random.choice(list(allowable_actions))
    if action == raise_bet:
        params['amount_to_raise'] = current_gameboard['board'].current_highest_bet

    return action, params


def make_flop_moves(player, current_gameboard, allowable_actions, code):

    if player.status != 'waiting_for_move':
        print(f'{player.player_name} is in the status {player.status}, something go wrong...')
        raise Exception

    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    action = np.random.choice(list(allowable_actions))
    if action == raise_bet:
        params['amount_to_raise'] = current_gameboard['board'].current_highest_bet
    if action == bet:
        params['first_bet'] = 20 * current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']

    return action, params


def make_turn_moves(player, current_gameboard, allowable_actions, code):

    if player.status != 'waiting_for_move':
        print(f'{player.player_name} is in the status {player.status}, something go wrong...')
        raise Exception

    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    action = np.random.choice(list(allowable_actions))
    if action == raise_bet:
        params['amount_to_raise'] = current_gameboard['board'].current_highest_bet
    if action == bet:
        params['first_bet'] = 20 * current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']

    return action, params


def make_river_moves(player, current_gameboard, allowable_actions, code):

    if player.status != 'waiting_for_move':
        print(f'{player.player_name} is in the status {player.status}, something go wrong...')
        raise Exception

    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    action = np.random.choice(list(allowable_actions))
    if action == raise_bet:
        params['amount_to_raise'] = current_gameboard['board'].current_highest_bet
    if action == bet:
        params['first_bet'] = 20 * current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']

    return action, params


def make_computing_best_hand_moves(player, current_gameboard, allowable_actions, code):

    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    if current_gameboard['calculate_best_hand'] in allowable_actions:
        return current_gameboard['calculate_best_hand'], params
    else:
        raise Exception
    # rank, best_hand = calculate_best_hand(current_gameboard, player)
    # current_gameboard['hands_of_players'][-1][player.player_name] = (rank, best_hand)
    #
    # return null_action, dict()


def make_continue_game_moves(player, current_gameboard, allowable_actions, code):

    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    action = np.random.choice(list(allowable_actions))
    if action == raise_bet:
        params['amount_to_raise'] = current_gameboard['board'].current_highest_bet

    return action, params


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
    ans['make_computing_best_hand_moves'] = make_computing_best_hand_moves
    ans['make_continue_game_moves'] = make_continue_game_moves
    return ans


decision_agent_methods = _build_decision_agent_methods_dict()
