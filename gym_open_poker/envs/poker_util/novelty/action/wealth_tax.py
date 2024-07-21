import gym
import sys

import gym_open_poker
from action import Action
import action

# import action_choices
from action_choices import call, all_in, raise_bet, bet, check, fold
from phase import Phase
from flag_config import flag_config_dict
from player import Player
import dealer


import logging

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.novelty.action.wealth_tax")


class WealthTax(gym.Wrapper):
    """
    If the player holds the highest wealth and opts to bet or raise, they must contribute an additional {tax_ratio} of
    the bet to the pot.

    """

    def __init__(self, env, tax_ratio=0.5):

        super().__init__(env)

        sys.modules["action_choices"].bet = getattr(sys.modules[__name__], "_alter_bet")
        sys.modules["action_choices"].raise_bet = getattr(sys.modules[__name__], "_alter_raise_bet")
        global TAX_RATIO
        TAX_RATIO = tax_ratio


def _alter_raise_bet(current_gameboard, player):
    """

    Args:
        current_gameboard
        player


    Returns:
        flag(flag_config_dict):

    """
    player.action_history.append(action.Action.RAISE_BET.name)
    logger.debug(f"{player.player_name} decides to --- Raise Bet ---")

    if current_gameboard["board"].current_bet_count == 0:
        logger.debug(f"{player.player_name}: there is no bet previously, I cannot raise a bet")
        return flag_config_dict["failure_code"]
    elif current_gameboard["board"].current_raise_count == current_gameboard["max_raise_count"]:
        logger.debug(
            f"{player.player_name}: it has reached the max_raise_count = " + str(current_gameboard["max_raise_count"])
        )
        return flag_config_dict["failure_code"]

    if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard["small_bet"]
    elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard["big_bet"]
    else:
        raise

    current_gameboard["board"].current_raise_count += 1

    already_bet = current_gameboard["board"].player_pot[player.player_name]

    bet_to_follow = (
        raise_amount * (current_gameboard["board"].current_bet_count + current_gameboard["board"].current_raise_count)
        - already_bet
    )

    # novelty! Tax
    # check if it is wealthest player
    max_cash_amount = 0
    for p in current_gameboard["players"]:
        if p.status != "lost":
            max_cash_amount = max(max_cash_amount, p.current_cash)
    tax = 0
    for p in current_gameboard["players"]:
        if p.status != "lost" and player.current_cash == max_cash_amount and p.player_name == player.player_name:
            tax = TAX_RATIO * raise_amount

    if tax > 0:
        logger.debug(
            f"Novelty! The wealthiest player has to pay an additional {TAX_RATIO} of the betting amount, i.e., ${tax}."
        )
        player.current_cash -= tax
    #

    if bet_to_follow == 0:
        logger.debug(f"{player.player_name} is big blind and nobody raise_bet, should do the check, not call.")
        return flag_config_dict["failure_code"]
    elif bet_to_follow > player.current_cash:
        logger.debug(f"{player.player_name} current cash {player.current_cash} is smaller than bet want to follow")
        return flag_config_dict["failure_code"]

    #
    player.current_cash -= bet_to_follow

    #
    current_gameboard["board"].player_pot[player.player_name] += bet_to_follow

    #
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.RAISE_BET)

    # the other players have to make decision again
    dealer.update_players_last_move_list_when_raise(current_gameboard, player.player_name)

    return flag_config_dict["successful_action"]


def _alter_bet(current_gameboard, player):
    """
    Args:
        current_gameboard
        player

    Returns:
        flag(flag_config_dict):

    """
    player.action_history.append(action.Action.BET.name)
    logger.debug(f"{player.player_name} decides to --- Bet ---")

    if current_gameboard["board"].current_bet_count == 1:
        logger.debug(f"{player.player_name}: I cannot bet since there is a bet before")
        return flag_config_dict["failure_code"]

    if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard["small_bet"]
    elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard["big_bet"]
    else:
        raise

    already_bet = current_gameboard["board"].player_pot[player.player_name]

    bet_to_follow = raise_amount - already_bet

    # novelty! Tax
    # check if it is wealthest player
    max_cash_amount = 0
    for p in current_gameboard["players"]:
        if p.status != "lost":
            max_cash_amount = max(max_cash_amount, p.current_cash)
    tax = 0
    for p in current_gameboard["players"]:
        if p.status != "lost" and player.current_cash == max_cash_amount and p.player_name == player.player_name:
            tax = TAX_RATIO * raise_amount

    if tax > 0:
        logger.debug(
            f"Novelty! The wealthiest player has to pay an additional {TAX_RATIO} of the betting amount, i.e., ${tax}."
        )
        player.current_cash -= tax
    #

    if bet_to_follow == 0:
        raise
    elif bet_to_follow > player.current_cash:
        logger.debug(f"{player.player_name} current cash {player.current_cash} is smaller than bet want to follow")
        return flag_config_dict["failure_code"]

    #
    player.current_cash -= bet_to_follow

    #
    current_gameboard["board"].player_pot[player.player_name] += bet_to_follow

    #
    current_gameboard["board"].current_bet_count += 1
    if current_gameboard["board"].current_bet_count > 1:
        raise

    #
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.BET)

    # the other players have to make decision again
    dealer.update_players_last_move_list_when_raise(current_gameboard, player.player_name)

    return flag_config_dict["successful_action"]
