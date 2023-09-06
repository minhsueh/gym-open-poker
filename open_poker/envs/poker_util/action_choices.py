from flag_config import flag_config_dict
import card_utility_actions
import copy
from helper_functions import *
from chip import Chip


# Note: like how skip turn gets removed and conclude actions get added to allowable_actions after a player decides not to skip turn,
# here (check, bet) for all players will be replaced by (call, raise_bet) after bet is made by a player in a round


def null_action():
    """
    :return: successful_action code
    """
    print('executing null action...')
    return flag_config_dict['successful_action']  # does nothing; code is always a success


# def directly_go_to_concluding_phase(player, current_gameboard, condition):
#     """
#     if one player is going out of chips, we should compute and compare their best hand in order to find
#     winner of this game
#     :param player:
#     :param current_gameboard:
#     :return:
#     """
#     print(f'{player.player_name} are {condition}, deal all of community cards and find winner')
#     cur_phase = current_gameboard['cur_phase']
#     if cur_phase == 'pre_flop_phase':
#         current_gameboard['board'].deal_community_card_by_number(5)
#     elif cur_phase == 'flop_phase':
#         current_gameboard['board'].deal_community_card_by_number(2)
#     elif cur_phase == 'turn_phase':
#         current_gameboard['board'].deal_community_card_by_number(1)
#
#     current_gameboard['cur_phase'] = 'concluding_phase'
#     current_gameboard[condition] = True


def call(player, current_gameboard):
    """
    The action of player who would like to match previous bet on the table
    :param player:
    :param current_gameboard:
    :return:
    """
    print(f'{player.player_name} decides to make a --- Call ---')
    is_first_player = is_first_player_in_this_round(player, current_gameboard)
    bet_to_follow = current_gameboard['board'].current_highest_bet

    # if player if small/big blind, the bet to follow should reduce
    if (player.small_blind or player.big_blind) and current_gameboard['cur_phase'] == 'pre_flop_phase':
        bet_to_follow -= player.bet_amount_each_round
        print(f'{player.player_name} is small/big blind, the bet to follow reduced to {bet_to_follow}')
        if bet_to_follow == 0:
            print(f'{player.player_name} is small/big blind and try to call with ${bet_to_follow}')
            return flag_config_dict['successful_action']

    if bet_to_follow > player.current_cash:
        print(f'{player.player_name} current cash {player.current_cash} is smaller than bet want to follow')
        return flag_config_dict['failure_code']
    elif not current_gameboard['board'].players_made_decisions and not is_first_player:
        print(f'{player.player_name}: cannot call at this time since no others bet previously...')
        return flag_config_dict['failure_code']
    elif not current_gameboard['board'].current_highest_bet and not is_first_player:
        print(f'{player.player_name}: cannot call at this time since previous bet is 0...')
        return flag_config_dict['failure_code']

    print(f'{player.player_name} wants to call with amount: {bet_to_follow}')

    total_bet = remove_chips_from_player_hand(player, bet_to_follow, 'call', current_gameboard)
    if not total_bet or total_bet < bet_to_follow:
        print(f'{player.player_name} does not have enough chips to call')
        return flag_config_dict['failure_code']
    elif total_bet != bet_to_follow:
        print(f'{player.player_name}: bet to follow is different from total bet I want')
        return flag_config_dict['failure_code']

    # transfer that amount of money into table
    transfer_chips_from_player_to_board(player, current_gameboard, bet_to_follow)

    return flag_config_dict['successful_action']


def match_highest_bet_on_the_table(player, current_gameboard):
    """
    at the end of each round, if already bet chips but the amount is smaller than the current highest bet on the
    table. In order to continue the game, player should match that bet now
    :param player:
    :param current_gameboard:
    :return:
    """
    print(f'{player.player_name} decides to --- Match ---')
    amount_to_match = current_gameboard['board'].current_highest_bet - player.bet_amount_each_round

    if amount_to_match > player.current_cash:
        print(f'{player.player_name}: current cash {player.current_cash} is smaller than amount want to match')
        return flag_config_dict['failure_code']
    elif player.bet_amount_each_round >= current_gameboard['board'].current_highest_bet:
        print(f'{player.player_name}: my bet is greater than or equal to the highest bet, something go wrong')
        return flag_config_dict['failure_code']

    total_bet = remove_chips_from_player_hand(player, amount_to_match, 'call', current_gameboard)
    if not total_bet or total_bet < amount_to_match:
        print(f'{player.player_name} does not have enough chips to match')
        return flag_config_dict['failure_code']

    transfer_chips_from_player_to_board(player, current_gameboard, amount_to_match)
    print(f'{player.player_name} pays ${amount_to_match} chips to match the highest bet $'
          f'{current_gameboard["board"].current_highest_bet} on the table')

    return flag_config_dict['successful_action']


