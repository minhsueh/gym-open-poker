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
    """Strategies for agent in pre-flop round
    1.
    :param player: current player
    :param current_gameboard: game board dictionary
    :param allowable_actions: action could be done by the agent
    :param code:
    :return:
    """

    if player.status != 'waiting_for_move':
        print(f'{player.player_name} is in the status {player.status}, something go wrong...')
        raise Exception

    # hole cards and some pairs agent want
    hole_card = player.hole_cards
    values = [card.number for card in hole_card]
    suits = [card.suit for card in hole_card]
    other_pairs = set(combinations([10, 11, 12, 13, 1], 2))

    # some board info
    board = current_gameboard['board']
    previous_bet = board.current_highest_bet
    big_blind_force_bet = current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']

    # parameters the agent need to take actions with
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    # if player is big blind or small blind
    if call in allowable_actions or raise_bet in allowable_actions:

        if suits[0] == suits[1]:  # hole cards are in same suit
            print(f'my two cards are in same suit: {suits[0]}')
            if (values[0], values[1]) in top_5_pair['suit'] or (values[1], values[0]) in top_5_pair['suit']:
                print('I have top 5 pair')
                current_gameboard['hole_card_type'] = ('top_1', 'suit')
                if previous_bet > big_blind_force_bet and raise_bet in allowable_actions:  # re-raise again
                    amount_to_raise = 1.5 * previous_bet
                    if player.bet_amount_each_game + amount_to_raise < rank2profit_percent['top_1'] * (player.bet_amount_each_game + player.current_cash):
                        params['amount_to_raise'] = amount_to_raise
                        return raise_bet, params
                    else:
                        params['amount_to_raise'] = previous_bet + 1
                        return raise_bet, params
                if player.bet_amount_each_game + previous_bet < rank2profit_percent['top_1'] * (player.bet_amount_each_game + player.current_cash):
                    return call, params

            elif (values[0], values[1]) in top_6_14_pair['suit'] or (values[1], values[0]) in top_6_14_pair['suit']:
                print('I have top 6-14 pairs')
                current_gameboard['hole_card_type'] = ('top_2', 'suit')
                if previous_bet > big_blind_force_bet and raise_bet in allowable_actions:  # re-raise again
                    amount_to_raise = 1.5 * previous_bet
                    if player.bet_amount_each_game + amount_to_raise < rank2profit_percent['top_2'] * (player.bet_amount_each_game + player.current_cash):
                        params['amount_to_raise'] = amount_to_raise
                        return raise_bet, params
                    else:
                        params['amount_to_raise'] = previous_bet + 1
                        return raise_bet, params
                if player.bet_amount_each_game + previous_bet < rank2profit_percent['top_2'] * (player.bet_amount_each_game + player.current_cash):
                    return call, params

            elif (values[0], values[1]) in top_15_26_pair['suit'] or (values[1], values[0]) in top_15_26_pair['suit']:
                print('I have top 15-26 pairs')
                current_gameboard['hole_card_type'] = ('top_3', 'suit')
                if previous_bet > big_blind_force_bet and raise_bet in allowable_actions:  # re-raise again
                    amount_to_raise = 1.5 * previous_bet
                    if player.bet_amount_each_game + amount_to_raise < rank2profit_percent['top_3'] * (player.bet_amount_each_game + player.current_cash):
                        params['amount_to_raise'] = amount_to_raise
                        return raise_bet, params
                    else:
                        params['amount_to_raise'] = previous_bet + 1
                        return raise_bet, params
                if player.bet_amount_each_game + previous_bet < rank2profit_percent['top_3'] * (player.bet_amount_each_game + player.current_cash):
                    return call, params

            elif (values[0], values[1]) in top_27_40_pair['suit'] or (values[1], values[0]) in top_27_40_pair['suit']:
                print('I have top 27-40 pairs')
                current_gameboard['hole_card_type'] = ('top_4', 'suit')
                if previous_bet > big_blind_force_bet and raise_bet in allowable_actions:  # re-raise again
                    amount_to_raise = 1.5 * previous_bet
                    if player.bet_amount_each_game + amount_to_raise < rank2profit_percent['top_4'] * (player.bet_amount_each_game + player.current_cash):
                        params['amount_to_raise'] = amount_to_raise
                        return raise_bet, params
                    else:
                        params['amount_to_raise'] = previous_bet + 1
                        return raise_bet, params
                if player.bet_amount_each_game + previous_bet < rank2profit_percent['top_4'] * (player.bet_amount_each_game + player.current_cash):
                    return call, params

            elif (values[0], values[1]) in other_pairs or (values[1], values[0]) in other_pairs:
                print('I have top 40+ pairs')
                current_gameboard['hole_card_type'] = ('top_5', 'suit')
                if player.bet_amount_each_game + previous_bet <= big_blind_force_bet:
                    return call, params

        else:
            print(f'my two cards are not in same suit')
            if (values[0], values[1]) in top_5_pair['un-suit'] or (values[1], values[0]) in top_5_pair['un-suit']:
                print('I have top 5 pairs')
                current_gameboard['hole_card_type'] = ('top_1', 'un-suit')
                if previous_bet > big_blind_force_bet and raise_bet in allowable_actions:  # re-raise again
                    amount_to_raise = 1.5 * previous_bet
                    if player.bet_amount_each_game + amount_to_raise < rank2profit_percent['top_1'] * (player.bet_amount_each_game + player.current_cash):
                        params['amount_to_raise'] = amount_to_raise
                        return raise_bet, params
                    else:
                        params['amount_to_raise'] = previous_bet + 1
                        return raise_bet, params
                if player.bet_amount_each_game + previous_bet < rank2profit_percent['top_1'] * (player.bet_amount_each_game + player.current_cash):
                    return call, params

            elif (values[0], values[1]) in top_6_14_pair['un-suit'] or (values[1], values[0]) in top_6_14_pair['un-suit']:
                print('I have top 6-14 pairs')
                current_gameboard['hole_card_type'] = ('top_2', 'un-suit')
                if previous_bet > big_blind_force_bet and raise_bet in allowable_actions:  # re-raise again
                    amount_to_raise = 1.5 * previous_bet
                    if player.bet_amount_each_game + amount_to_raise < rank2profit_percent['top_2'] * (player.bet_amount_each_game + player.current_cash):
                        params['amount_to_raise'] = amount_to_raise
                        return raise_bet, params
                    else:
                        params['amount_to_raise'] = previous_bet + 1
                        return raise_bet, params
                if player.bet_amount_each_game + previous_bet < rank2profit_percent['top_2'] * (player.bet_amount_each_game + player.current_cash):
                    return call, params

            elif (values[0], values[1]) in top_15_26_pair['un-suit'] or (values[1], values[0]) in top_15_26_pair['un-suit']:
                print('I have top 15-26 pairs')
                current_gameboard['hole_card_type'] = ('top_3', 'un-suit')
                if previous_bet > big_blind_force_bet and raise_bet in allowable_actions:  # re-raise again
                    amount_to_raise = 1.5 * previous_bet
                    if player.bet_amount_each_game + amount_to_raise < rank2profit_percent['top_3'] * (player.bet_amount_each_game + player.current_cash):
                        params['amount_to_raise'] = amount_to_raise
                        return raise_bet, params
                    else:
                        params['amount_to_raise'] = previous_bet + 1
                        return raise_bet, params
                if player.bet_amount_each_game + previous_bet < rank2profit_percent['top_3'] * (player.bet_amount_each_game + player.current_cash):
                    return call, params

            elif (values[0], values[1]) in top_27_40_pair['un-suit'] or (values[1], values[0]) in top_27_40_pair['un-suit']:
                print('I have top 27-40 pairs')
                current_gameboard['hole_card_type'] = ('top_4', 'un-suit')
                if previous_bet > big_blind_force_bet and raise_bet in allowable_actions:  # re-raise again
                    amount_to_raise = 1.5 * previous_bet
                    if player.bet_amount_each_game + amount_to_raise < rank2profit_percent['top_4'] * (player.bet_amount_each_game + player.current_cash):
                        params['amount_to_raise'] = amount_to_raise
                        return raise_bet, params
                    else:
                        params['amount_to_raise'] = previous_bet + 1
                        return raise_bet, params
                if player.bet_amount_each_game + previous_bet < rank2profit_percent['top_4'] * (player.bet_amount_each_game + player.current_cash):
                    return call, params

            elif (values[0], values[1]) in other_pairs or (values[1], values[0]) in other_pairs:
                print('I have top 40+ pairs')
                current_gameboard['hole_card_type'] = ('top_5', 'un-suit')
                if player.bet_amount_each_game + previous_bet <= big_blind_force_bet:
                    return call, params

    print('I have bottom pairs')
    current_gameboard['hole_card_type'] = ('bottom', 'un-suit') if suits[0] != suits[1] else ('bottom', 'suit')
    if previous_bet > big_blind_force_bet:  # someone raise
        print('someone raise, I fold')
        return fold, params
    if previous_bet <= big_blind_force_bet:  # no one raise
        if player.big_blind and check in allowable_actions:
            print('no one raise, I check')
            return check, params
        else:
            print('no one raise, I call to big blind amount')
            return call, params

    return fold, params


