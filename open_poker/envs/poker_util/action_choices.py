from flag_config import flag_config_dict
import card_utility_actions
import copy
import dealer
from chip import Chip
import action


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
    if current_gameboard['board'].current_bet_count != 1:
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

    already_bet = current_gameboard['board'].player_pot[player.player_name]
    
    bet_to_follow = raise_amount * (current_gameboard['board'].current_bet_count + current_gameboard['board'].current_raise_count) - already_bet
    
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

    # 
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.CALL)

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

    if current_gameboard['board'].current_bet_count == 0:
        logger.debug(f'{player.player_name}: there is no bet previously, I cannot raise a bet')
        return flag_config_dict['failure_code']
    elif current_gameboard['board'].current_raise_count == current_gameboard['max_raise_count']:
        logger.debug(f'{player.player_name}: it has reached the max_raise_count = ' + str(current_gameboard['max_raise_count']))
        return flag_config_dict['failure_code'] 

    if current_gameboard['board'].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard['small_bet']
    elif current_gameboard['board'].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard['big_bet']
    else:
        raise


    current_gameboard['board'].current_raise_count += 1

    already_bet = current_gameboard['board'].player_pot[player.player_name]
    
    bet_to_follow = raise_amount * (current_gameboard['board'].current_bet_count + current_gameboard['board'].current_raise_count) - already_bet
    
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

    #
    current_gameboard['board'].current_raise_count += 1

    #
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.RAISE_BET)

    # the other players have to make decision again
    dealer.update_players_last_move_list_when_raise(current_gameboard, player.player_name)

    return flag_config_dict['successful_action']




def fold(player, current_gameboard):
    """ 
    1. assign current_gameboard['board'].players_last_move_list[player_name] to FOLD
    2. put amount in player_pot(current spent) into pots_amount_list[-1]
    current_gameboard['board'].player_pot[player_name]
    current_gameboard['board'].pots_amount_list
    3. remove player_name from current_gameboard['board'].pots_attendee_list


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

    # 1.
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.FOLD)

    # 2.
    current_gameboard['board'].pots_amount_list[-1] += current_gameboard['board'].player_pot[player.player_name]
    del current_gameboard['board'].player_pot[player.player_name]

    # 3.
    for player_set in current_gameboard['board'].pots_attendee_list:
        if player.player_name in player_set:
            player_set.remove(player.player_name)



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

    for player_idx in range(len(current_gameboard['board'].players_last_move_list)):
        p = current_gameboard['players'][player_idx]
        p_last_move = current_gameboard['board'].players_last_move_list[player_idx] 

        if action.Action.BET == p_last_move or action.Action.RAISE_BET == p_last_move:
            logger.debug(f'{p.player_name} bet/raise_bet, you cannot chcek')
            return flag_config_dict['failure_code']



    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.CHECK)

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
    


    if current_gameboard['board'].current_bet_count == 1:
        logger.debug(f'{player.player_name}: I cannot bet since there is a bet before')
        return flag_config_dict['failure_code']

    if current_gameboard['board'].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard['small_bet']
    elif current_gameboard['board'].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard['big_bet']
    else:
        raise


    already_bet = current_gameboard['board'].player_pot[player.player_name]
    
    bet_to_follow = raise_amount - already_bet
    
    if bet_to_follow == 0:
        raise
    elif bet_to_follow > player.current_cash:
        logger.debug(f'{player.player_name} current cash {player.current_cash} is smaller than bet want to follow')
        return flag_config_dict['failure_code']

    # 
    player.current_cash -= bet_to_follow
    
    #
    current_gameboard['board'].player_pot[player.player_name] += bet_to_follow

    # 
    current_gameboard['board'].current_bet_count += 1
    if current_gameboard['board'].current_bet_count > 1:
        raise

    #
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.BET)

    # the other players have to make decision again
    dealer.update_players_last_move_list_when_raise(current_gameboard, player.player_name)

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


    if current_gameboard['board'].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard['small_bet']
    elif current_gameboard['board'].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard['big_bet']
    else:
        raise

    already_bet = current_gameboard['board'].player_pot[player.player_name]
    
    if current_gameboard['board'].current_bet_count == 0:
        bet_to_follow = raise_amount - already_bet
    else:
        bet_to_follow = raise_amount * (current_gameboard['board'].current_bet_count + current_gameboard['board'].current_raise_count) - already_bet

    
    if bet_to_follow == 0:
        raise
    elif player.current_cash > bet_to_follow:
        # only player.current_cash < bet_to_follow can do the all_in
        logger.debug(f'{player.player_name} have ${player.current_cash}, but raise/bet only cost {bet_to_follow}, should not all in')
        return flag_config_dict['failure_code']


    #
    bet_to_follow = player.current_cash

    # 
    player.current_cash -= bet_to_follow
    
    #
    current_gameboard['board'].player_pot[player.player_name] += bet_to_follow

    
    #
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.ALL_IN)


    return flag_config_dict['successful_action']


