import novelty_generator
import sys
from board import Board
from novelty_function import *


def exchange_hands_novelty(current_gameboard, alternate_func='exchange_hands_and_find_winner'):
    """
    once injecting this novelty, functions for exchange hand randomly at showdown will be executed
    :param current_gameboard:
    :param alternate_func:
    :return:
    """
    ObjectAttributeNovelty = novelty_generator.ObjectAttributeNovelty()
    ObjectAttributeNovelty.exchange_hand_novelty(current_gameboard=current_gameboard, alternate_func=alternate_func)


def exchange_hands_left_novelty(current_gameboard, alternate_func='exchange_hands_left_and_find_winner'):
    """
    exchange hand to left of player at showdown
    :param current_gameboard:
    :param alternate_func:
    :return:
    """
    ObjectAttributeNovelty = novelty_generator.ObjectAttributeNovelty()
    ObjectAttributeNovelty.exchange_hand_novelty(current_gameboard=current_gameboard, alternate_func=alternate_func)


def reorder_hand_ranking(current_gameboard):
    """
    orders of hand ranking will be randomly ordered at this time, like highest card > three of a kind
    but numbers to compare if equal hand will be same as before
    :param current_gameboard:
    :return:
    """
    ObjectAttributeNovelty = novelty_generator.ObjectAttributeNovelty()
    ObjectAttributeNovelty.hand_rank_novelty(current_gameboard, random=True)


def reorder_numbers_ranking(current_gameboard):
    """
    orders of number ranking will be changed at this time, like 1 > 5 or 5 > 6
    but hand ranking like two pairs will be same as before
    :param current_gameboard:
    :return:
    """
    ObjectAttributeNovelty = novelty_generator.ObjectAttributeNovelty()
    ObjectAttributeNovelty.number_rank_novelty(current_gameboard, random=True)


def royal_texas_version(current_gameboard, num=9):
    """
    the novelty remove any cards with number smaller than num
    :param current_gameboard:
    :param num: lower bound for keeping cards
    :return:
    """
    HandAttributeNovelty = novelty_generator.HandAttributeNovelty()
    HandAttributeNovelty.card_numbers_novelty(current_gameboard, num=num)


def finish_flop_round(current_gameboard,
                      alternate_func1='alternate_compute_allowable_pre_flop_actions',
                      alternate_func2='alternate_compute_allowable_flop_actions'):
    """
    The novelty change allowable actions in both pre-flop round and flop round
    In pre-flop round, player could either call/fold or check if it is big blind
    In flop round, player could either all-in/fold which means that the game should conclude at this time
    :param curreng_gameboard:
    :param alternate_func1: new function to compute allowable actions for pre-flop round
    :param alternate_func2: new function to computer allowable actions for flop round
    :return:
    """
    HandAttributeNovelty = novelty_generator.HandAttributeNovelty()
    HandAttributeNovelty.pre_flop_allowable_actions_modified_novelty(current_gameboard, alternate_func1)
    HandAttributeNovelty.flop_allowable_actions_modified_novelty(current_gameboard, alternate_func2)


def undo_finish_flop_round(current_gameboard,
                           alternate_func1='compute_allowable_pre_flop_actions',
                           alternate_func2='compute_allowable_flop_actions'):
    """
    This is not novelty!!!
    After novelty injection 'finish_flop_round', if want to run the normal tournament, then need to inject this function.
    This is only used for experiments.
    :param current_gameboard:
    :param alternate_func1:
    :param alternate_func2:
    :return:
    """
    HandAttributeNovelty = novelty_generator.HandAttributeNovelty()
    HandAttributeNovelty.pre_flop_allowable_actions_modified_novelty(current_gameboard, alternate_func1)
    HandAttributeNovelty.flop_allowable_actions_modified_novelty(current_gameboard, alternate_func2)


def cards_invisible_to_players(current_gameboard,
                               hole_card_type='hole_card', num_hole_card=1,
                               community_card_type='', num_community_card=0,
                               alternate_func1='alternate_deal_hole_cards',
                               alternate_func2='alternate_deal_community_card',
                               alternate_func3='alternate_calculate_best_hand_invisible'):
    """
    the novelty is to make some cards invisible to players. Either hole cards or community cards and also
    number of invisible cards should be determined
    :param current_gameboard:
    :param hole_card_type: 'hole_card'
    :param num_hole_card: up to maximum number of type of the card
    :param community_card_type:
    :param num_community_card
    :param alternate_func1:
    :param alternate_func2:
    :param alternate_func3:
    :return:
    """
    if hole_card_type and community_card_type:
        current_gameboard['invisible_card'] = {
            hole_card_type: num_hole_card,
            community_card_type: num_community_card,
            'players': {},
            'community': {}
        }
    elif hole_card_type:
        current_gameboard['invisible_card'] = {
            hole_card_type: num_hole_card,
            'players': {},
            'community': {}
        }
    elif community_card_type:
        current_gameboard['invisible_card'] = {
            community_card_type: num_community_card,
            'players': {},
            'community': {}
        }

    ObjectAttributeNovelty = novelty_generator.ObjectAttributeNovelty()
    HandAttributeNovelty = novelty_generator.HandAttributeNovelty()
    if 'hole_card' in current_gameboard['invisible_card']:
        ObjectAttributeNovelty.hole_card_invisible_novelty(current_gameboard, alternate_func1)
        HandAttributeNovelty.invisible_compute_best_hand_novelty(current_gameboard, alternate_func3)
    if 'community_card' in current_gameboard['invisible_card']:
        ObjectAttributeNovelty.community_card_invisible_novelty(current_gameboard, alternate_func2)


