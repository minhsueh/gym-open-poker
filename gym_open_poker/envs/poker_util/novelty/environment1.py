import gym
import numpy as np
import sys

from gym_open_poker.envs.poker_util.card import Card
from gym_open_poker.envs.poker_util.action import Action
import collections
from gym_open_poker.envs.poker_util.dealer import *

class Environment1(gym.Wrapper):
    """
    This novelty is 'Environment1'.
    At the conclusion of each game, every active player who has not lost will receive an incentive of $10.
    """
    def __init__(self, env):


        super().__init__(env)
        sys.modules['dealer'].conclude_game = getattr(sys.modules[__name__], '_alter_conclude_game')




def _alter_conclude_game(current_gameboard):
    """ 
    winner
        give money
        record all avtive player hole cards

    initialized board
        community card
        holes card
        players_last_move_list
        early_stop

    dealer position




    Args:
        current_gameboard
        phase(Phase)

    Returns:
        terminated(bool): True if only 1 person live
        truncated(bool): True if meet termination condition

    """
    

    #


    main_pot_attendee = current_gameboard['board'].pots_attendee_list[0]

    # assign money
    for pot_idx in range(len(current_gameboard['board'].pots_amount_list)):
        money_amount = current_gameboard['board'].pots_amount_list[pot_idx]
        player_list = current_gameboard['board'].pots_attendee_list[pot_idx]
        winners = find_winner(current_gameboard, player_list)
        assign_money_to_winners(current_gameboard, winners, money_amount)
        # print cash info after assign pot to winners
        print_player_info(current_gameboard)




    # add into board.history
    ##  player's rank
    cur_game_idx = current_gameboard['board'].game_idx
    rank_list = get_player_rank_list(current_gameboard)
    current_gameboard['board'].history['rank'][cur_game_idx] = rank_list
    ##  player's cash and status
    player_cash_list = []
    player_status_list = []
    for player_idx in range(1, current_gameboard['total_number_of_players']+1):
        player = current_gameboard['players_dict']['player_' + str(player_idx)]
        player_cash_list.append(player.current_cash)
        player_status_list.append(player.status)
    current_gameboard['board'].history['cash'][cur_game_idx] = player_cash_list
    current_gameboard['board'].history['player_status'][cur_game_idx] = player_status_list


    # print(current_gameboard['board'].history)



    # recheck if player is lose
    live_player_list = []
    for player in current_gameboard['players']:
        if player.status != 'lost':
            if player.current_cash > 0:
                live_player_list.append(player.player_name)
            if player.current_cash == 0:
                player.assign_status(current_gameboard, 'lost')
                if player.player_name == 'player_1':
                    return(True, False)
            elif player.current_cash < 0:
                raise

    # update last reward for each active player
    for player in current_gameboard['players']:
        if player.status != 'lost':
            player.last_reward = player.current_cash - player.last_game_cash
            player.last_game_cash = player.current_cash



    # showdown: record every player's card in main_pot_attendee
    showdown_list = []
    for player in current_gameboard['players']:
        if player.player_name in main_pot_attendee:
            hands = copy.deepcopy(player.hole_cards)
        else:
            hands = [None, None]
        showdown_list.append(hands)
    current_gameboard['board'].previous_showdown = showdown_list


    # if meet termination condition
    current_gameboard['game_count'] += 1
    if time.time() - current_gameboard['start_time'] > current_gameboard['max_time_limitation']:
        logger.debug('Reach time termination condition = ' + str(current_gameboard['max_time_limitation']) + '. End!')
        return(False, True)
    if current_gameboard['game_count'] > current_gameboard['max_game_limitation']:
        logger.debug('Reach game termination condition = ' + str(current_gameboard['max_game_limitation']) + '. End!')
        return(False, True)



    # check how many player left
    if len(live_player_list) == 1:
        logger.debug(f'{live_player_list[0]} win! the tournament! End!')
        return(True, False)
    elif len(live_player_list) == 0:
        raise



    # novelty!!!!
    for player in current_gameboard['players']:
        if player.status != 'lost':
            player.current_cash += 10


    return(False, False)