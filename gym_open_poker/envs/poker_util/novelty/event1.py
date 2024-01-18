import gym
import numpy as np
import sys

import collections
import logging
from card import Card
from action import Action
from phase import Phase
from card_utility_actions import (is_three_of_a_kind, is_four_of_a_kind, get_three_of_a_kind)


logger = logging.getLogger('gym_open_poker.envs.poker_util.logging_info.novelty.event1')

class Event1(gym.Wrapper):
    """
    If the game meet the following condition,
        1. In the river
        2. Any player achieves three-of-a-kind with the number x,  but not four-of-a-kind already.
        3. The remaining card with the number x is still available in the deck.
    Then, the dealer will distribute the card with the number x to elevate that player's hand to four-of-a-kind.
    Note:
        1. If two players achieve three-of-a-kind, we just choose the first player in player sequence
    """
    def __init__(self, env):


        super().__init__(env)
        sys.modules['dealer'].check_and_deal_community_card = getattr(sys.modules[__name__], '_alter_check_and_deal_community_card')


def _alter_check_and_deal_community_card(current_gameboard):
    """ 
    Normally, we will inject function current_gameboard['board'].deal_community_card_by_number(num_cards_to_deal).
    But in this novelty, we should do it munually.

    Args:
        current_gameboard

    Returns:
        

    Raises:

    """
    num_cards_to_deal = -1
    if current_gameboard['board'].cur_phase == Phase.PRE_FLOP:
        print('Should not deal community card in pre_flop phase!')
        raise
    elif current_gameboard['board'].cur_phase == Phase.FLOP:
        num_cards_to_deal = 3
    else:
        num_cards_to_deal =  1

    # 
    current_gameboard['board'].burn_card()
    

    if current_gameboard['board'].deck_idx + num_cards_to_deal > len(current_gameboard['board'].deck):
        logger.debug('Error: cannot deal more communities cards')
        raise Exception

    # conditions check
    condition1 = False
    ## condition 1
    if current_gameboard['board'].cur_phase == Phase.RIVER:
        condition1 = True

    ## condition 2 & condition 3
    for player in current_gameboard['players']:
        condition2 = condition3 = False
        hole_cards = player.hole_cards
        community_cards = current_gameboard['board'].community_cards
        total_hand = community_cards + hole_cards
        if is_three_of_a_kind(total_hand) and not is_four_of_a_kind(total_hand):
            condition2 = True

        ## condition 3
        if condition2:
            # Get the remaining card for the four-of-a-kind
            hand_number_list = get_three_of_a_kind(total_hand)
            number_counter = collections.Counter(hand_number_list)
            desired_number = None
            desired_suit = None
            for number in number_counter:
                if number_counter[number] == 3:
                    desired_number = number
            all_suit = set(['club', 'diamond', 'heart', 'spade'])
            have_suits = set()
            for card in total_hand:
                if card.number == desired_number:
                    have_suits.add(card.suit)
            desired_suit_set = all_suit - have_suits
            if len(desired_suit_set) != 1:
                raise
            desired_suit = list(desired_suit_set)[0]
            if desired_number is None or desired_suit is None:
                raise
            # check if this card in deck
            found_desired_card = False
            for card_idx, card in enumerate(current_gameboard['board'].deck[(current_gameboard['board'].deck_idx):]):
                if card.suit == desired_suit and card.number == desired_number:
                    distrubing_card = current_gameboard['board'].deck[current_gameboard['board'].deck_idx:][card_idx]
                    condition3 = True
                    found_desired_card = True
                    break
            if found_desired_card:
                break
    if condition1 and condition2 and condition3:
        # deal that card
        current_gameboard['board'].assign_deck_idx(num_cards_to_deal)
        current_gameboard['board'].community_cards.extend([distrubing_card])
        logger.debug('Novelty event1 is injected!')
        logger.debug(f'Current community cards on the table:')
        for c in current_gameboard['board'].community_cards:
            logger.debug(f'---> {c}')

    else:
        community_cards = current_gameboard['board'].deck[current_gameboard['board'].deck_idx: current_gameboard['board'].deck_idx+num_cards_to_deal]
        current_gameboard['board'].assign_deck_idx(num_cards_to_deal)
        current_gameboard['board'].community_cards.extend(community_cards)
        logger.debug(f'Current community cards on the table:')
        for c in current_gameboard['board'].community_cards:
            logger.debug(f'---> {c}')