def undo_draw_card(current_gameboard,
                   alternate_func1='deal_hole_cards',
                   alternate_func2='deal_community_card'):
    """
    This is not novelty!!!
    Similar to previous undo function, only used for experiments which is running in loop
    :param current_gameboard:
    :param alternate_func1:
    :param alternate_func2:
    :return:
    """
    ObjectAttributeNovelty = novelty_generator.ObjectAttributeNovelty()
    ObjectAttributeNovelty.hole_card_invisible_novelty(current_gameboard, alternate_func1)
    ObjectAttributeNovelty.community_card_invisible_novelty(current_gameboard, alternate_func2)


def remove_rank_category(current_gameboard, rank_names={'three_of_a_kind'}):
    """
    remove hand rank categories
    :param current_gameboard:
    :param rank_names: if hand rank in rank_names, it should not be considered
    :return:
    """

    ObjectAttributeNovelty = novelty_generator.ObjectAttributeNovelty()

    cur_hand_rank_funcs = current_gameboard['hand_rank_funcs']
    updated_hand_rank_funcs = [(cur_check, cur_get, name)
                               for cur_check, cur_get, name in cur_hand_rank_funcs
                               if name not in rank_names]

    n = len(updated_hand_rank_funcs) + 1
    updated_hand_rank_dict = dict()
    for cur_check, cur_get, name in updated_hand_rank_funcs:
        updated_hand_rank_dict[name] = n
        n -= 1
    updated_hand_rank_dict['highest_card'] = 1

    ObjectAttributeNovelty.edit_hand_rank_category(current_gameboard, updated_hand_rank_dict, updated_hand_rank_funcs)


def add_rank_category(current_gameboard, rank_name='color_flush', rank_num=5,
                      check_func='is_color_flush',
                      get_func='get_color_flush'):
    """
    adding new hand rank to current rank category. For example, adding a new category called 'color_flush'. If
    player get more than 5 cards with same color, then it should be detected as hand of color_flush
    :param current_gameboard:
    :param rank_name: name of new hand rank
    :param rank_num: how large is this hand rank
    :param check_func: check function for player to see if there is new rank in their hand
    :param get_func: get function for player to extract value from current hand
    :return:
    """
    ObjectAttributeNovelty = novelty_generator.ObjectAttributeNovelty()

    cur_hand_rank_funcs = current_gameboard['hand_rank_funcs']
    cur_hand2rank_number = current_gameboard['hand_rank_type']
    updated_hand_rank_funcs = []
    updated_hand_rank_type = {}

    n = len(cur_hand2rank_number) + 1
    for cur_check, cur_get, name in cur_hand_rank_funcs:
        if n == rank_num:
            updated_hand_rank_funcs.append((getattr(sys.modules[__name__], check_func),
                                            getattr(sys.modules[__name__], get_func),
                                            rank_name))
            updated_hand_rank_type[rank_name] = n
            n -= 1
            updated_hand_rank_funcs.append((cur_check, cur_get, name))
            updated_hand_rank_type[name] = n
        else:
            updated_hand_rank_funcs.append((cur_check, cur_get, name))
            updated_hand_rank_type[name] = n
        n -= 1
    updated_hand_rank_type['highest_card'] = 1

    ObjectAttributeNovelty.edit_hand_rank_category(current_gameboard, updated_hand_rank_type, updated_hand_rank_funcs)


def pay_insurance_after_hole_card(current_gameboard,
                                  insurance_rate=5,
                                  alternate_func1='pay_insurance',
                                  alternate_func2='alternate_assign_pot'):
    """
    an insurance novelty that the bank would pay max insurance_rate * you insurance amount for you if you loss the
    current game. For example, if you pay $100 to buy the insurance and insurance rate is 5, then you loss $600
    in this game, at this time you would only be charge another $100 from your pot. The bank pay extra $500 to the
    winner.
    :param current_gameboard:
    :param insurance_rate: insurance rate for computing max amount could be covered
    :param alternate_func1: function to charge insurance payment for player
    :param alternate_func2: alternate function to assign pot to winner and player who purchase insurance before
    :return:
    """
    # a record of how much players pay for insurance
    current_gameboard['insurance_pot'] = {}
    current_gameboard['insurance_rate'] = insurance_rate
    ExtraActionNovelty = novelty_generator.ExtraActionNovelty()
    ExtraActionNovelty.insurance_novelty(current_gameboard, alternate_func1, alternate_func2)


def draw_card_with_replacement(current_gameboard,
                               alternate_func1='alternate_deal_hole_card_replacement',
                               alternate_func2='alternate_community_hole_card_replacement'):
    """
    novelty with chance to draw repeated card from deck
    :param current_gameboard:
    :param alternate_func1:
    :param alternate_func2:
    :return:
    """
    ObjectAttributeNovelty = novelty_generator.ObjectAttributeNovelty()
    ObjectAttributeNovelty.hole_card_invisible_novelty(current_gameboard, alternate_func1)
    ObjectAttributeNovelty.community_card_invisible_novelty(current_gameboard, alternate_func2)

