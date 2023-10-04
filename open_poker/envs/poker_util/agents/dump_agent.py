import numpy as np
from action_choices import *
from card_utility_actions import *
from itertools import combinations
from agent_helper_function import *
from collections import Counter
"""
The agent consider its hand for each round and each game with appropriate actions, which might lead to a more 
cash winning during the tournament. 

Top 5 hands (2.1% of all starting hands, 50% of profits): AA, KK, QQ, JJ and AKs

Top 6-14 hands (4.2% of all starting hands, 30% of profits): TT, 99, AQs, AJs, ATs, AK, AQ, KQs, KJs

Top 15-26 hands (5.7% of all starting hands, 15% of profits): 88, 77, A9s, A8s, AJ, AT, KTs, K9s, KQ, QJs, QTs, JTs

Top 27-40 hands (6.3% of all hands, 5% of profits): 66, 55, A7S-A3s, K8S, KJ, KT, Q9s, QJ, J9s, T9s
"""

# some combinations of hole card the agent prefer in the pre-flop round
top_5_pair = {
    'un-suit': {(1, 1), (13, 13), (12, 12), (11, 11)},
    'suit': {(1, 13)}
}
top_6_14_pair = {
    'un-suit': {(10, 10), (9, 9), (1, 13), (1, 12)},
    'suit': {(1, 12), (1, 11), (1, 10), (13, 12), (13, 11)}
}
top_15_26_pair = {
    'un-suit': {(8, 8), (7, 7), (1, 11), (1, 10), (12, 13)},
    'suit': {(1, 9), (1, 8), (13, 10), (13, 9), (12, 11), (12, 10), (11, 10)}
}
top_27_40_pair = {
    'un-suit': {(6, 6), (5, 5), (13, 11), (13, 10), (12, 11)},
    'suit': {(1, 7), (1, 6), (1, 5), (1, 4), (1, 3), (13, 8), (12, 9), (11, 9), (10, 9)}
}
# categories and its corresponding profit percent which used for making decisions
rank2profit_percent = {
    'top_1': 0.5,
    'top_2': 0.3,
    'top_3': 0.15,
    'top_4': 0.05,
}


def make_pre_flop_moves(player, current_gameboard, allowable_actions, code):


    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard


    if check in allowable_actions:
        return check, params
    else:
        return call, params

    


def make_flop_moves(player, current_gameboard, allowable_actions, code):
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    
    if check in allowable_actions:
        return check, params
    else:
        return call, params


def make_turn_moves(player, current_gameboard, allowable_actions, code):
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    
    if check in allowable_actions:
        return check, params
    else:
        return call, params


def make_river_moves(player, current_gameboard, allowable_actions, code):
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    
    if check in allowable_actions:
        return check, params
    else:
        return call, params

def make_computing_best_hand_moves(player, current_gameboard, allowable_actions, code):
    """Just compute the agent's best hand in this function

    :param player:
    :param current_gameboard:
    :param allowable_actions:
    :param code:
    :return:
    """
    # parameters for actions to take
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    # agent has to compute best hand at this time
    if current_gameboard['calculate_best_hand'] in allowable_actions:
        return current_gameboard['calculate_best_hand'], params
    else:
        raise Exception


def make_continue_game_moves(player, current_gameboard, allowable_actions, code):
    """Should the agent continue to play the agent according to the actions other players take in this round
    The agent will take this function only if i) they previously check or ii) bet some money before other raise
    1. If my previous decision is check, I could either fold or call with certain amount
    2. If my previous decision is call/bet/raise but now other players after me raise the bet again, I could either
    fold or match with certain amount

    Notice: raise is not allowable because the board need to conclude the current round, probably raise is allowable
    later but need to refactor the system
    :param player: agent obj
    :param current_gameboard: current game board dict
    :param allowable_actions: actions that are allowable to take
    :param code:
    :return:
    """

    # card info
    total_hand = player.hole_cards + current_gameboard['board'].community_cards
    values = [card.number for card in total_hand]
    suits = [card.suit for card in total_hand]
    hole_card_type, hole_card_suit = current_gameboard['hole_card_type']

    # baord info
    board = current_gameboard['board']
    previous_bet = board.current_highest_bet
    minimum_bet = 10 * current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']

    # parameters for actions to take
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard


    if current_gameboard['cur_phase'] == 'flop_phase':
        # no check at this round
        if (hole_card_type != 'top_5' and hole_card_type != 'bottom') and match_highest_bet_on_the_table in allowable_actions:
            amount_to_match = previous_bet - player.bet_amount_each_round
            if amount_to_match + player.bet_amount_each_game < (player.current_cash + player.bet_amount_each_game) * rank2profit_percent[hole_card_type] and \
                    amount_to_match < player.current_cash:
                return match_highest_bet_on_the_table, params

    elif current_gameboard['cur_phase'] == 'turn_phase':
        if player.current_decision == 'check' and not previous_bet and check in allowable_actions:
            return check, params
        elif player.is_all_in:  # wait until the game showdown
            return null_action(), params
        if match_highest_bet_on_the_table in allowable_actions:
            amount_to_match = previous_bet - player.bet_amount_each_round
            if hole_card_type == 'top_3' or hole_card_type == 'top_4' or hole_card_type == 'top_5':
                if amount_to_match + player.bet_amount_each_game < 2 * minimum_bet and amount_to_match < player.current_cash:
                    return match_highest_bet_on_the_table, params
                elif fold in allowable_actions:
                    return fold, params
            else:
                if amount_to_match + player.bet_amount_each_game < 1.5 * minimum_bet and amount_to_match < player.current_cash:
                    return match_highest_bet_on_the_table, params
                elif fold in allowable_actions:
                    return fold, params

    elif current_gameboard['cur_phase'] == 'river_phase':
        if player.current_decision == 'check' and not previous_bet and check in allowable_actions:
            return check, params
        elif player.is_all_in:  # wait until the game showdown
            return null_action(), params
        elif fold in allowable_actions:
            return fold, params

    elif current_gameboard['cur_phase'] == 'concluding_phase':
        if player.current_decision == 'check' and not previous_bet and check in allowable_actions:
            return check, params
        elif player.is_all_in:  # wait until the game showdown
            return null_action(), params
        elif fold in allowable_actions:
            return fold, params

    # if reach here, the agent just does nothing
    return null_action, dict()


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
