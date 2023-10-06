from flag_config import flag_config_dict
import card_utility_actions
import copy
from helper_functions import *
from chip import Chip

from phase import Phase
import logging

logger = logging.getLogger('open_poker.envs.poker_util.logging_info.action_choices')

# Note: like how skip turn gets removed and conclude actions get added to allowable_actions after a player decides not to skip turn,
# here (check, bet) for all players will be replaced by (call, raise_bet) after bet is made by a player in a round


def null_action():
    """
    :return: successful_action code
    """
    logger.debug('executing null action...')
    return flag_config_dict['successful_action']  # does nothing; code is always a success


# def directly_go_to_concluding_phase(player, current_gameboard, condition):
#     """
#     if one player is going out of chips, we should compute and compare their best hand in order to find
#     winner of this game
#     :param player:
#     :param current_gameboard:
#     :return:
#     """
#     logger.debug(f'{player.player_name} are {condition}, deal all of community cards and find winner')
#     cur_phase = current_gameboard['board'].cur_phase
#     if cur_phase == 'pre_flop_phase':
#         current_gameboard['board'].deal_community_card_by_number(5)
#     elif cur_phase == 'flop_phase':
#         current_gameboard['board'].deal_community_card_by_number(2)
#     elif cur_phase == 'turn_phase':
#         current_gameboard['board'].deal_community_card_by_number(1)
#
#     current_gameboard['board'].cur_phase = 'concluding_phase'
#     current_gameboard[condition] = True




def call(player, current_gameboard):
    """ 
    determine if player can call. 

    Procedures: to determine whether it is a successful action. If it does not go through the whole criteria, then it fails.
    criterias:
        if current_bet_count == 1

    Method1: 
        check on current_bet_count and current_raise_count
        bet_to_follow = 0
        1. PRE_FLOP:
            (1) BIG_BLIND
                if current_bet_count == 1 and current_raise_count == 0:
                    bet_to_follow = current_gameboard['big_blind_amount'] = current_gameboard['small_bet']

            (2) RAISE_BET
                if current_bet_count == 1 and current_raise_count > 0:
                    bet_to_follow = current_gameboard['small_bet'] * (current_bet_count + current_raise_count)
           The above two are equivalent to the following formula:
                raise_amount = current_gameboard['small_bet']
                bet_to_follow = raise_amount * (current_bet_count + current_raise_count)
        


        2. FLOP: 
            (1) BET
            (2) RAISE_BET
            raise_amount = current_gameboard['small_bet']
            bet_to_follow = raise_amount * (current_bet_count + current_raise_count)

        3. TURN and RIVER
            (1) BET
            (2) RAISE_BET

            The calculation is similar to the procedures in pre-flop, except the raise_amount = current_gameboard['big_bet']
            raise_amount = current_gameboard['big_bet']
            bet_to_follow = raise_amount * (current_bet_count + current_raise_count)
    

    Method2 (not used):    
        iterate players_last_move_list reversely, until 
        1. pre-flrop
            RAISE_BET or BIG_BLIND
        2. other rounds
            RAISE_BET or BET


    Args:
        current_gameboard

    Returns:
        flag(flag_config_dict):

    """

    logger.debug(f'{player.player_name} decides to make a --- Call ---')

    # Basic criteria:
    if current_gameboard['current_bet_count'] != 1:
        logger.debug(f'{player.player_name}: cannot call at this time since no others bet previously.')
        return flag_config_dict['failure_code']

    # check player's current_cash is larger than bet_to_follow
    if current_gameboard['board'].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard['small_bet']
    elif current_gameboard['board'].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard['big_bet']
    else:
        print('cur_phase is invalid, current value = ' + str(current_gameboard['board'].cur_phase))
        raise

    already_bet = player.bet_amount_each_round

    


    bet_to_follow = raise_amount * (current_gameboard['current_bet_count'] + current_gameboard['current_raise_count']) - already_bet
    if bet_to_follow == 0:
        logger.debug(f'{player.player_name} is big blind and nobody raise_bet, should do the check, not call.')
        return flag_config_dict['failure_code']
    elif bet_to_follow > player.current_cash:
        logger.debug(f'{player.player_name} current cash {player.current_cash} is smaller than bet want to follow')
        return flag_config_dict['failure_code']

    # 
    player.current_cash -= bet_to_follow

    #
    current_gameboard['board'].player_pot[player.player_name] += bet_to_follow

    # perform call
    current_gameboard['board'].add_total_cash_on_table(bet_to_follow)

    return flag_config_dict['successful_action']










