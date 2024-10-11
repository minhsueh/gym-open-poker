import gym
import numpy as np
import sys
import logging
import time

import initialize_game_elements

from card_utility_actions import (
    is_royal_flush,
    is_straight,
    is_one_pair,
    is_two_pair,
    is_flush,
    is_full_house,
    is_straight_flush,
    is_three_of_a_kind,
    is_four_of_a_kind,
    is_high_card,
)
from card_utility_actions import (
    get_royal_flush,
    get_straight,
    get_flush,
    get_two_pair,
    get_one_pair,
    get_full_house,
    get_high_card,
    get_straight_flush,
    get_four_of_a_kind,
    get_three_of_a_kind,
)
import dealer


logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.novelty.game_element.buy_in")


class BuyIn(gym.Wrapper):
    """
    This novelty adjusts the initial {buy_in_amount}.
    """

    def __init__(self, env, buy_in_amount=100):

        super().__init__(env)
        sys.modules["initialize_game_elements"].initialize_game_element = getattr(
            sys.modules[__name__], "_alter_initialize_game_element"
        )
        global BUY_IN_AMOUNT
        BUY_IN_AMOUNT = buy_in_amount


def _alter_initialize_game_element(player_decision_agents, customized_arg_dict, random_func):
    """Initialization function for cards, player, board, history, and rules

    Args:
        player_decision_agents:
        random_seet(int)

    Returns:
        game_element variable which contains all elements to use during the game

    Raises:

    """

    game_elements = dict()
    game_elements["small_blind_amount"] = customized_arg_dict.get(
        "small_blind", 5
    )  # this could increase as number of games increase
    game_elements["big_small_blind_ratio"] = customized_arg_dict.get(
        "big_small_blind_ratio", 2
    )  # if small_blind_amount is 1, big blind pay 1 * 2
    game_elements["big_blind_amount"] = game_elements["small_blind_amount"] * game_elements["big_small_blind_ratio"]
    game_elements["small_bet"] = game_elements["big_blind_amount"]  # in pre-flop and flop
    game_elements["big_small_bet_ratio"] = 2
    game_elements["big_bet"] = game_elements["big_blind_amount"] * game_elements["big_small_bet_ratio"]  # in turn and river
    game_elements["max_raise_count"] = customized_arg_dict.get("max_raise_count", 3)

    # novelty!!!!
    game_elements["buy_in_amount"] = BUY_IN_AMOUNT
    logger.debug(f"Novelty! The buy in is modified to {BUY_IN_AMOUNT}")

    game_elements["early_stop"] = False

    # ------termination conditions------
    game_elements["game_count"] = 1
    game_elements["start_time"] = time.time()
    game_elements["max_game_limitation"] = customized_arg_dict.get("max_game_limitation", np.inf)
    game_elements["max_time_limitation"] = customized_arg_dict.get("max_time_limitation", np.inf)

    initialize_game_elements._initialize_cards(game_elements)
    logger.debug("Successfully instantiated and initialized cards.")

    initialize_game_elements._initialize_players(game_elements, player_decision_agents)
    logger.debug("Successfully instantiated and initialized players.")
    random_func.shuffle(game_elements["players"])
    player_seq = ""
    for idx, player in enumerate(game_elements["players"]):
        player.position = idx
        player_seq += player.player_name + " -> "
    logger.debug(player_seq[:-4])
    game_elements["players_dict"] = {player.player_name: player for player in game_elements["players"]}
    game_elements["total_number_of_players"] = len(game_elements["players_dict"])
    game_elements["active_player"] = game_elements["total_number_of_players"]

    initialize_game_elements._initialize_board(game_elements, random_func)
    logger.debug("Successfully instantiated and initialized board.")

    initialize_game_elements._initialize_game_history_structs(game_elements)
    logger.debug("Successfully instantiated game history data structures.")

    initialize_game_elements._initialize_rules(game_elements)
    logger.debug("Successfully instantiated and initialized rules.")

    dealer.print_player_info(game_elements)

    # define hand rank order
    game_elements["hand_rank_type"] = {
        "royal_flush": 10,
        "straight_flush": 9,
        "four_of_a_kind": 8,
        "full_house": 7,
        "flush": 6,
        "straight": 5,
        "three_of_a_kind": 4,
        "two_pairs": 3,
        "one_pair": 2,
        "high_card": 1,
    }
    game_elements["hand_type_list"] = sorted(
        game_elements["hand_rank_type"].keys(), key=lambda x: game_elements["hand_rank_type"][x], reverse=True
    )

    # define hand rank functions
    game_elements["hand_rank_funcs"] = [
        (is_royal_flush, get_royal_flush, "royal_flush"),
        (is_straight_flush, get_straight_flush, "straight_flush"),
        (is_four_of_a_kind, get_four_of_a_kind, "four_of_a_kind"),
        (is_full_house, get_full_house, "full_house"),
        (is_flush, get_flush, "flush"),
        (is_straight, get_straight, "straight"),
        (is_three_of_a_kind, get_three_of_a_kind, "three_of_a_kind"),
        (is_two_pair, get_two_pair, "two_pairs"),
        (is_one_pair, get_one_pair, "one_pair"),
        (is_high_card, get_high_card, "high_card"),
    ]

    # define numbers rank order, initially the number is itself
    game_elements["numbers_rank_type"] = {i: i for i in range(2, 14)}
    game_elements["numbers_rank_type"][1] = 14

    # extra actions
    game_elements["extra_action"] = {}

    return game_elements