def remove_chips_from_player_hand(player, amount_of_bet, new_decision, current_gameboard):
    """
    the function used to remove that amount of chips from player
    reduce the corresponding cash from player, and put chips in a side temporarily which would be move to dealer later
    assign new current decision status to the player
    :param player: player object
    :param amount_of_bet: amount of money remove from player
    :param new_decision: decision status
    :return: amount of money removed
    """
    chips, remaining = chips_combination_given_amount(player, amount_of_bet, current_gameboard)
    if not chips or remaining > 0:
        return None  # return failure_code at this time

    player.assign_current_decision(new_decision)
    player.reduce_current_cash(amount_of_bet - remaining)
    player.add_bet_amount_each_round(amount_of_bet - remaining)
    player.bet_amount_each_game += amount_of_bet - remaining

    total_bet = 0
    for amount, chips_list in chips.items():
        total_bet += amount * len(chips_list)
        player.add_current_bet(amount, chips_list)
    return total_bet  # get proper amount of money from this player


def transfer_chips_from_player_to_board(player, current_gameboard, total_bet):
    """
    add amount of money to the dealer, and also update current highest bet on the table in this round
    remove player chips from his/her hand
    :param player: player object
    :param current_gameboard: current gameboard
    :param total_bet: amount of bet to add
    :return: None
    """
    current_gameboard['board'].add_total_cash_on_table(total_bet)
    current_gameboard['board'].compare_for_highest_bet(total_bet)
    current_gameboard['board'].add_chips_to_pot(player.current_bet)
    player.current_bet = dict()


def raise_bet(player, current_gameboard, amount_to_raise):
    """
    In this action, player would like to bet a higher amount then previous bet on the table
    :param player:
    :param current_gameboard:
    :return:
    """
    print(f'{player.player_name} decides to --- Raise Bet ---')
    highest_bet = current_gameboard['board'].current_highest_bet

    if not highest_bet:
        print(f'{player.player_name}: there is no bet previously, I cannot raise a bet')
        return flag_config_dict['failure_code']
    # minimum raise should be the size of last bet
    elif current_gameboard['cur_phase'] == 'pre_flop_phase' and not highest_bet:
        if amount_to_raise < current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']:
            print(f'{player.player_name}: minimum raise bet should be at least size of last bet')
            return flag_config_dict['failure_code']
    elif amount_to_raise < highest_bet:
        print(f'{player.player_name}: minimum raise bet should be at least size of last bet')
        return flag_config_dict['failure_code']

    # new amount after raise with certain amount
    new_bet = highest_bet + amount_to_raise
    if new_bet > player.current_cash:
        print(f'{player.player_name}: current cash {player.current_cash} is smaller than bet {new_bet}')
        return flag_config_dict['failure_code']

    total_bet = remove_chips_from_player_hand(player, new_bet, 'raise_bet', current_gameboard)
    # if do not have enough money, just put as much as player current has
    if not total_bet or total_bet < new_bet:
        print(f'{player.player_name} does not have enough chips to raise bet')
        return flag_config_dict['failure_code']

    print(f'{player.player_name}: I will bet with amount ${new_bet}')
    if total_bet != new_bet:
        print(f'{player.player_name}: do not properly raise a bet with corrected amount')
        return flag_config_dict['failure_code']

    transfer_chips_from_player_to_board(player, current_gameboard, new_bet)

    return flag_config_dict['successful_action']


