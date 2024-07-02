import gym
import sys

import gym_open_poker
from action import Action

# import action_choices
from action_choices import call, all_in, raise_bet, bet, check, fold
from phase import Phase
from flag_config import flag_config_dict
from player import Player


import logging

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.novelty.action.game_fold_restrict")


class GameFoldRestrict(gym.Wrapper):
    """
    This novelty, named 'Action1', restricts the fold action for all players,
    meaning that the optimal action for a user with a suboptimal hand is limited to checking or passively calling.
    """

    def __init__(self, env):

        super().__init__(env)

        sys.modules["player"].Player.compute_allowable_pre_flop_actions = getattr(
            sys.modules[__name__], "_alter_compute_allowable_pre_flop_actions"
        )
        sys.modules["player"].Player.compute_allowable_flop_actions = getattr(
            sys.modules[__name__], "_alter_compute_allowable_flop_actions"
        )
        sys.modules["player"].Player.compute_allowable_turn_actions = getattr(
            sys.modules[__name__], "_alter_compute_allowable_turn_actions"
        )
        sys.modules["player"].Player.compute_allowable_river_actions = getattr(
            sys.modules[__name__], "_alter_compute_allowable_river_actions"
        )
        sys.modules["action_choices"].fold = getattr(sys.modules[__name__], "_alter_fold")


def _alter_compute_allowable_pre_flop_actions(self, current_gameboard):
    """
    novelty: remove fold from allowable_actions

    Args:
        current_gameboard

    Returns:
        allowable_actions(set)

    Raises:

    """
    if current_gameboard["players_dict"][self.player_name].status == "lost":
        raise

    allowable_actions = set()

    # get player_idx
    for player_idx, player in enumerate(current_gameboard["players"]):
        if player.player_name == self.player_name:
            break

    # check if it is fold already
    if current_gameboard["board"].players_last_move_list[player_idx] == Action.FOLD:
        raise

    # 1. fold
    # allowable_actions.add(Action.FOLD)  # can fold at any time

    # bet, raise_bet, call, chcek, all_in

    if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard["small_bet"]
    elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard["big_bet"]
    else:
        raise

    already_bet = current_gameboard["board"].player_pot[player.player_name]
    current_bet_count = current_gameboard["board"].current_bet_count
    current_raise_count = current_gameboard["board"].current_raise_count

    if current_bet_count == 0:
        # bet(all_in)
        if self.current_cash <= raise_amount:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.BET)
        # check
        allowable_actions.add(Action.CHECK)

    elif current_bet_count == 1 and current_raise_count < current_gameboard["max_raise_count"]:

        is_big_blind = False
        # exception: BB in pre-flop
        if current_gameboard["board"].players_last_move_list[player_idx] == Action.BIG_BLIND:
            is_big_blind = True

        # call, all_in
        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
        if (
            current_gameboard["board"].cur_phase == Phase.PRE_FLOP
            and bet_to_follow == 0
            and current_gameboard["board"].players_last_move_list[player_idx] != Action.BIG_BLIND
        ):
            raise
        if is_big_blind and current_raise_count == 0:
            allowable_actions.add(Action.CHECK)
        else:
            if self.current_cash <= bet_to_follow:
                allowable_actions.add(Action.ALL_IN)
            else:
                allowable_actions.add(Action.CALL)

        # raise_bet, all_in
        required_raise_amount = raise_amount * (current_bet_count + current_raise_count + 1) - already_bet
        if self.current_cash <= required_raise_amount:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.RAISE_BET)

    elif current_bet_count == 1 and current_raise_count == current_gameboard["max_raise_count"]:
        # call, all_in

        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
        if bet_to_follow == 0:
            raise

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.CALL)

    else:
        raise

    # logger.debug("allowable_actions = " + ", ".join([action.name for action in allowable_actions]))

    return allowable_actions


def _alter_compute_allowable_flop_actions(self, current_gameboard):
    """
    novelty: remove fold from allowable_actions
    Args:
    current_gameboard

    Returns:
        bool: True if betting is over

    """
    if current_gameboard["players_dict"][self.player_name].status == "lost":
        raise

    allowable_actions = set()

    # get player_idx
    for player_idx, player in enumerate(current_gameboard["players"]):
        if player.player_name == self.player_name:
            break

    # check if it is fold already
    if current_gameboard["board"].players_last_move_list[player_idx] == Action.FOLD:
        raise

    # 1. fold
    # allowable_actions.add(Action.FOLD)  # can fold at any time

    # bet, raise_bet, call, chcek, all_in

    if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard["small_bet"]
    elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard["big_bet"]
    else:
        raise

    already_bet = current_gameboard["board"].player_pot[player.player_name]
    current_bet_count = current_gameboard["board"].current_bet_count
    current_raise_count = current_gameboard["board"].current_raise_count

    if current_bet_count == 0:
        # bet(all_in)
        if self.current_cash <= raise_amount:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.BET)
        # check
        allowable_actions.add(Action.CHECK)

    elif current_bet_count == 1 and current_raise_count < current_gameboard["max_raise_count"]:
        # exception: BB in pre-flop
        if (
            current_gameboard["board"].cur_phase == Phase.PRE_FLOP
            and current_raise_count == 0
            and current_gameboard["board"].players_last_move_list[player_idx] == Action.BIG_BLIND
        ):
            allowable_actions.add(Action.CHECK)

        # call, all_in
        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
        if bet_to_follow == 0:
            raise

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.CALL)

        # raise_bet, all_in
        required_raise_amount = raise_amount * (current_bet_count + current_raise_count + 1) - already_bet
        if self.current_cash <= required_raise_amount:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.RAISE_BET)

    elif current_bet_count == 1 and current_raise_count == current_gameboard["max_raise_count"]:
        # call, all_in

        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
        if bet_to_follow == 0:
            raise

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.CALL)

    else:
        raise

    # logger.debug("allowable_actions = " + ", ".join([action.name for action in allowable_actions]))

    return allowable_actions