def raise_bet(player, current_gameboard, amount_to_raise):
    """ 
    determine if player can raise_bet. 
    criterias:
        if current_bet_count == 1 and current_raise_count > 0


    Procedures: to determine whether it is a successful action. If it does not go through the whole criteria, then it fails.
    Method1: 
        check on current_bet_count and current_raise_count
        bet_to_follow = 0
        1. PRE_FLOP:
            (1) BIG_BLIND
                if current_bet_count == 1 and current_raise_count == 0:
                    bet_to_follow = current_gameboard['big_blind_amount'] = current_gameboard['small_bet']

            (2) RAISE_BET
                if current_bet_count == 1 and current_raise_count > 0:
                    bet_to_follow = current_gameboard['small_bet'] * (current_bet_count + current_raise_count)
           The above two are equivalent to the following formula:
                raise_amount = current_gameboard['small_bet']
                bet_to_follow = raise_amount * (current_bet_count + current_raise_count)
        


        2. FLOP: 
            (1) BET
            (2) RAISE_BET
            raise_amount = current_gameboard['small_bet']
            bet_to_follow = raise_amount * (current_bet_count + current_raise_count)

        3. TURN and RIVER
            (1) BET
            (2) RAISE_BET

            The calculation is similar to the procedures in pre-flop, except the raise_amount = current_gameboard['big_bet']
            raise_amount = current_gameboard['big_bet']
            bet_to_follow = raise_amount * (current_bet_count + current_raise_count)

    Args:
        current_gameboard

    Returns:
        flag(flag_config_dict):

    """
    logger.debug(f'{player.player_name} decides to --- Raise Bet ---')
    if current_gameboard['current_bet_count'] == 0:
        logger.debug(f'{player.player_name}: there is no bet previously, I cannot raise a bet')
        return flag_config_dict['failure_code']
    elif current_gameboard['current_raise_count'] == current_gameboard['max_raise_count']:
        logger.debug(f'{player.player_name}: it has reached the max_raise_count = ' + str(current_gameboard['max_raise_count']))
        return flag_config_dict['failure_code'] 

    if current_gameboard['board'].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard['small_bet']
    elif current_gameboard['board'].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard['big_bet']
    else:
        raise

    bet_to_follow = raise_amount * (current_gameboard['current_bet_count'] + current_gameboard['current_raise_count'])

    current_gameboard['board'].player_pot[player.player_name] += bet_to_follow

    highest_bet = current_gameboard['board'].current_highest_bet

    if not highest_bet:
        logger.debug(f'{player.player_name}: there is no bet previously, I cannot raise a bet')
        return flag_config_dict['failure_code']
    # minimum raise should be the size of last bet
    elif current_gameboard['board'].cur_phase == 'pre_flop_phase' and not highest_bet:
        if amount_to_raise < current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']:
            logger.debug(f'{player.player_name}: minimum raise bet should be at least size of last bet')
            return flag_config_dict['failure_code']
    elif amount_to_raise < highest_bet:
        logger.debug(f'{player.player_name}: minimum raise bet should be at least size of last bet')
        return flag_config_dict['failure_code']

    # new amount after raise with certain amount
    new_bet = highest_bet + amount_to_raise
    if new_bet > player.current_cash:
        logger.debug(f'{player.player_name}: current cash {player.current_cash} is smaller than bet {new_bet}')
        return flag_config_dict['failure_code']

    total_bet = remove_chips_from_player_hand(player, new_bet, 'raise_bet', current_gameboard)
    # if do not have enough money, just put as much as player current has
    if not total_bet or total_bet < new_bet:
        logger.debug(f'{player.player_name} does not have enough chips to raise bet')
        return flag_config_dict['failure_code']

    logger.debug(f'{player.player_name}: I will bet with amount ${new_bet}')
    if total_bet != new_bet:
        logger.debug(f'{player.player_name}: do not properly raise a bet with corrected amount')
        return flag_config_dict['failure_code']

    transfer_chips_from_player_to_board(player, current_gameboard, new_bet)

    current_gameboard['current_raise_count'] += 1
    if current_gameboard['current_raise_count'] > current_gameboard['max_raise_count']:
        raise

    return flag_config_dict['successful_action']




