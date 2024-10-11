from card import Card
from player import Player
from board import Board
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
from collections import deque
import dealer
import numpy as np
import time
import sys

import logging


logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.init_game_elements")


def initialize_game_element(player_decision_agents, customized_arg_dict, random_func):
    """Initialization function for cards, player, board, history, and rules

    Args:
        player_decision_agents:
        random_seet(int)

    Returns:
        game_element variable which contains all elements to use during the game

    Raises:

    """
    # np.random.seed(random_seed)

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

    # print("-------")
    # print(customized_arg_dict["buy_in_amount"])
    game_elements["buy_in_amount"] = customized_arg_dict.get("buy_in_amount", 200)
    # print(game_elements["buy_in_amount"])

    game_elements["early_stop"] = False

    # ------termination conditions------
    game_elements["game_count"] = 1
    game_elements["start_time"] = time.time()
    game_elements["max_game_limitation"] = customized_arg_dict.get("max_game_limitation", np.inf)
    game_elements["max_time_limitation"] = customized_arg_dict.get("max_time_limitation", np.inf)

    _initialize_cards(game_elements)
    logger.debug("Successfully instantiated and initialized cards.")

    _initialize_players(game_elements, player_decision_agents)
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

    _initialize_board(game_elements, random_func)
    logger.debug("Successfully instantiated and initialized board.")

    _initialize_game_history_structs(game_elements)
    logger.debug("Successfully instantiated game history data structures.")

    _initialize_rules(game_elements)
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


def _initialize_board(game_elements, random_func):
    """
    Initialize game board
    :param game_elements:
    :return:
    """
    # dealer = game_elements['players'][0]
    board_args = dict()
    board_args["total_cash"] = 0
    board_args["pot"] = dict()
    board_args["side_pot"] = dict()
    board_args["deck"] = game_elements["deck"]
    board_args["deck_idx"] = 0
    board_args["buy_in_amount"] = game_elements["buy_in_amount"]
    board_args["num_active_player_on_table"] = len(game_elements["players"])
    board_args["random_func"] = random_func
    board = Board(**board_args)
    game_elements["board"] = board


def _initialize_players(game_elements, player_decision_agents):
    """
    Initialize all players for each game
    :param game_elements:
    :param player_decision_agents: dict of player name as its corresponding agent object
    :return: None
    """
    players = deque()
    for player_name, agent in player_decision_agents.items():
        player_args = dict()
        player_args["player_name"] = player_name
        player_args["status"] = "active"  # lost, active
        player_args["hole_cards"] = list()
        # player_args['current_bet'] = dict()
        player_args["agent"] = agent
        # player_args['current_decision'] = None

        player_args["current_cash"] = game_elements["buy_in_amount"]
        players.append(Player(**player_args))
        # logging stradegy_type
        if player_name != "player_1":
            logger.debug(f"{player_name} is initialized with stradegy_type {agent.strategy_type}")
    game_elements["players"] = players


def _initialize_cards(game_elements):
    """Initialization card into game_elements object
    Args:
        None
    Returns:
    Raises:
    """
    nums = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["club", "diamond", "heart", "spade"]
    colors = ["black", "red", "red", "black"]
    temp_deck = [(num, suit, color) for num in nums for suit, color in zip(suits, colors)]

    deck = list()
    for num, suit, color in temp_deck:
        if num == "A":
            card = Card(suit=suit, number=1, is_num_card=False, is_face_card=False, is_ace_card=True, active=1, color=color)
        elif num.isdigit():
            card = Card(
                suit=suit, number=int(num), is_num_card=True, is_face_card=False, is_ace_card=False, active=1, color=color
            )
        elif num == "J":
            card = Card(suit=suit, number=11, is_num_card=False, is_face_card=True, is_ace_card=False, active=1, color=color)
        elif num == "Q":
            card = Card(suit=suit, number=12, is_num_card=False, is_face_card=True, is_ace_card=False, active=1, color=color)
        elif num == "K":
            card = Card(suit=suit, number=13, is_num_card=False, is_face_card=True, is_ace_card=False, active=1, color=color)
        deck.append(card)
    game_elements["deck"] = deck


def _initialize_game_history_structs(game_elements):

    game_elements["history"] = dict()
    game_elements["history"]["function"] = list()
    game_elements["history"]["param"] = list()
    game_elements["history"]["return"] = list()

    game_elements["history"]["cash"] = dict()  # {game_idx: [player_1's cash, player_2's cash, ...]}}
    game_elements["history"]["cash"][0] = [game_elements["buy_in_amount"]] * len(game_elements["players"])
    game_elements["history"]["rank"] = dict()  # {game_idx: [player_1's rank, player_2's rank, ...]}}
    game_elements["history"]["rank"][0] = [1] * len(game_elements["players"])
    game_elements["history"]["final_rank"] = []
    game_elements["history"]["player_status"] = dict()  # {game_idx: [player_1's status, player_2's status, ...]}}
    game_elements["history"]["player_status"][0] = ["active"] * len(game_elements["players"])
    game_elements["history"]["player_strategy"] = dict()  # {game_idx: [player_1's strategy, player_2's strategy, ...]}}
    game_elements["history"][
        "action_history"
    ] = dict()  # {game_idx: {player_1: [action1, action2 ...], player2: [action1, action2 ...]}}}


def _initialize_rules(game_elements):
    pass
