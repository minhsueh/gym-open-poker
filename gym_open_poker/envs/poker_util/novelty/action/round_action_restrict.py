import gym
import sys

import gym_open_poker
from action import Action

# import action_choices
from action_choices import call, all_in, raise_bet, bet, check, fold
from phase import Phase
from flag_config import flag_config_dict
from player import Player
import action
import dealer


import logging

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.novelty.action.round_action_restrict")


class RoundActionReStrict(gym.Wrapper):
    """
    This novelty, named 'Action1', restricts the fold action for all players,
    meaning that the optimal action for a user with a suboptimal hand is limited to checking or passively calling.
    """

    def __init__(self, env, restricted_action="fold", restricted_phase="pre-flop"):

        super().__init__(env)
        if restricted_action == "fold":
            sys.modules["action_choices"].fold = getattr(sys.modules[__name__], "_alter_fold")
        elif restricted_action == "call":
            sys.modules["action_choices"].call = getattr(sys.modules[__name__], "_alter_call")
        elif restricted_action == "raise_bet":
            sys.modules["action_choices"].raise_bet = getattr(sys.modules[__name__], "_alter_raise_bet")
        elif restricted_action == "check":
            sys.modules["action_choices"].check = getattr(sys.modules[__name__], "_alter_check")
        elif restricted_action == "bet":
            sys.modules["action_choices"].bet = getattr(sys.modules[__name__], "_alter_bet")
        elif restricted_action == "all_in":
            sys.modules["action_choices"].all_in = getattr(sys.modules[__name__], "_alter_all_in")
        else:
            raise

        if restricted_phase == "pre-flop":
            sys.modules["player"].Player.compute_allowable_pre_flop_actions = getattr(
                sys.modules[__name__], "_alter_compute_allowable_pre_flop_actions"
            )
        elif restricted_phase == "flop":
            sys.modules["player"].Player.compute_allowable_flop_actions = getattr(
                sys.modules[__name__], "_alter_compute_allowable_flop_actions"
            )
        elif restricted_phase == "turn":
            sys.modules["player"].Player.compute_allowable_turn_actions = getattr(
                sys.modules[__name__], "_alter_compute_allowable_turn_actions"
            )
        elif restricted_phase == "river":
            sys.modules["player"].Player.compute_allowable_river_actions = getattr(
                sys.modules[__name__], "_alter_compute_allowable_river_actions"
            )
        else:
            raise

        phase_dict = {"pre-flop": Phase.PRE_FLOP, "flop": Phase.FLOP, "turn": Phase.TURN, "river": Phase.RIVER}
        action_dict = {
            "fold": Action.FOLD,
            "bet": Action.BET,
            "call": Action.CALL,
            "raise": Action.RAISE_BET,
            "all_in": Action.ALL_IN,
            "check": Action.CHECK,
        }
        global RESTRICTED_PHASE, RESTRICTED_ACTION
        RESTRICTED_PHASE = phase_dict[restricted_phase]
        RESTRICTED_ACTION = action_dict[restricted_action]


def _alter_call(current_gameboard, player):
    """
    Args:
        current_gameboard
        player


    Returns:
        flag(flag_config_dict):

    """
    # novelty
    if current_gameboard["board"].cur_phase == RESTRICTED_PHASE:
        logger.debug(f"{player.player_name} decides to --- Call ---")
        logger.debug(f"Novelty! player cannot call in {RESTRICTED_PHASE}")
        return flag_config_dict["failure_code"]
    #

    player.action_history.append(action.Action.CALL.name)
    logger.debug(f"{player.player_name} decides to make a --- Call ---")

    # Basic criteria:
    if current_gameboard["board"].current_bet_count != 1:
        logger.debug(f"{player.player_name}: cannot call at this time since no others bet previously.")
        return flag_config_dict["failure_code"]

    # check player's current_cash is larger than bet_to_follow
    if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard["small_bet"]
    elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard["big_bet"]
    else:
        print("cur_phase is invalid, current value = " + str(current_gameboard["board"].cur_phase))
        raise

    already_bet = current_gameboard["board"].player_pot[player.player_name]

    bet_to_follow = (
        raise_amount * (current_gameboard["board"].current_bet_count + current_gameboard["board"].current_raise_count)
        - already_bet
    )

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
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.CALL)

    return flag_config_dict["successful_action"]


