# ===============================================
# limited poker
from phase import Phase
from action import Action
from card_utility_actions import get_best_hand, get_number_rank
import copy
import logging
import collections
import time

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.dealer")


def change_phase(current_gameboard):
    """change the phase
    Args:
        current_gameboard

    Returns:
        new_phase(Phase)

    Raises:

    """

    phase_idx = int(current_gameboard["board"].cur_phase.value)
    new_phase_idx = (phase_idx + 1) % 4
    new_phase = Phase(new_phase_idx)
    current_gameboard["board"].cur_phase = new_phase
    logger.debug("The phase changed to " + str(new_phase))
    return new_phase


def check_and_deal_hole_cards(current_gameboard):
    """The main difference with board.deal_community_card is that the dealer must first check that
    the player status is not lost.

    Dealer should deal the card start from small blind

    Args:
        current_gameboard

    Returns:


    Raises:


    """
    if current_gameboard["board"].cur_phase == Phase.PRE_FLOP:
        logger.debug("======================================================")
        logger.debug(f'Game{current_gameboard["board"].game_idx} is starting.')
        logger.debug(
            "Current dealer position = "
            + str(current_gameboard["board"].dealer_position)
            + "(0-indexed), dealer is "
            + str(current_gameboard["players"][current_gameboard["board"].dealer_position].player_name)
        )
        logger.debug("------------ Dealer is dealing hole cards ------------")

        # put into local variables for better readability
        dealer_position = current_gameboard["board"].dealer_position
        total_number_of_players = current_gameboard["total_number_of_players"]

        for idx in range(dealer_position + 1, dealer_position + total_number_of_players + 1):
            player = current_gameboard["players"][idx % total_number_of_players]

            if player.status != "lost":
                current_gameboard["board"].deal_hole_cards(player, current_gameboard["board"].cur_phase, current_gameboard)

                logger.debug("Current deck has {} cards.".format(current_gameboard["board"].remain_deck_number()))
    else:
        print(
            "The cur_phase at the funciton reset should only be Phase.PRE_FLOP, current value = "
            + str(current_gameboard["board"].cur_phase)
        )
        raise


def check_and_deal_community_card(current_gameboard):
    """We will put card_utility_actions.number_cards_to_draw in this function and use board.deal_community_card_by_number
    to deal with the community cards. In my opinion, number_cards_to_draw should be placed in this module.

    Args:
        current_gameboard

    Returns:


    Raises:

    """
    num_cards_to_deal = -1
    if current_gameboard["board"].cur_phase == Phase.PRE_FLOP:
        print("Should not deal community card in pre_flop phase!")
        raise
    elif current_gameboard["board"].cur_phase == Phase.FLOP:
        num_cards_to_deal = 3
    else:
        num_cards_to_deal = 1

    current_gameboard["board"].deal_community_card_by_number(num_cards_to_deal)