def fold(player, current_gameboard):
    """ 
    determine if player can fold. 
    criterias:
        Not fold and lose

    Args:
        current_gameboard

    Returns:
        flag(flag_config_dict):

    """
    logger.debug(f'{player.player_name} decides to --- Fold ---')
    if player.is_fold:
        logger.debug(f'{player.player_name}: already fold in previous round, cannot fold again')
        return flag_config_dict['failure_code']

    player.assign_current_decision('fold')
    player.assign_to_fold(current_gameboard)

    return flag_config_dict['successful_action']




def check(player, current_gameboard):
    """ 
    determine if player can check. 
    criterias:
        Not fold and lose
        if current_bet_count == 0 and current_raise_count == 0 

    Args:
        current_gameboard

    Returns:
        flag(flag_config_dict):

    """
    logger.debug(f'{player.player_name} decides to --- Check ---')
    return flag_config_dict["check"]





def bet(player, current_gameboard, first_bet):
    """ 
    determine if player can bet. 
    criterias:
        Not fold and lose
        if current_bet_count == 0 

    Args:
        current_gameboard

    Returns:
        flag(flag_config_dict):

    """
    logger.debug(f'{player.player_name} decides to --- Bet ---')
    


    if current_gameboard['current_bet_count'] == 1:
        logger.debug(f'{player.player_name}: I cannot bet since there is a bet before')
        return flag_config_dict['failure_code']



    total_bet = remove_chips_from_player_hand(player, first_bet, 'bet', current_gameboard)
    if not total_bet or total_bet < first_bet:
        logger.debug(f'{player.player_name} does not have enough chips to bet')
        return flag_config_dict['failure_code']

    logger.debug(f'{player.player_name}: as the first player, I bet with chips ${first_bet}')
    if total_bet != first_bet:
        logger.debug(f'{player.player_name}: bet number is different as you want, something go wrong...')
        return flag_config_dict['failure_code']

    transfer_chips_from_player_to_board(player, current_gameboard, first_bet)

    current_gameboard['current_bet_count'] += 1
    if current_gameboard['current_bet_count'] > 1:
        raise

    return flag_config_dict['successful_action']


def all_in(player, current_gameboard):
    """
    player wants to put all his/her money to bet
    :param player:
    :param current_gameboard:
    :return:
    """
    logger.debug(f'{player.player_name} decides to --- All-in --- with amount ${player.current_cash}!')

    if player.current_cash <= 0:
        logger.debug(f'{player.player_name} does not have more money for betting')
        return flag_config_dict['failure_code']


    total_bet = remove_chips_from_player_hand(player, player.current_cash, 'all_in', current_gameboard)
    if not total_bet or total_bet < player.current_cash:
        logger.debug('something went wrong when extract chips from player hand')
        return flag_config_dict['failure_code']

    # board should recognize this and concluding game at the end of this round
    # current_gameboard['is_one_player_out_of_money'] = True
    player.assign_to_all_in(current_gameboard)
    # add info into side pot for the board
    current_gameboard['board'].side_pot[player.player_name] = player.bet_amount_each_game
    # money of all-in going into the board
    transfer_chips_from_player_to_board(player, current_gameboard, total_bet)

    return flag_config_dict['successful_action']