def _alter_raise_bet(current_gameboard, player):
    """

    Args:
        current_gameboard
        player


    Returns:
        flag(flag_config_dict):

    """
    # novelty
    if current_gameboard["board"].cur_phase == RESTRICTED_PHASE:
        logger.debug(f"{player.player_name} decides to --- Raise Bet ---")
        logger.debug(f"Novelty! player cannot raise in {RESTRICTED_PHASE}")
        return flag_config_dict["failure_code"]
    #

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


def _alter_fold(current_gameboard, player):
    """
    1. assign current_gameboard['board'].players_last_move_list[player_name] to FOLD
    2. remove the player from current_gameboard["board"].pots_attendee_list


    criterias:
        Not fold and lose

    Args:
        current_gameboard
        player


    Returns:
        flag(flag_config_dict):

    """
    # novelty
    if current_gameboard["board"].cur_phase == RESTRICTED_PHASE:
        logger.debug(f"{player.player_name} decides to --- Fold ---")
        logger.debug(f"Novelty! player cannot fold in {RESTRICTED_PHASE}")
        return flag_config_dict["failure_code"]
    #

    player.action_history.append(action.Action.FOLD.name)
    logger.debug(f"{player.player_name} decides to --- Fold ---")
    if player.is_fold:
        logger.debug(f"{player.player_name}: already fold in previous round, cannot fold again")
        return flag_config_dict["failure_code"]

    # 1.
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.FOLD)

    # 2.
    for attendee_set in current_gameboard["board"].pots_attendee_list:
        if player.player_name in attendee_set:
            attendee_set.remove(player.player_name)

    return flag_config_dict["successful_action"]


def _alter_check(current_gameboard, player):
    """
    Args:
        current_gameboard
        player


    Returns:
        flag(flag_config_dict):

    """
    # novelty
    if current_gameboard["board"].cur_phase == RESTRICTED_PHASE:
        logger.debug(f"{player.player_name} decides to --- Check ---")
        logger.debug(f"Novelty! player cannot check in {RESTRICTED_PHASE}")
        return flag_config_dict["failure_code"]
    #

    player.action_history.append(action.Action.CHECK.name)
    logger.debug(f"{player.player_name} decides to --- Check ---")

    for player_idx in range(len(current_gameboard["board"].players_last_move_list)):
        p = current_gameboard["players"][player_idx]
        if player.player_name != p.player_name:
            p_last_move = current_gameboard["board"].players_last_move_list[player_idx]

            if (
                action.Action.BET == p_last_move
                or action.Action.RAISE_BET == p_last_move
                or action.Action.BIG_BLIND == p_last_move
            ):
                logger.debug(f"{p.player_name} bet/raise_bet/big_blind, you cannot chcek")
                return flag_config_dict["failure_code"]

    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.CHECK)

    return flag_config_dict["check"]


def _alter_bet(current_gameboard, player):
    """
    Args:
        current_gameboard
        player

    Returns:
        flag(flag_config_dict):

    """
    # novelty
    if current_gameboard["board"].cur_phase == RESTRICTED_PHASE:
        logger.debug(f"{player.player_name} decides to --- Bet ---")
        logger.debug(f"Novelty! player cannot bet in {RESTRICTED_PHASE}")
        return flag_config_dict["failure_code"]
    #

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