def force_small_big_blind_bet(current_gameboard):
    """This function is called after the function deal_hole_cards, so the next active and next next player after dealer are
    small blind and big blind, respectively.

    Args:
        current_gameboard

    Returns:
        (Boolean): if this function failed, meaning active players have no cash to pay blind

    """

    if current_gameboard["board"].cur_phase == Phase.PRE_FLOP:
        logger.debug(f'Current hand in game: {current_gameboard["board"].game_idx}')
        logger.debug("------------Dealer is forcing small and bid blind bet ------------")

        # put into local variables for better readability
        dealer_position = current_gameboard["board"].dealer_position
        total_number_of_players = current_gameboard["total_number_of_players"]

        # calculate active_players_on_table:
        active_players_on_table = 0
        for player in current_gameboard["players"]:
            if player.status != "lost":
                active_players_on_table += 1

        #
        if active_players_on_table > 2:
            count_blind = 0
            for idx in range(dealer_position + 1, dealer_position + total_number_of_players + 1):
                player = current_gameboard["players"][idx % total_number_of_players]
                if player.status != "lost":
                    # check if small blind have enough cash to afford, or it is lose
                    if count_blind == 0:
                        if player.current_cash >= current_gameboard["small_blind_amount"]:
                            current_gameboard["board"].small_blind_postiion_idx = idx % total_number_of_players
                            player.force_bet_small_blind(current_gameboard)
                            logger.debug(f"{player.player_name} currently has ${player.current_cash}.")
                            count_blind += 1
                            continue
                        else:
                            logger.debug(f"{player.player_name} does not have cash to pay small blind, assign to lost")
                            player.assign_status(current_gameboard, "lost")

                    # check if big blind have enough cash to afford, or it is lose
                    elif count_blind == 1:
                        if (
                            player.current_cash
                            >= current_gameboard["small_blind_amount"] * current_gameboard["big_small_blind_ratio"]
                        ):
                            current_gameboard["board"].big_blind_postiion_idx = idx % total_number_of_players
                            player.force_bet_big_blind(current_gameboard)
                            logger.debug(f"{player.player_name} currently has ${player.current_cash}.")
                            current_gameboard["board"].current_bet_count = 1
                            break
                        else:
                            logger.debug(f"{player.player_name} does not have cash to pay big blind, assign to lost")
                            player.assign_status(current_gameboard, "lost")

        elif active_players_on_table == 2:
            # heads on game: Under practically all rules, the dealer posts the small blind and is first to act preflop.
            # After the flop, the other player acts first.
            count_blind = 0
            for idx in range(dealer_position, dealer_position + total_number_of_players):
                player = current_gameboard["players"][idx % total_number_of_players]
                if player.status != "lost":
                    # check if small blind have enough cash to afford, or it is lose
                    if count_blind == 0:
                        if player.current_cash >= current_gameboard["small_blind_amount"]:
                            current_gameboard["board"].small_blind_postiion_idx = idx % total_number_of_players
                            player.force_bet_small_blind(current_gameboard)
                            logger.debug(f"{player.player_name} currently has ${player.current_cash}.")
                            count_blind += 1
                            continue
                        else:
                            logger.debug(f"{player.player_name} does not have cash to pay small blind, assign to lost")
                            player.assign_status(current_gameboard, "lost")

                    # check if big blind have enough cash to afford, or it is lose
                    elif count_blind == 1:
                        if (
                            player.current_cash
                            >= current_gameboard["small_blind_amount"] * current_gameboard["big_small_blind_ratio"]
                        ):
                            current_gameboard["board"].big_blind_postiion_idx = idx % total_number_of_players
                            player.force_bet_big_blind(current_gameboard)
                            logger.debug(f"{player.player_name} currently has ${player.current_cash}.")
                            current_gameboard["board"].current_bet_count = 1
                            break
                        else:
                            logger.debug(f"{player.player_name} does not have cash to pay big blind, assign to lost")
                            player.assign_status(current_gameboard, "lost")
        else:
            return True

    else:
        raise (
            "The cur_phase at the funciton reset should only be Phase.PRE_FLOP, current value = "
            + str(current_gameboard["board"].cur_phase)
        )

    return False


def check_player1_lost(current_gameboard):
    if current_gameboard["players_dict"]["player_1"].status == "lost":
        return True
    else:
        return False


def conclude_tournament(current_gameboard, early_stop=False):
    """
    Args:
        current_gameboard
        early_stop(Bool): True if the tournament ends without calling conclude_game.
                          This is an indicator to record history.


    Returns:
        None

    """
    logger.debug("Concluding tournament:")

    # add into board.history
    if early_stop:
        #  player's rank
        cur_game_idx = current_gameboard["board"].game_idx
        # rank_list = get_player_rank_list(current_gameboard)
        rank_list = [-1] * len(current_gameboard["players"])  # By here, player_1 is lost, so there is no point for the ranking
        current_gameboard["history"]["rank"][cur_game_idx] = rank_list
        #  player's cash and status
        player_cash_list = []
        player_status_list = []
        for player_idx in range(1, current_gameboard["total_number_of_players"] + 1):
            player = current_gameboard["players_dict"]["player_" + str(player_idx)]
            player_cash_list.append(player.current_cash)
            player_status_list.append(player.status)
        current_gameboard["history"]["cash"][cur_game_idx] = player_cash_list
        current_gameboard["history"]["player_status"][cur_game_idx] = player_status_list

    cash_dict = collections.defaultdict(list)
    for player in current_gameboard["players"]:
        cash = round(player.current_cash, 2)
        cash_dict[cash].append(player.player_name)

    for rank_idx, cash in enumerate(sorted(cash_dict.keys(), reverse=True)):
        for player_name in cash_dict[cash]:
            logger.debug(f"{player_name} ended up having ${cash} with rank {rank_idx+1}.")


