from flag_config import flag_config_dict
import dealer
import action


from phase import Phase
import logging

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.action_choices")


def call(current_gameboard, player):
    """
    Args:
        current_gameboard
        player


    Returns:
        flag(flag_config_dict):

    """
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


def raise_bet(current_gameboard, player):
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


def fold(current_gameboard, player):
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


def check(current_gameboard, player):
    """
    Args:
        current_gameboard
        player


    Returns:
        flag(flag_config_dict):

    """
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


def bet(current_gameboard, player):
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


def all_in(current_gameboard, player):
    """
    Args:
        current_gameboard
        player

    Returns:
        flag(flag_config_dict):


    """
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