def chips_combination_given_amount_old(player, amount, current_gameboard):
    """
    provide proper chips combination with given amount
    :param player: get those chip from this player
    :param amount: amount of chip wanted
    :param current_gameboard:
    :return: result chips dict, remaining amount (0 means corrected)
    """
    logger.debug(f'{player.player_name} now wants to compute available chips combination for bet')
    keys = sorted(player.chips.keys(), key=lambda x: -x)
    res = dict()

    for key in keys:
        if not player.chips[key]:
            continue
        while amount and key <= amount and player.chips[key]:
            cur_chip = player.chips[key].pop()
            amount -= key
            if key not in res:
                res[key] = list([cur_chip])
            else:
                res[key].append(cur_chip)

    # change a large chip to $1 chip
    change_amount = 1
    num2color, num2weight = current_gameboard['num2color'], current_gameboard['num2weight']
    if amount > 0:  # current chips is not enough
        for key in keys:
            if not player.chips[key]:
                continue
            while player.chips[key] and amount > 0:
                cur_chip = player.chips[key].pop()
                num_of_exchange = cur_chip.get_amount() // change_amount
                new_chips_list = list()

                for i in range(num_of_exchange):
                    new_chip = Chip(amount=change_amount, color=num2color[change_amount], weight=num2weight[change_amount])
                    new_chips_list.append(new_chip)

                while amount > 0 and new_chips_list:
                    amount -= change_amount
                    if change_amount not in res:
                        res[change_amount] = list([new_chips_list.pop()])
                    else:
                        res[change_amount].append(new_chips_list.pop())

                # put remaining into player pocket
                for c in new_chips_list:
                    player.chips[change_amount].add(c)

    # logger.debug(f'{player.player_name} gives the chips info below:')
    # print_chips_info(res)

    return res, amount

def chips_combination_given_amount(player, amount, current_gameboard):
    """ 
    Args:
        current_gameboard

    Returns:

    """
    logger.debug(f'{player.player_name} now wants to compute available chips combination for bet')
    keys = sorted(player.chips.keys(), key=lambda x: -x)
    res = dict()

    for key in keys:
        if not player.chips[key]:
            continue
        while amount and key <= amount and player.chips[key]:
            cur_chip = player.chips[key].pop()
            amount -= key
            if key not in res:
                res[key] = list([cur_chip])
            else:
                res[key].append(cur_chip)

    # change a large chip to $1 chip
    change_amount = 1
    num2color, num2weight = current_gameboard['num2color'], current_gameboard['num2weight']
    if amount > 0:  # current chips is not enough
        for key in keys:
            if not player.chips[key]:
                continue
            while player.chips[key] and amount > 0:
                cur_chip = player.chips[key].pop()
                num_of_exchange = cur_chip.get_amount() // change_amount
                new_chips_list = list()

                for i in range(num_of_exchange):
                    new_chip = Chip(amount=change_amount, color=num2color[change_amount], weight=num2weight[change_amount])
                    new_chips_list.append(new_chip)

                while amount > 0 and new_chips_list:
                    amount -= change_amount
                    if change_amount not in res:
                        res[change_amount] = list([new_chips_list.pop()])
                    else:
                        res[change_amount].append(new_chips_list.pop())

                # put remaining into player pocket
                for c in new_chips_list:
                    player.chips[change_amount].add(c)

    # logger.debug(f'{player.player_name} gives the chips info below:')
    # print_chips_info(res)

    return res, amount

# def split_larger_chips_to_smaller_chips(player, amount_list, amount_you_want, current_gameboard):
#     """
#     current strategy is to change any one larger chip to $1 chip
#     :param player:
#     :param amount_list:
#     :return: True if the player still have other chips to use, otherwise False
#     """
#     logger.debug(f'Board: starting to exchange chips for {player.player_name}')
#     cur_chip = None
#     num2color = current_gameboard['num2color']
#     num2weight = current_gameboard['num2weight']
#
#     for amount in amount_list:
#         if player.chips[amount]:
#             cur_chip = player.chips[amount].pop()
#             num_of_exchange = cur_chip.get_amount() // amount_you_want
#             for i in range(num_of_exchange):
#                 player.chips[amount_you_want].add(Chip(amount=amount_you_want, color=num2color[amount], weight=num2weight[amount]))
#             break
#
#     if cur_chip:
#         logger.debug(f'{player.player_name} has change ${cur_chip.get_amount()} chip to {num_of_exchange} '
#               f'number of ${amount_you_want} chips')
#     else:
#         logger.debug(f'{player.player_name} does not have more chips to exchange')
#
#     return True if cur_chip else False