def betting(current_gameboard, phase):
    """

    This function should not be used for open AI gym monopoly, because we need to return observation and
    wait for the user's response.

    Args:
        current_gameboard
        phase(Phase)

    Returns:
        None

    """

    pass


def initialize_betting(current_gameboard):
    """

    to initialize the position where to start the betting, current_bet_count, current_raise_count, num_active_player_on_table

    Args:
        current_gameboard
        phase(Phase)

    Returns:
        None

    """

    logger.debug("------------Dealer is initializing the betting parameters. ------------")

    if current_gameboard["board"].cur_phase != Phase.PRE_FLOP:
        current_gameboard["board"].current_bet_count = 0
    current_gameboard["board"].current_raise_count = 0
    for idx, player in enumerate(current_gameboard["players"]):

        if player.status == "lost":
            current_gameboard["board"].players_last_move_list[idx] = Action.LOST
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.LOST
        elif (
            current_gameboard["board"].cur_phase == Phase.PRE_FLOP
            and current_gameboard["board"].small_blind_postiion_idx == idx
            and current_gameboard["board"].players_last_move_list[idx] != Action.ALL_IN
        ):
            current_gameboard["board"].players_last_move_list[idx] = Action.SMALL_BLIND
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.SMALL_BLIND
        elif (
            current_gameboard["board"].cur_phase == Phase.PRE_FLOP
            and current_gameboard["board"].big_blind_postiion_idx == idx
            and current_gameboard["board"].players_last_move_list[idx] != Action.ALL_IN
        ):
            current_gameboard["board"].players_last_move_list[idx] = Action.BIG_BLIND
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.BIG_BLIND
        elif current_gameboard["board"].players_last_move_list[idx] == Action.LOST:
            continue
        elif current_gameboard["board"].players_last_move_list[idx] == Action.FOLD:
            continue
        elif current_gameboard["board"].players_last_move_list[idx] == Action.ALL_IN:
            current_gameboard["board"].players_last_move_list[idx] = Action.ALL_IN_ALREADY
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.ALL_IN_ALREADY
        elif current_gameboard["board"].players_last_move_list[idx] == Action.ALL_IN_ALREADY:
            continue
        else:
            current_gameboard["board"].players_last_move_list[idx] = Action.NONE
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.NONE

    logger.debug("The current current_bet_count is: " + str(current_gameboard["board"].current_bet_count))
    logger.debug("The current current_raise_count is: " + str(current_gameboard["board"].current_raise_count))
    # logger.debug('The current num_active_player_on_table is: ' + str(current_gameboard['num_active_player_on_table']))
    logger.debug("The current players_last_move_list is: " + str(_get_players_last_move_list_string(current_gameboard)))
    logger.debug(
        "The current players_last_move_list_hist is: " + str(_get_players_last_move_list_hist_string(current_gameboard))
    )


def _get_players_last_move_list_string(current_gameboard):
    """

    phrase current_gameboard['board'].players_last_move_list into string and return

    Args:
        current_gameboard
        print_in_initialized(bool): True if using in the funciton initialize_betting(sb and bb included)


    Returns:
        str: players_last_move_list string

    """

    players_last_move_list_string = ""
    for idx, last_move in enumerate(current_gameboard["board"].players_last_move_list):
        if last_move is Action.NONE:
            players_last_move_list_string += "None, "
        else:
            players_last_move_list_string += last_move.name + ", "
    return players_last_move_list_string[:-2]


def _get_players_last_move_list_hist_string(current_gameboard):
    """

    phrase current_gameboard['board'].players_last_move_list_hist into string and return

    Args:
        current_gameboard
        print_in_initialized(bool): True if using in the funciton initialize_betting(sb and bb included)


    Returns:
        str: players_last_move_list string

    """

    players_last_move_list_hist_string = ""
    for idx, last_move in enumerate(current_gameboard["board"].players_last_move_list_hist):
        if last_move is Action.NONE:
            players_last_move_list_hist_string += "None, "
        else:
            players_last_move_list_hist_string += last_move.name + ", "
    return players_last_move_list_hist_string[:-2]


