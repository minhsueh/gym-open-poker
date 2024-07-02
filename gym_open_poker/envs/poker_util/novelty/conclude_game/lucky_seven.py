import gym
import numpy as np
import sys
import copy
import logging
from dealer import find_winner, assign_money_to_winners, print_player_info, get_player_rank_list
from action import Action
import time


logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.novelty.conclude_game.lucky_seven")


class LuckySeven(gym.Wrapper):
    """
    If a player holds hole cards with values smaller than 7 and chooses not to fold in this game,
    they will receive bonus {amount} of cash.
    """

    def __init__(self, env, amount=50):

        super().__init__(env)

        sys.modules["dealer"].conclude_game = getattr(sys.modules[__name__], "_alter_conclude_game")
        global LUCKY_AMOUNT
        LUCKY_AMOUNT = amount


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
    logger.debug("Concluding Game:")
    #
    pot_attendee = set()

    # assign money
    for pot_idx in range(len(current_gameboard["board"].pots_amount_list)):
        money_amount = current_gameboard["board"].pots_amount_list[pot_idx]
        player_list = current_gameboard["board"].pots_attendee_list[pot_idx]
        if len(player_list) > 1:
            winners = find_winner(current_gameboard, player_list)
        elif len(player_list) == 1:
            winners = list(player_list)
        else:
            raise
        assign_money_to_winners(current_gameboard, winners, money_amount)
        # update pot_attendee in this game
        pot_attendee.union(set(player_list))
    # print cash info after assign pot to winners
    print_player_info(current_gameboard)

    # novelty!!!!
    has_lucky_person = False
    for player_idx, player in enumerate(current_gameboard["players"]):
        if (
            player.status != "lost"
            and current_gameboard["board"].players_last_move_list[player_idx] != Action.FOLD
            and all([2 <= card.number <= 7 for card in player.hole_cards])
        ):
            has_lucky_person = True
            logger.debug(
                f"Novelty! {player.player_name} have hole cards with both values smaller than 7, get ${LUCKY_AMOUNT}."
            )
            player.current_cash += LUCKY_AMOUNT
            if player.current_cash <= 0:
                player.assign_status(current_gameboard, "lost")
    if has_lucky_person:
        print_player_info(current_gameboard)

    # add into history
    # player's rank
    cur_game_idx = current_gameboard["board"].game_idx
    rank_list = get_player_rank_list(current_gameboard)
    current_gameboard["history"]["rank"][cur_game_idx] = rank_list
    # player's cash and status
    player_cash_list = []
    player_status_list = []
    player_strategy_list = []
    player_action_dict = dict()
    for player_idx in range(1, current_gameboard["total_number_of_players"] + 1):
        player = current_gameboard["players_dict"]["player_" + str(player_idx)]
        player_cash_list.append(player.current_cash)
        player_status_list.append(player.status)
        player_action_dict["player_" + str(player_idx)] = player.action_history
        player.action_history = []
        if player_idx == 1:
            player_strategy_list.append("player_1")
        else:
            player_strategy_list.append(player.agent.strategy_type)
    current_gameboard["history"]["cash"][cur_game_idx] = player_cash_list
    current_gameboard["history"]["player_status"][cur_game_idx] = player_status_list
    current_gameboard["history"]["player_strategy"][cur_game_idx] = player_strategy_list
    current_gameboard["history"]["action_history"][cur_game_idx] = player_action_dict

    # print(current_gameboard['board'].history)

    # recheck if player is lose
    live_player_list = []
    for player in current_gameboard["players"]:
        if player.status != "lost":
            if player.current_cash > 0:
                live_player_list.append(player.player_name)
            if player.current_cash == 0:
                player.assign_status(current_gameboard, "lost")
                if player.player_name == "player_1":
                    return (True, False)
            elif player.current_cash < 0:
                raise

    # update last reward for each active player
    for player in current_gameboard["players"]:
        if player.status != "lost":
            player.last_reward = player.current_cash - player.last_game_cash
            player.last_game_cash = player.current_cash

    # showdown: record every player's card in pot_attendee
    showdown_list = []
    for player in current_gameboard["players"]:
        if player.player_name in pot_attendee:
            hands = copy.deepcopy(player.hole_cards)
        else:
            hands = [None, None]
        showdown_list.append(hands)
    current_gameboard["board"].previous_showdown = showdown_list

    # if meet termination condition
    current_gameboard["game_count"] += 1
    if time.time() - current_gameboard["start_time"] > current_gameboard["max_time_limitation"]:
        logger.debug("Reach time termination condition = " + str(current_gameboard["max_time_limitation"]) + ". End!")
        return (False, True)
    if current_gameboard["game_count"] > current_gameboard["max_game_limitation"]:
        logger.debug("Reach game termination condition = " + str(current_gameboard["max_game_limitation"]) + ". End!")
        return (False, True)

    # check how many player left
    if len(live_player_list) == 1:
        logger.debug(f"{live_player_list[0]} win! the tournament! End!")
        return (True, False)
    elif len(live_player_list) == 0:
        raise

    return (False, False)