def make_flop_moves(player, current_gameboard, allowable_actions, code):
    """Strategies for agent in flop round
    1.
    :param player:
    :param current_gameboard:
    :param allowable_actions:
    :param code:
    :return:
    """

    if player.status != 'waiting_for_move':
        print(f'{player.player_name} is in the status {player.status}, something go wrong...')
        raise Exception

    # card info
    total_hand = player.hole_cards + current_gameboard['board'].community_cards
    values = [card.number for card in total_hand]
    suits = [card.suit for card in total_hand]

    # board info
    board = current_gameboard['board']
    previous_bet = board.current_highest_bet
    minimum_bet = 10 * current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']

    # parameters for take actions
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard


    hole_card_type, hole_card_suit = current_gameboard['hole_card_type']
    # previous pair in the top category
    if hole_card_type == 'top_1' or hole_card_type == 'top_2' or hole_card_type == 'top_3':
        if all_in in allowable_actions:
            return all_in, params
        # for val in values:
        #     if values.count(val) >= 3 and all_in in allowable_actions:
        #         return all_in, params
        # for su in suits:
        #     if suits.count(su) >= 4 and all_in in allowable_actions:
        #         return all_in, params
        # cnt = 1
        # max_cnt = 1
        # values_copy = sorted(copy.copy(values))
        # if 1 in values:
        #     values_copy.append(14)
        # for i in range(1, len(values_copy)):
        #     if values_copy[i] - 1 == values_copy[i-1]:
        #         cnt += 1
        #     else:
        #         cnt = 1
        #     max_cnt = max(cnt, max_cnt)
        # if max_cnt >= 3 and all_in in allowable_actions:
        #     return all_in, params

    # check since no players bet at this time yet
    elif previous_bet == 0 and check in allowable_actions:
        return check, params

    # previous pair in the middle category
    elif hole_card_type == 'top_4' or hole_card_type == 'top_5':
        if previous_bet <= minimum_bet * 2 and call in allowable_actions:
            return call, params

    # previous pair in the bottom category
    else:
        if previous_bet <= minimum_bet * 1.5 and call in allowable_actions:
            return call, params

    # if reach here, which means that the agent does not all_in with top pairs or the agent does not call with
    # the proper amount
    return fold, params