def check_betting_over(current_gameboard):
    """
    We do not need to consider the sequence because it should be handled in the function open_poker._betting


    1. check current_gameboard['board'].players_last_move_list
        (a) only one player stayed in game, i.e., current_gameboard['board'].players_last_move_list has only one non-fold
            or non-lose
        (b) all players check
        (c) all other players call and only one play is bet/raise_bet
        (d) in pre-flop, all CALL and big blind check

    Args:
        current_gameboard

    Returns:
        bool: True if betting is over

    """
    logger.debug("--The dealer is checking if the betting is over.--")
    # logger.debug('The current players_last_move_list is: ' + str(_get_players_last_move_list_string(current_gameboard)))
    #

    total_number_of_players = current_gameboard["total_number_of_players"]

    count_lost = 0
    count_call = 0
    count_check = 0
    count_bet = 0
    count_raise_bet = 0
    count_fold = 0
    count_none = 0
    count_all_in = 0
    count_all_in_already = 0
    for move in current_gameboard["board"].players_last_move_list:
        if move in [Action.NONE, Action.SMALL_BLIND, Action.BIG_BLIND]:
            count_none += 1
        elif move == Action.LOST:
            count_lost += 1
        elif move == Action.CALL:
            count_call += 1
        elif move == Action.CHECK:
            count_check += 1
        elif move == Action.BET:
            count_bet += 1
        elif move == Action.RAISE_BET:
            count_raise_bet += 1
        elif move == Action.FOLD:
            count_fold += 1
        elif move == Action.ALL_IN:
            count_all_in += 1
        elif move == Action.ALL_IN_ALREADY:
            count_all_in_already += 1
        else:
            print("The move is invalid, current move = " + str(move))
            raise

    player_stayed_count = total_number_of_players - count_lost - count_fold - count_all_in_already
    if player_stayed_count == 1:
        logger.debug("Only one player is active, the betting is over.")
        return True

    if count_none > 0:
        logger.debug("At least one player has not moved yet. The betting continues.")
        return False

    logger.debug("All players made the decision, the betting is over.")
    return True


def initialize_round(current_gameboard):
    """
    current_gameboard['board'].player_pot



    Args:
        current_gameboard
        phase(Phase)

    Returns:


    """

    phase = current_gameboard["board"].cur_phase

    # calculate active_players_on_table:
    active_players_on_table = 0
    for player in current_gameboard["players"]:
        if player.status != "lost":
            active_players_on_table += 1

    # put into local variables for better readability
    dealer_position = current_gameboard["board"].dealer_position
    total_number_of_players = current_gameboard["total_number_of_players"]

    if active_players_on_table > 2:
        if phase == Phase.PRE_FLOP:
            # the current_betting_idx should be the player after big blind
            position_after_dealer = 3
        elif phase in [Phase.FLOP, Phase.TURN, Phase.RIVER]:
            # the current_betting_idx should be the player after dealer
            position_after_dealer = 1
        else:
            print("This phase is not valid, current phase = " + str(phase))
            raise

        counter = 0
        found = False
        for idx in range(dealer_position + 1, dealer_position + total_number_of_players + 1):
            player = current_gameboard["players"][idx % total_number_of_players]
            if player.status != "lost":
                counter += 1
                if counter == position_after_dealer:
                    found = True
                    current_gameboard["board"].current_betting_idx = idx % total_number_of_players
                    current_betting_idx_player = player.player_name

        if not found:
            # just to make sure current_betting_idx is updated
            raise ("current_betting_idx is not initializing, please check!")
    elif active_players_on_table == 2:
        # heads up game:
        if phase == Phase.PRE_FLOP:
            # the current_betting_idx should be the player after big blind
            position_after_dealer = 2
        elif phase in [Phase.FLOP, Phase.TURN, Phase.RIVER]:
            # the current_betting_idx should be the player after dealer
            position_after_dealer = 1
        else:
            print("This phase is not valid, current phase = " + str(phase))
            raise

        counter = 0
        found = False
        for idx in range(dealer_position + 1, dealer_position + 2 * total_number_of_players + 1):
            player = current_gameboard["players"][idx % total_number_of_players]
            if player.status != "lost":
                counter += 1
                if counter == position_after_dealer:
                    found = True
                    current_gameboard["board"].current_betting_idx = idx % total_number_of_players
                    current_betting_idx_player = player.player_name
                    break

        if not found:
            # just to make sure current_betting_idx is updated
            raise ("current_betting_idx is not initializing, please check!")

    else:
        raise
    logger.debug(
        "The current current_betting_idx is: "
        + str(current_gameboard["board"].current_betting_idx)
        + "(0-indexed), "
        + current_betting_idx_player
        + " start betting"
    )

    # initialize player.current_money_in_pot
    current_gameboard["board"].player_pot = collections.defaultdict(int)

    for idx, player in enumerate(current_gameboard["players"]):
        if player.status == "lost":
            current_gameboard["board"].players_last_move_list[idx] = Action.LOST
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.LOST
        elif (
            current_gameboard["board"].cur_phase == Phase.PRE_FLOP
            and current_gameboard["board"].small_blind_postiion_idx == idx
            and current_gameboard["board"].players_last_move_list[idx] != Action.ALL_IN
        ):
            current_gameboard["board"].players_last_move_list[idx] = Action.SMALL_BLIND
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.SMALL_BLIND
        elif (
            current_gameboard["board"].cur_phase == Phase.PRE_FLOP
            and current_gameboard["board"].big_blind_postiion_idx == idx
            and current_gameboard["board"].players_last_move_list[idx] != Action.ALL_IN
        ):
            current_gameboard["board"].players_last_move_list[idx] = Action.BIG_BLIND
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.BIG_BLIND
        elif current_gameboard["board"].players_last_move_list[idx] == Action.LOST:
            continue
        elif current_gameboard["board"].players_last_move_list[idx] == Action.FOLD:
            continue
        elif current_gameboard["board"].players_last_move_list[idx] == Action.ALL_IN:
            current_gameboard["board"].players_last_move_list[idx] = Action.ALL_IN_ALREADY
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.ALL_IN_ALREADY
        elif current_gameboard["board"].players_last_move_list[idx] == Action.ALL_IN_ALREADY:
            continue
        else:
            current_gameboard["board"].players_last_move_list[idx] = Action.NONE
            current_gameboard["board"].players_last_move_list_hist[idx] = Action.NONE