def _alter_compute_allowable_turn_actions(self, current_gameboard):
    """
    novelty: remove fold from allowable_actions

    Args:
    current_gameboard

    Returns:
        bool: True if betting is over

    """
    if current_gameboard["players_dict"][self.player_name].status == "lost":
        raise

    allowable_actions = set()

    # get player_idx
    for player_idx, player in enumerate(current_gameboard["players"]):
        if player.player_name == self.player_name:
            break

    # check if it is fold already
    if current_gameboard["board"].players_last_move_list[player_idx] == Action.FOLD:
        raise

    # 1. fold
    # allowable_actions.add(Action.FOLD)  # can fold at any time

    # bet, raise_bet, call, chcek, all_in

    if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard["small_bet"]
    elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard["big_bet"]
    else:
        raise

    already_bet = current_gameboard["board"].player_pot[player.player_name]
    current_bet_count = current_gameboard["board"].current_bet_count
    current_raise_count = current_gameboard["board"].current_raise_count

    if current_bet_count == 0:
        # bet(all_in)
        if self.current_cash <= raise_amount:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.BET)
        # check
        allowable_actions.add(Action.CHECK)

    elif current_bet_count == 1 and current_raise_count < current_gameboard["max_raise_count"]:

        # exception: BB in pre-flop
        if (
            current_gameboard["board"].cur_phase == Phase.PRE_FLOP
            and current_raise_count == 0
            and current_gameboard["board"].players_last_move_list[player_idx] == Action.BIG_BLIND
        ):
            allowable_actions.add(Action.CHECK)

        # call, all_in
        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
        if bet_to_follow == 0:
            raise

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.CALL)

        # raise_bet, all_in
        required_raise_amount = raise_amount * (current_bet_count + current_raise_count + 1) - already_bet
        if self.current_cash <= required_raise_amount:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.RAISE_BET)

    elif current_bet_count == 1 and current_raise_count == current_gameboard["max_raise_count"]:
        # call, all_in

        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
        if bet_to_follow == 0:
            raise

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.CALL)

    else:
        raise

    # logger.debug("allowable_actions = " + ", ".join([action.name for action in allowable_actions]))

    return allowable_actions


def _alter_compute_allowable_river_actions(self, current_gameboard):
    """
    novelty: remove fold from allowable_actions

    Args:
    current_gameboard

    Returns:
        bool: True if betting is over

    """
    if current_gameboard["players_dict"][self.player_name].status == "lost":
        raise

    allowable_actions = set()

    # get player_idx
    for player_idx, player in enumerate(current_gameboard["players"]):
        if player.player_name == self.player_name:
            break

    # check if it is fold already
    if current_gameboard["board"].players_last_move_list[player_idx] == Action.FOLD:
        raise

    # 1. fold
    # allowable_actions.add(Action.FOLD)  # can fold at any time

    # bet, raise_bet, call, chcek, all_in

    if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard["small_bet"]
    elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard["big_bet"]
    else:
        raise

    already_bet = current_gameboard["board"].player_pot[player.player_name]
    current_bet_count = current_gameboard["board"].current_bet_count
    current_raise_count = current_gameboard["board"].current_raise_count

    if current_bet_count == 0:
        # bet(all_in)
        if self.current_cash <= raise_amount:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.BET)
        # check
        allowable_actions.add(Action.CHECK)

    elif current_bet_count == 1 and current_raise_count < current_gameboard["max_raise_count"]:

        # exception: BB in pre-flop
        if (
            current_gameboard["board"].cur_phase == Phase.PRE_FLOP
            and current_raise_count == 0
            and current_gameboard["board"].players_last_move_list[player_idx] == Action.BIG_BLIND
        ):
            allowable_actions.add(Action.CHECK)

        # call, all_in
        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
        if bet_to_follow == 0:
            raise

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.CALL)

        # raise_bet, all_in
        required_raise_amount = raise_amount * (current_bet_count + current_raise_count + 1) - already_bet
        if self.current_cash <= required_raise_amount:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.RAISE_BET)

    elif current_bet_count == 1 and current_raise_count == current_gameboard["max_raise_count"]:
        # call, all_in

        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
        if bet_to_follow == 0:
            raise

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(Action.ALL_IN)
        else:
            allowable_actions.add(Action.CALL)

    else:
        raise

    # logger.debug("allowable_actions = " + ", ".join([action.name for action in allowable_actions]))

    return allowable_actions


def _alter_fold(current_gameboard, player):
    """
    In this novelty, fold is prohibited. So, we directly return flag_config_dict['failure_code'] in any circumstance.

    Args:
        current_gameboard
        player

    Returns:
        flag(flag_config_dict):

    """
    logger.debug(f"{player.player_name} decides to --- Fold ---")
    logger.debug("player cannot fold due to the novelty restriction")
    return flag_config_dict["failure_code"]