def make_turn_moves(player, current_gameboard, allowable_actions, code):
    """Strategies of agent in turn round
    1. If all-in in previous round, the agent has to wait until the showdown
    2. If no others bet which mean previous bet is 0, the agent would check
    3. If there are other players bet which mean previous bet is not 0, the agent would fold
    :param player:
    :param current_gameboard:
    :param allowable_actions:
    :param code:
    :return:
    """

    if player.status != 'waiting_for_move':
        print(f'{player.player_name} is in the status {player.status}, something go wrong...')
        raise Exception

    # card info
    total_hand = player.hole_cards + current_gameboard['board'].community_cards
    values = [card.number for card in total_hand]
    suits = [card.suit for card in total_hand]

    # board info
    board = current_gameboard['board']
    previous_bet = board.current_highest_bet

    # parameters for actions to take
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    if previous_bet <= 0 and check in allowable_actions:
        return check, params

    return fold, params


def make_river_moves(player, current_gameboard, allowable_actions, code):
    """Strategies of agent in river round
    1. If all-in in previous round, the agent has to wait until the showdown
    2. If no others bet which mean previous bet is 0, the agent would check
    3. If there are other players bet which mean previous bet is not 0, the agent would fold
    :param player:
    :param current_gameboard:
    :param allowable_actions:
    :param code:
    :return:
    """

    if player.status != 'waiting_for_move':
        print(f'{player.player_name} is in the status {player.status}, something go wrong...')
        raise Exception

    # card info
    total_hand = player.hole_cards + current_gameboard['board'].community_cards
    values = [card.number for card in total_hand]
    suits = [card.suit for card in total_hand]

    # baord info
    board = current_gameboard['board']
    previous_bet = board.current_highest_bet

    # parameters for actions to take
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    if previous_bet <= 0 and check in allowable_actions:
        return check, params

    return fold, params


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