def initialize_game(current_gameboard):
    """
    Args:
        current_gameboard
        phase(Phase)

    Returns:


    """
    # game index

    current_gameboard["board"].game_idx += 1

    # reset board
    current_gameboard["board"].reset_board_each_game(current_gameboard)

    # reset player
    for player in current_gameboard["players"]:
        player.reset_player_each_game(current_gameboard)

    # phase
    current_gameboard["board"].cur_phase = Phase.PRE_FLOP


def conclude_round(current_gameboard):
    """
    1. put the bet into pot
    2. if there are all-in player, make a side pot

    in the betting, we will use current_gameboard['board']['player_pot'] to store the amount player spent

    we will use current_gameboard['board']['pots_amount_list'] and current_gameboard['board']['pots_attendee_list']
    to keep track on pot amount and attendee.



    Args:
        current_gameboard

    Returns:
        early_stop(bool): True if only one player active


    """

    # check if there are all-in players
    player_pot = current_gameboard[
        "board"
    ].player_pot  # this is a dictionary with key being player name and value being amount

    all_in_players_list = []  # each element: (player_name, all_in_amount)
    for p_idx, p in enumerate(current_gameboard["players"]):
        if (
            current_gameboard["board"].players_last_move_list[p_idx] == Action.ALL_IN
            or current_gameboard["board"].players_last_move_list[p_idx] == Action.ALL_IN_ALREADY
        ):
            all_in_players_list.append((p.player_name, player_pot[p.player_name]))
    all_in_players_list.sort(key=lambda x: x[1], reverse=True)  # sort all_in_amount in decending order
    # All-in -> side pot
    cur_side_pot_amount_list = []
    cur_side_pot_attendee_list = []
    if all_in_players_list:
        while all_in_players_list:
            all_in_player, all_in_amount = all_in_players_list.pop()
            side_attendee = set()
            for p_idx, p in enumerate(current_gameboard["players"]):
                if player_pot[p.player_name] > all_in_amount:
                    player_pot[p.player_name] -= all_in_amount
                    side_attendee.add(p.player_name)
            if len(side_attendee) != 0:
                cur_side_pot_amount_list.append(all_in_amount * len(side_attendee))
                cur_side_pot_attendee_list.append(side_attendee)

    # main pot if there is no ALL-IN, or rightmost side pot(only these people are active)
    cur_main_pot_amount = 0
    cur_main_pot_attendee = set()
    fold_count = 0
    lost_count = 0
    check_count = 0
    none_count = 0
    for p_idx, p in enumerate(current_gameboard["players"]):
        if current_gameboard["board"].players_last_move_list[p_idx] == Action.LOST:
            lost_count += 1
        elif current_gameboard["board"].players_last_move_list[p_idx] == Action.FOLD:
            fold_count += 1
        elif p.player_name in player_pot:
            # might be fold, bet and call
            cur_main_pot_amount += player_pot[p.player_name]
            cur_main_pot_attendee.add(p.player_name)

        elif current_gameboard["board"].players_last_move_list[p_idx] == Action.CHECK:
            check_count += 1
        elif current_gameboard["board"].players_last_move_list[p_idx] in [
            Action.NONE,
            Action.BIG_BLIND,
        ]:
            none_count += 1
        else:
            print(p.player_name)
            raise

    # recheck
    """
    print(lost_count)
    print(fold_count)
    print(check_count)
    print(cur_main_pot_attendee)
    print(current_gameboard['board'].pots_attendee_list)
    """
    assert (
        none_count + lost_count + fold_count + check_count + len(cur_main_pot_attendee)
        == current_gameboard["total_number_of_players"]
    )

    # put the above two into current_gameboard['board']['pots_amount_list'] and current_gameboard['pots_attendee_list']
    # These might inlcude player who is fold, should recheck again in find_winner(conclude_game)

    current_gameboard["board"].pots_amount_list[-1] += cur_main_pot_amount

    if cur_side_pot_amount_list:
        current_gameboard["board"].pots_amount_list += cur_side_pot_amount_list
        current_gameboard["board"].pots_attendee_list += cur_side_pot_attendee_list

    if len(cur_main_pot_attendee) == 1:
        return True
    elif none_count == 1:
        return True
    else:
        return False