def _alter_all_in(current_gameboard, player):
    """
    Args:
        current_gameboard
        player

    Returns:
        flag(flag_config_dict):


    """
    # novelty
    if current_gameboard["board"].cur_phase == RESTRICTED_PHASE:
        logger.debug(f"{player.player_name} decides to --- All-in ---")
        logger.debug(f"Novelty! player cannot all-in in {RESTRICTED_PHASE}")
        return flag_config_dict["failure_code"]
    #

    player.action_history.append(action.Action.ALL_IN.name)
    logger.debug(f"{player.player_name} decides to --- All-in --- with amount ${player.current_cash}!")

    if player.current_cash <= 0:
        logger.debug(f"{player.player_name} does not have more money for betting")
        return flag_config_dict["failure_code"]

    if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
        raise_amount = current_gameboard["small_bet"]
    elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
        raise_amount = current_gameboard["big_bet"]
    else:
        raise

    already_bet = current_gameboard["board"].player_pot[player.player_name]

    # case1: want to call
    bet_to_follow_case1 = (
        raise_amount * (current_gameboard["board"].current_bet_count + current_gameboard["board"].current_raise_count)
        - already_bet
    )
    # case2; want to bet/raise_bet
    bet_to_follow_case2 = (
        raise_amount * (current_gameboard["board"].current_bet_count + current_gameboard["board"].current_raise_count + 1)
        - already_bet
    )

    #
    if player.current_cash > bet_to_follow_case1 and player.current_cash > bet_to_follow_case2:
        # only player.current_cash < bet_to_follow can do the all_in
        logger.debug(
            f"{player.player_name} have ${player.current_cash}, but raise/bet only cost {bet_to_follow_case2}, \
                should not all in"
        )
        return flag_config_dict["failure_code"]

    #
    if player.current_cash > bet_to_follow_case1:
        # case 2
        case = "case2"
    else:
        # case 1
        case = "case1"

    #
    bet_to_follow = player.current_cash

    #
    player.current_cash -= bet_to_follow

    #
    current_gameboard["board"].player_pot[player.player_name] += bet_to_follow

    if case == "case2":
        # update
        if current_gameboard["board"].current_bet_count == 0:
            if bet_to_follow >= raise_amount / 2:
                # "half bet" rule
                current_gameboard["board"].current_bet_count = 1
                # the other players have to make decision again
                dealer.update_players_last_move_list_when_raise(current_gameboard, player.player_name)
        elif current_gameboard["board"].current_raise_count < current_gameboard["max_raise_count"]:
            if bet_to_follow >= raise_amount / 2:
                # "half bet" rule
                current_gameboard["board"].current_raise_count += 1
                # the other players have to make decision again
                dealer.update_players_last_move_list_when_raise(current_gameboard, player.player_name)
        elif current_gameboard["board"].current_raise_count == current_gameboard["max_raise_count"]:
            raise
        else:
            raise

    #
    dealer.update_player_last_move(current_gameboard, player.player_name, action.Action.ALL_IN)

    return flag_config_dict["successful_action"]


def _alter_compute_allowable_pre_flop_actions(self, current_gameboard):
    """

    if you are highest bet in the last move, then you cannot raise_bet again

    1. fold
        always
    2. check
        bet/raise_bet not in last_move
    3. bet
        big_blind already bet, so no bet allowed

    The following depends on current_cash:
    if cash < raise_amount:
        # no call and raise_net. only have all_in
        # no one bet before, or someone bet/raise_bet
        if (current_gameboard['board'].current_bet_count == 0) or (bet/raise_bet in last_move)
            4. all_in
    else:
        # no all_in. have call, and raise_bet.
        5. raise_bet
            current_gameboard['board'].current_raise_count < max
        6. call
            raise_bet in last_move


    corner case:
        big blind
        small blind

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
    allowable_actions.add(Action.FOLD)  # can fold at any time

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

    # novelty
    if RESTRICTED_ACTION in allowable_actions:
        allowable_actions.remove(RESTRICTED_ACTION)

    return allowable_actions


def _alter_compute_allowable_flop_actions(self, current_gameboard):
    """
    1. fold
        always
    2. check
        bet/raise_bet not in last_move


    The following depends on current_cash:
    if cash < raise_amount:
        # no call, bet, and raise_net. only have all_in
        # no one bet before, or someone bet/raise_bet
        if (current_gameboard['board'].current_bet_count == 0) or (bet/raise_bet in last_move)
            6. all_in
    else:
        # no all_in. have call, bet, and raise_net.
        3. bet
            current_gameboard['board'].current_bet_count == 0
        4. raise_bet
            bet/raise_bet in last_move and current_gameboard['board'].current_raise_count < max
        5. call
            bet/raise_bet in last_move

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
    allowable_actions.add(Action.FOLD)  # can fold at any time

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

    # novelty
    if RESTRICTED_ACTION in allowable_actions:
        allowable_actions.remove(RESTRICTED_ACTION)

    return allowable_actions


def _alter_compute_allowable_turn_actions(self, current_gameboard):
    """
    first player: bet or check

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
    allowable_actions.add(Action.FOLD)  # can fold at any time

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

    # novelty
    if RESTRICTED_ACTION in allowable_actions:
        allowable_actions.remove(RESTRICTED_ACTION)

    return allowable_actions


def _alter_compute_allowable_river_actions(self, current_gameboard):
    """
    first player: bet or check

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
    allowable_actions.add(Action.FOLD)  # can fold at any time

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

    # novelty
    if RESTRICTED_ACTION in allowable_actions:
        allowable_actions.remove(RESTRICTED_ACTION)

    return allowable_actions
