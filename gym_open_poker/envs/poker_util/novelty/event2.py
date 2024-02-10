import gym
import sys
import logging
from action import Action
from phase import Phase


logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.novelty.event2")


class Event2(gym.Wrapper):
    """
    In this novelty, Event2 encourages the player in the big blind position to make aggressive moves.
    Specifically, if the player in the big blind position has more cash than the current_gameboard['big_blind_amount']
    (preventing the scenario of the player being already ALL-IN),
    additional money ($current_gameboard['big_blind_amount']) is provided to the player in the big blind position.
    """

    def __init__(self, env):

        super().__init__(env)
        sys.modules["dealer"].force_small_big_blind_bet = getattr(sys.modules[__name__], "_alter_force_small_big_blind_bet")


def _alter_force_small_big_blind_bet(current_gameboard):
    """This function is called after the function deal_hole_cards, so the next active and next next player after
    dealer are small blind and big blind, respectively.

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
                            # novelty
                            if current_gameboard["board"].players_last_move_list[idx] != Action.ALL_IN:
                                logger.debug(
                                    "Novelty event2: providing additional money to the player in the big blind position."
                                )
                                player.current_cash += current_gameboard["big_blind_amount"]
                                logger.debug(f"{player.player_name} currently has ${player.current_cash}.")
                            #
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
                            # novelty
                            if current_gameboard["board"].players_last_move_list[idx] != Action.ALL_IN:
                                logger.debug(
                                    "Novelty event2: providing additional money to the player in the big blind position."
                                )
                                player.current_cash += current_gameboard["big_blind_amount"]
                                logger.debug(f"{player.player_name} currently has ${player.current_cash}.")
                            #
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