def print_player_info(current_gameboard):
    logger.debug("*********************************************************")
    logger.debug("                       Player Info              ")
    for p in current_gameboard["players"]:
        logger.debug(f"{p.player_name} status: {p.status} with cash: {p.current_cash}")
    logger.debug("*********************************************************")


def print_single_player_cash_info(current_gameboard, player_name):
    for p in current_gameboard["players"]:
        if p.player_name == player_name:
            logger.debug(f"{p.player_name} cash info (current_cash): {p.current_cash}")
            break


def get_player_rank_list(current_gameboard):
    """
    this function will be called in conclude_game, recording rank into board.history

    Returns:
        rank_list(list): following the order as current_gameboard['players'], each element record the rank in this game

    """

    rank_dict = get_rank_dict(current_gameboard)
    hand_type_list = current_gameboard["hand_type_list"]
    ranking_count = 1
    player_ranking_dic = dict()
    for hand_type in hand_type_list:
        if len(rank_dict[hand_type]) != 0:
            for player_hand_list in rank_dict[hand_type]:
                for player_name, hand in player_hand_list:
                    player_ranking_dic[player_name] = (ranking_count, hand)
                ranking_count += 1

    rank_list = []
    for player in current_gameboard["players"]:
        if player.player_name in player_ranking_dic:
            rank_list.append(player_ranking_dic[player.player_name][0])
        else:
            rank_list.append(0)

    return rank_list


def conclude_game(current_gameboard):
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

    main_pot_attendee = current_gameboard["board"].pots_attendee_list[0]

    # assign money
    for pot_idx in range(len(current_gameboard["board"].pots_amount_list)):
        money_amount = current_gameboard["board"].pots_amount_list[pot_idx]
        player_list = current_gameboard["board"].pots_attendee_list[pot_idx]
        winners = find_winner(current_gameboard, player_list)
        assign_money_to_winners(current_gameboard, winners, money_amount)
    # print cash info after assign pot to winners
    print_player_info(current_gameboard)

    # add into board.history
    # player's rank
    cur_game_idx = current_gameboard["board"].game_idx
    rank_list = get_player_rank_list(current_gameboard)
    current_gameboard["history"]["rank"][cur_game_idx] = rank_list
    # player's cash and status
    player_cash_list = []
    player_status_list = []
    for player_idx in range(1, current_gameboard["total_number_of_players"] + 1):
        player = current_gameboard["players_dict"]["player_" + str(player_idx)]
        player_cash_list.append(player.current_cash)
        player_status_list.append(player.status)
    current_gameboard["history"]["cash"][cur_game_idx] = player_cash_list
    current_gameboard["history"]["player_status"][cur_game_idx] = player_status_list

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

    # showdown: record every player's card in main_pot_attendee
    showdown_list = []
    for player in current_gameboard["players"]:
        if player.player_name in main_pot_attendee:
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


