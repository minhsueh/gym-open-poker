from card import Card
from chip import Chip
from player import Player
from board import Board
from helper_functions import *
from card_utility_actions import calculate_best_hand
from card_utility_actions import (is_royal_flush, is_straight, is_one_pair, is_two_pair, is_flush, is_full_house,
                                  is_straight_flush, is_three_of_a_kind, is_four_of_a_kind)
from card_utility_actions import (get_royal_flush, get_straight, get_flush, get_two_pair, get_one_pair, get_full_house,
                                  get_high_card, get_straight_flush, get_four_of_a_kind, get_three_of_a_kind)
from collections import deque
import sys


def initialize_board(player_decision_agents):
    """
    Initialization function to create all necessary game elements before the game start
    :param player_decision_agents:
    :return: game_element variable which contains all elements to use during the game
    :rtype: dict
    """
    game_elements = dict()
    game_elements['num2color'] = {
        1: 'white',
        5: 'red',
        10: 'blue',
        25: 'green',
        100: 'black',
        500: 'purple',
        1000: 'orange'
    }
    game_elements['num2weight'] = {
        1: 7.5,
        5: 8.5,
        10: 9.0,
        25: 11.5,
        100: 13,
        500: 13.5,
        1000: 14.0
    }
    game_elements['amount2cnt'] = {
        1: 10,
        5: 1,
        10: 0,
        25: 1,
        100: 0,
        500: 2,
        1000: 0
    }

    _initialize_cards(game_elements)
    print('Initialized cards data structures...')

    # initialized chips when initialized players
    _initialize_players(game_elements, player_decision_agents)
    print('Initialized players data structures...')
    print('Initialized chips data structures...')

    _initialize_board(game_elements)
    print('Initialized board data structures...')

    _initialize_game_history_structs(game_elements)
    print('Initialized game history data structures...')

    game_elements['type'] = "game_elements"
    game_elements['hands_of_players'] = [dict()]  # each game result in dict, -1 should be least game
    game_elements['small_blind_amount'] = 1  # this could increase as number of games increase
    game_elements['big_blind_pay_from_baseline'] = 2  # if small_blind_amount is 1, big blind pay 1 * 2

    # used for all in condition, and player out of money during the game
    game_elements['players_dict'] = {p.player_name:p for p in game_elements['players']}

    # define hand rank order
    game_elements['hand_rank_type'] = {
        'royal_flush': 10,
        'straight_flush': 9,
        'four_of_a_kind': 8,
        'full_house': 7,
        'flush': 6,
        'straight': 5,
        'three_of_a_kind': 4,
        'two_pairs': 3,
        'one_pair': 2,
        'highest_card': 1
    }

    # define hand rank functions
    game_elements['hand_rank_funcs'] = [
        (is_royal_flush, get_royal_flush, 'royal_flush'),
        (is_straight_flush, get_straight_flush, 'straight_flush'),
        (is_four_of_a_kind, get_four_of_a_kind, 'four_of_a_kind'),
        (is_full_house, get_full_house, 'full_house'),
        (is_flush, get_flush, 'flush'),
        (is_straight, get_straight, 'straight'),
        (is_three_of_a_kind, get_three_of_a_kind, 'three_of_a_kind'),
        (is_two_pair, get_two_pair, 'two_pairs'),
        (is_one_pair, get_one_pair, 'one_pair')
    ]

    # define numbers rank order, initially the number is itself
    game_elements['numbers_rank_type'] = {i: i for i in range(1, 14)}

    game_elements['find_winner'] = getattr(sys.modules[__name__], 'find_winner')
    game_elements['calculate_best_hand'] = getattr(sys.modules[__name__], 'calculate_best_hand')
    game_elements['assign_pot_to_only_winner'] = getattr(sys.modules[__name__], 'assign_pot_to_only_winner')

    # extra actions
    game_elements['extra_action'] = {}

    return game_elements


def _initialize_board(game_elements):
    """
    Initialize game board
    :param game_elements:
    :return:
    """
    dealer = game_elements['players'][0]
    board_args = dict()
    board_args['dealer_name'] = dealer.player_name
    board_args['total_cash'] = 0
    board_args['pot'] = dict()
    board_args['side_pot'] = dict()
    board_args['deck'] = game_elements['deck']
    board_args['deck_idx'] = 0
    board_args['num_active_player_on_table'] = len(game_elements['players'])
    board = Board(**board_args)
    game_elements['board'] = board


def _initialize_players(game_elements, player_decision_agents):
    """
    Initialize all players for each game
    :param game_elements:
    :param player_decision_agents: dict of player name as its corresponding agent object
    :return: None
    """
    amount2cnt = game_elements['amount2cnt']

    players = deque()
    for player_name, agent in player_decision_agents.items():
        player_args = dict()
        player_args['player_name'] = player_name
        player_args['status'] = 'waiting_for_move'  # win, lost, waiting_for_move
        player_args['small_blind'] = False
        player_args['big_blind'] = False
        player_args['is_dealer'] = False
        player_args['hole_cards'] = list()
        player_args['current_bet'] = dict()
        player_args['agent'] = agent
        player_args['current_decision'] = None

        chips = _initialize_chips(game_elements, amount2cnt=amount2cnt)
        player_args['chips'] = chips
        player_args['current_cash'] = sum([chip.amount for amount_set in chips.values() for chip in amount_set])
        players.append(Player(**player_args))
    game_elements['players'] = players


def _initialize_cards(game_elements):
    """
    Initialize all cards in a deck
    :param game_elements:
    :return: None
    """
    nums = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suits = ['club',  'diamond', 'heart', 'spade']
    colors = ['black', 'black', 'red', 'red']
    temp_deck = [(num, suit, color) for num in nums for suit, color in zip(suits, colors)]

    deck = list()
    for num, suit, color in temp_deck:
        if num == 'A':
            card = Card(suit=suit, number=1, is_num_card=False, is_face_card=False, is_ace_card=True, active=1, color=color)
        elif num.isdigit():
            card = Card(suit=suit, number=int(num), is_num_card=True, is_face_card=False, is_ace_card=False, active=1, color=color)
        elif num == 'J':
            card = Card(suit=suit, number=11, is_num_card=False, is_face_card=True, is_ace_card=False, active=1, color=color)
        elif num == 'Q':
            card = Card(suit=suit, number=12, is_num_card=False, is_face_card=True, is_ace_card=False, active=1, color=color)
        elif num == 'K':
            card = Card(suit=suit, number=13, is_num_card=False, is_face_card=True, is_ace_card=False, active=1, color=color)
        deck.append(card)
    game_elements['deck'] = deck


def _initialize_chips(game_elements, amount2cnt):
    """
    Initialize all chips to be used during the game
    :param game_elements:
    :return: None
    """
    amounts = [1, 5, 10, 25, 100, 500, 1000]
    num2color = game_elements['num2color']
    num2weight = game_elements['num2weight']

    chips = dict()
    for amount in amounts:
        chips[amount] = set()
        for _ in range(amount2cnt[amount]):
            chips[amount].add(Chip(amount=amount, color=num2color[amount], weight=num2weight[amount]))
    return chips


def _initialize_game_history_structs(game_elements):
    """
    history key is used to keep record of events happened during the entire game
    :param game_elements: dictionary of game elements
    :return: None
    """
    game_elements['history'] = dict()
    game_elements['history']['function'] = list()
    game_elements['history']['param'] = list()
    game_elements['history']['return'] = list()


# initialize_board({1:1, 2:2})
