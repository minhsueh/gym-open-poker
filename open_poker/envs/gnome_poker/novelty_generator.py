import sys
import numpy as np
from novelty_function import *
from action_choices import *
from card_utility_actions import *
import card_utility_actions
from player import Player
from board import Board
import helper_functions


class Novelty(object):
    def __init__(self):
        pass


class ClassNovelty(Novelty):
    def __init__(self):
        super().__init__()


class AttributeNovelty(Novelty):
    def __init__(self):
        super().__init__()


class RepresentationNovelty(Novelty):
    def __init__(self):
        super().__init__()


class ActionNovelty(Novelty):
    def __init__(self):
        super().__init__()


class ExtraActionNovelty(ActionNovelty):
    def __init__(self):
        super(ExtraActionNovelty, self).__init__()

    def insurance_novelty(self, current_gameboard, alternate_func1, alternate_func2):
        """

        :param current_gameboard:
        :param func1:
        :param func2:
        :return:
        """
        current_gameboard['extra_action']['pay_insurance'] = getattr(sys.modules[__name__], alternate_func1)
        current_gameboard['assign_pot_to_only_winner'] = getattr(sys.modules[__name__], alternate_func2)


class HandAttributeNovelty(AttributeNovelty):
    def __init__(self):
        super(HandAttributeNovelty, self).__init__()

    def card_numbers_novelty(self, current_gameboard, num):
        """
        The novelty is inspired by royal texas, in which we only keep numbers of card from 9 to Ace.
        This time, we give this function more power to have ability to remove any numbers card with parameter
        num
        :param current_gameboard:
        :param num: any cards with number smaller than num will be removed
        :return:
        """
        deck = current_gameboard['deck']
        new_deck = []
        for card in deck:
            if card.number >= num or (card.number == 1 and num < 14):
                new_deck.append(card)
        current_gameboard['deck'] = new_deck

    def pre_flop_allowable_actions_modified_novelty(self, current_gameboard, alternate_func):
        """
        alternate actions in pre-flop
        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        Player.compute_allowable_pre_flop_actions = getattr(sys.modules[__name__], alternate_func)

    def flop_allowable_actions_modified_novelty(self, current_gameboard, alternate_func):
        """
        alternate actions in flop
        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        Player.compute_allowable_flop_actions = getattr(sys.modules[__name__], alternate_func)

    def turn_allowable_actions_modified_novelty(self, current_gamebaord, alternate_func):
        """
        alternate actions in turn
        :param current_gamebaord:
        :param alternate_func:
        :return:
        """
        Player.compute_allowable_turn_actions = getattr(sys.modules[__name__], alternate_func)

    def river_allowable_actions_modified_novelty(self, current_gameboard, alternate_func):
        """
        alternate actions in river
        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        Player.compute_allowable_river_actions = getattr(sys.modules[__name__], alternate_func)

    def invisible_compute_best_hand_novelty(self, current_gameboard, alternate_func):
        """
        when compute current best hand, because previously some cards are invisible, now it is able
        to see all cards
        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        current_gameboard['calculate_best_hand'] = getattr(sys.modules[__name__], alternate_func)


class ObjectAttributeNovelty(AttributeNovelty):
    def __init__(self):
        super(ObjectAttributeNovelty, self).__init__()

    def edit_hand_rank_category(self, current_gameboard, hand_rank_dict, hand_rank_funcs):
        """
        remove some hand rank category. For example, three of a kind cannot be detected and consider as a hand rank
        :param current_gameboard:
        :param hand_rank_dict: new hand rank dict (key: value --> rank name: rank value)
        :param hand_rank_funcs: new hand rank functions (check func, get func, rank name)
        :return:
        """
        current_gameboard['hand_rank_type'] = hand_rank_dict
        current_gameboard['hand_rank_funcs'] = hand_rank_funcs

    def exchange_hand_novelty(self, current_gameboard, alternate_func):
        """
        The novelty is to exchange hands between current active players
        :param current_gameboard: current_gameboard['players'] contains all current active players
        :return: None
        """
        current_gameboard['find_winner'] = getattr(sys.modules[__name__], alternate_func)

    def hand_rank_novelty(self, current_gameboard, random=False, given_hand=None):
        """
        The novelty changes the hand rank order like, flush > three of a kind > ... > highest card
        :param current_gameboard:
        :param random: if true, order of rank will be random
        :param given_hand: if not random, a given rank should be provided in dict format
        :return:
        """
        if random:
            original_hand = current_gameboard['hand_rank_type']
            values = [v for v in original_hand.values()]
            np.random.shuffle(values)

            new_hand = dict()
            i = 0
            for k in original_hand.keys():
                new_hand[k] = values[i]
                i += 1
            current_gameboard['hand_rank_type'] = new_hand
        else:
            current_gameboard['hand_rank_type'] = given_hand

    def number_rank_novelty(self, current_gameboard, random=False, given_hand=None):
        """

        :param current_gameboard:
        :param random: if true, order of rank will be random
        :param given_hand: if not random, a given rank should be provided
        :return:
        """
        if random:
            num2power = current_gameboard['numbers_rank_type']
            values = [v for v in num2power.values()]
            np.random.shuffle(values)

            new_hand = dict()
            i = 0
            for k in num2power.keys():
                new_hand[k] = values[i]
                i += 1
            current_gameboard['numbers_rank_type'] = new_hand
        else:
            current_gameboard['numbers_rank_type'] = given_hand

    def hole_card_invisible_novelty(self, current_gameboard, alternate_func):
        """

        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        Board.deal_hole_cards = getattr(sys.modules[__name__], alternate_func)

    def community_card_invisible_novelty(self, current_gameboard, alternate_func):
        """

        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        Board.deal_community_card = getattr(sys.modules[__name__], alternate_func)
