def assign_money_to_winners(current_gameboard, winners, money_amount):
    """
    Args:
        current_gameboard
        winners(list[str]): a list of player name
        money_amount(int): the amount to split

    Returns:
        None

    """
    # one winner
    if len(winners) == 1:
        logger.debug(f"{winners[0]} can get ${money_amount}")
        winnner_player = current_gameboard["players_dict"][winners[0]]
        winnner_player.current_cash += money_amount
        return

    # multiple winners
    amount_per_winner = round(money_amount / len(winners), 2)
    logger.debug(f"Board: amount each winner could get is {amount_per_winner}")

    for player_name in winners:
        cur_player = current_gameboard["players_dict"][player_name]
        cur_player.current_cash += amount_per_winner


def find_winner(current_gameboard, player_list):
    """





    Args:
        current_gameboard
        player_list(list): one element in current_gameboard['board'].pots_attendee_list.

    Returns:
        winners(list of str): a list of player_name

    """
    # early stop
    active_player = []
    for player_idx in range(len(current_gameboard["board"].players_last_move_list)):
        if current_gameboard["board"].players_last_move_list[player_idx] not in [
            Action.LOST,
            Action.FOLD,
        ]:
            active_player.append(current_gameboard["players"][player_idx].player_name)
    if len(active_player) == 1:
        return active_player

    #
    rank_dict = get_rank_dict(current_gameboard)
    hand_type_list = current_gameboard["hand_type_list"]
    winners = []
    for hand_type in hand_type_list:
        if len(rank_dict[hand_type]) != 0:
            for player_hand_list in rank_dict[hand_type]:
                for player_name, _ in player_hand_list:
                    if player_name in player_list:
                        winners.append(player_name)
                if len(winners) > 0:
                    logger.debug("The winner is : " + ", ".join(winners))
                    return winners


def log_ranking(current_gameboard):
    """
    Args:
        current_gameboard

    Returns:
        None

    """

    rank_dict = get_rank_dict(current_gameboard)
    hand_type_list = current_gameboard["hand_type_list"]
    ranking_count = 1
    player_ranking_dic = dict()
    for hand_type in hand_type_list:
        if len(rank_dict[hand_type]) != 0:
            for player_hand_list in rank_dict[hand_type]:
                for player_name, hand in player_hand_list:
                    player_ranking_dic[player_name] = (ranking_count, hand)
                ranking_count += 1

    for player_idx, player in enumerate(current_gameboard["players"]):
        if player.player_name in player_ranking_dic:
            rank, hand = player_ranking_dic[player.player_name]
            hand_string = ""
            for num in hand:
                hand_string += str(num)
                hand_string += ", "
            hand_string = hand_string[:-2]
            logger.debug(player.player_name + "'s rank = " + str(rank) + ", which have hand = " + hand_string)
        else:
            logger.debug(
                player.player_name
                + " has no rank becasue it status = "
                + current_gameboard["board"].players_last_move_list[player_idx].name
            )


def log_best_card(current_gameboard):
    """
    Args:
        current_gameboard

    Returns:
        None

    """
    number_rank = get_number_rank()
    for idx, move in enumerate(current_gameboard["board"].players_last_move_list):
        player = current_gameboard["players"][idx]
        community_cards = current_gameboard["board"].community_cards
        hole_cards = player.hole_cards
        total_hand = community_cards + hole_cards
        total_hand_string = ""
        total_hand_number_list = []
        for card in total_hand:
            total_hand_number_list.append(card.get_number())
        for card_num in sorted(total_hand_number_list, key=lambda x: -number_rank[x]):
            total_hand_string += str(card_num)
            total_hand_string += ", "
        total_hand_string = total_hand_string[:-2]
        if move == Action.LOST:
            continue
        elif move != Action.FOLD:
            rank_type2, hand2 = get_best_hand(current_gameboard, total_hand)
            best_hand_string = ""
            for best_num in hand2:
                best_hand_string += str(best_num)
                best_hand_string += ", "
            best_hand_string = best_hand_string[:-2]
            logger.debug(
                player.player_name
                + " has total hands = ("
                + total_hand_string
                + "), having "
                + rank_type2
                + " where best hand is "
                + best_hand_string
            )

        else:
            logger.debug(player.player_name + " is inactive, but has total hands = (" + total_hand_string + ")")