def fold(player, current_gameboard):
    """
    player decide to end the participation in the current hand
    :param player: player object
    :param current_gameboard: current gameboard
    :return:
    """
    print(f'{player.player_name} decides to --- Fold ---')
    if player.is_fold:
        print(f'{player.player_name}: already fold in previous round, cannot fold again')
        return flag_config_dict['failure_code']

    player.assign_current_decision('fold')
    player.assign_to_fold(current_gameboard)

    return flag_config_dict['successful_action']


def check(player, current_gameboard):
    """
    Player decide to pass on the chance to bet
    :param player:
    :param current_gameboard:
    :return:
    """
    print(f'{player.player_name} decides to --- Check ---')
    return flag_config_dict["check"]


def bet(player, current_gameboard, first_bet):
    """
    the first player who decides to bet a certain amount of money in the round
    minimum number to bet is 20 times of big blind and maximum number to bet is 100 times of big blind
    :param player:
    :param current_gameboard:
    :return:
    """
    print(f'{player.player_name} decides to --- Bet ---')
    prev_bet = current_gameboard['board'].current_highest_bet
    minimum_bet = 20 * current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']
    maximum_bet = 100 * current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']

    if prev_bet:
        print(f'{player.player_name}: I cannot bet since there is a bet ${prev_bet} before')
        return flag_config_dict['failure_code']
    elif first_bet > player.current_cash:
        print(f'{player.player_name}: current cash {player.current_cash} is smaller than {first_bet}')
        return flag_config_dict['failure_code']
    elif first_bet < minimum_bet or first_bet > maximum_bet:
        print(f'{player.player_name}: initial bet should in range {minimum_bet} ~ {maximum_bet}')
        return flag_config_dict['failure_code']

    total_bet = remove_chips_from_player_hand(player, first_bet, 'bet', current_gameboard)
    if not total_bet or total_bet < first_bet:
        print(f'{player.player_name} does not have enough chips to bet')
        return flag_config_dict['failure_code']

    print(f'{player.player_name}: as the first player, I bet with chips ${first_bet}')
    if total_bet != first_bet:
        print(f'{player.player_name}: bet number is different as you want, something go wrong...')
        return flag_config_dict['failure_code']

    transfer_chips_from_player_to_board(player, current_gameboard, first_bet)

    return flag_config_dict['successful_action']


def all_in(player, current_gameboard):
    """
    player wants to put all his/her money to bet
    :param player:
    :param current_gameboard:
    :return:
    """
    print(f'{player.player_name} decides to --- All-in --- with amount ${player.current_cash}!')

    if player.current_cash <= 0:
        print(f'{player.player_name} does not have more money for betting')
        return flag_config_dict['failure_code']


    total_bet = remove_chips_from_player_hand(player, player.current_cash, 'all_in', current_gameboard)
    if not total_bet or total_bet < player.current_cash:
        print('something went wrong when extract chips from player hand')
        return flag_config_dict['failure_code']

    # board should recognize this and concluding game at the end of this round
    # current_gameboard['is_one_player_out_of_money'] = True
    player.assign_to_all_in(current_gameboard)
    # add info into side pot for the board
    current_gameboard['board'].side_pot[player.player_name] = player.bet_amount_each_game
    # money of all-in going into the board
    transfer_chips_from_player_to_board(player, current_gameboard, total_bet)

    return flag_config_dict['successful_action']


def chips_combination_given_amount(player, amount, current_gameboard):
    """
    provide proper chips combination with given amount
    :param player: get those chip from this player
    :param amount: amount of chip wanted
    :param current_gameboard:
    :return: result chips dict, remaining amount (0 means corrected)
    """
    print(f'{player.player_name} now wants to compute available chips combination for bet')
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

    # print(f'{player.player_name} gives the chips info below:')
    # print_chips_info(res)

    return res, amount


# def split_larger_chips_to_smaller_chips(player, amount_list, amount_you_want, current_gameboard):
#     """
#     current strategy is to change any one larger chip to $1 chip
#     :param player:
#     :param amount_list:
#     :return: True if the player still have other chips to use, otherwise False
#     """
#     print(f'Board: starting to exchange chips for {player.player_name}')
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
#         print(f'{player.player_name} has change ${cur_chip.get_amount()} chip to {num_of_exchange} '
#               f'number of ${amount_you_want} chips')
#     else:
#         print(f'{player.player_name} does not have more chips to exchange')
#
#     return True if cur_chip else False