def get_rank_dict(current_gameboard):
    """
    final ranking_list looks like: [[(player_name, total_hand)], [(), ()]]
    process:
    iterate player in current_gameboard['board'].players_last_move_list:
        if player is active:



    Args:
        current_gameboard

    Returns:
        rank_list(dict):
            keys = hand_type
            values = a list of a list of tuple, each tuple contain (player_name, best_hand)

    """
    hand_type_list = current_gameboard["hand_type_list"]
    ranking_dic = {hand_type: [] for hand_type in hand_type_list}

    for idx, move in enumerate(current_gameboard["board"].players_last_move_list):
        player = current_gameboard["players"][idx]
        if move not in [Action.FOLD, Action.LOST]:

            community_cards = current_gameboard["board"].community_cards
            hole_cards = player.hole_cards
            total_hand = community_cards + hole_cards
            rank_type2, hand2 = get_best_hand(current_gameboard, total_hand)
            if len(ranking_dic[rank_type2]) == 0:
                ranking_dic[rank_type2].append([(player.player_name, hand2)])
                continue
            elif len(ranking_dic[rank_type2]) > 0:
                # there is another player having same rank_type, compare each card
                tem_stack = (
                    []
                )  # to store the (player_name, hand) that smaller than current player. This list is in ascending order.
                found = False
                while ranking_dic[rank_type2]:
                    player_hand_list = ranking_dic[rank_type2].pop()
                    # in player_hand_list, every player should have the same hand, so we just need the first one
                    _, hand1 = player_hand_list[0]

                    comparison_res = compare_two_hands(current_gameboard, hand1, hand2)
                    if comparison_res == 0:
                        player_hand_list.append((player.player_name, hand2))
                        tem_stack.append(player_hand_list)
                        found = True
                        break
                    elif comparison_res == 1:
                        tem_stack.append([(player.player_name, hand2)])
                        tem_stack.append(player_hand_list)
                        found = True
                        break

                    tem_stack.append(player_hand_list)

                if not found:
                    tem_stack.append([(player.player_name, hand2)])
                ranking_dic[rank_type2] += tem_stack[::-1]
    return ranking_dic


def compare_two_hands(current_gameboard, hand1, hand2):
    """
    Rank might be equal; hence, we will return a list of tuple as it is not able to represent
    the rank if using list only


    Args:
        current_gameboard
        player1_hand: a list of card value (inteter) with size = 5
        player2_hand: a list of card value (inteter) with size = 5

    Returns:
        (int):
            case1. 1: player1_hand > player2_hand
            case2: 0: player1_hand = player2_hand
            case3: -1: player1_hand < player2_hand



    """
    number_rank = get_number_rank()

    # check if player1 and player2 did not fold or lose

    res = 0
    # Two players have the same rank_type, we need to check hand1 and hand2 one by one
    for card_idx in range(5):
        if number_rank[hand1[card_idx]] > number_rank[hand2[card_idx]]:
            res = 1
            break
        elif number_rank[hand1[card_idx]] < number_rank[hand2[card_idx]]:
            res = -1
            break
    return res


def update_player_last_move(current_gameboard, player_name, move):
    """
    update move to players_last_move_list


    Args:
        current_gameboard
        player_name(str)
        move(Action): the move in ['']

    Returns:
        None

    """
    for player_idx, player in enumerate(current_gameboard["players"]):
        if player.player_name == player_name:
            break
    current_gameboard["board"].players_last_move_list[player_idx] = move
    current_gameboard["board"].players_last_move_list_hist[player_idx] = move


def update_players_last_move_list_when_raise(current_gameboard, raise_player_name):
    """
    when a player bet/raise, the other player meed to decide call/fold/all-in

    process:
        iterate players_last_move_list:
            if player is active(not fold/lost):
                current_gameboard['board'].players_last_move_list[player_idx] = Action.NONE


    Args:
        current_gameboard
        raise_player_name: the name of player who bet/raise

    Returns:
        None

    """

    logger.debug(f"{raise_player_name} bet/raise, updating players_last_move_list")
    for player_idx in range(len(current_gameboard["players"])):
        cur_player = current_gameboard["players"][player_idx]
        if (
            cur_player.player_name != raise_player_name
            and cur_player.status != "lost"
            and current_gameboard["board"].players_last_move_list[player_idx] != Action.FOLD
            and current_gameboard["board"].players_last_move_list[player_idx] != Action.ALL_IN
            and current_gameboard["board"].players_last_move_list[player_idx] != Action.ALL_IN_ALREADY
        ):
            current_gameboard["board"].players_last_move_list[player_idx] = Action.NONE
