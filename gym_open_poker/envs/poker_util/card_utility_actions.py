import copy
from itertools import groupby
from operator import itemgetter
from flag_config import flag_config_dict

from phase import Phase

import logging

logger = logging.getLogger('open_poker.envs.poker_util.logging_info.card_utility_actions')


def get_number_rank():

    """
    get the number ranking dictionary, except card 1 is 14, others will be the value itself

    Args:


    Returns:
        (dict)

    """
    number_rank = {i: i for i in range(2, 14)}
    number_rank[1] = 14
    return(number_rank)


def number_cards_to_draw(phase):
    """
    determine number of cards need to be draw from the deck for each round
    :param phase: name of current round
    :return: number of cards
    :rtype: int
    """
    if phase == Phase.PRE_FLOP:
        return 2
    elif phase == Phase.FLOP:
        return 3
    else:
        return 1




def get_best_hand(current_gameboard, total_hand):
    """
    Args:
        current_gameboard
        total_hand: a list of Card objects with size = 7

    Returns:
        rank_type: royal_flush, straight_flush, four_of_a_kind, full_house, flush...
        hand(list[int]): a list of integer with size = 5, only number is needed since suit is only used for hand type

    """
    
    # if len(total_hand) != 7:
    #    raise Exception

    

    hand_rank_functions = current_gameboard['hand_rank_funcs']
    hand = rank_type = None

    # loop start from the highest rank to the lowest, so always the highest would be return
    for cur_check_func, cur_get_func, rank_name in hand_rank_functions:
        if cur_check_func(total_hand):  # detect a hand rank
            hand = cur_get_func(total_hand)
            rank_type = rank_name
            break  # break if find one rank

    
    return rank_type, hand



def is_high_card(total_hand):
    """
    In this case, it always retrun True
    Args:
        total_hand


    Returns:
        True

    """
    
    return True

def is_one_pair(total_hand):

    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    for num in set(values):
        if values.count(num) >= 2:
            return True
    return False


def is_two_pair(total_hand):
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    cnt = 0
    for num in set(values):
        if values.count(num) >= 2:
            cnt += 1
    return cnt >= 2


def is_three_of_a_kind(total_hand):
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    for num in set(values):
        if values.count(num) >= 3:
            return True
    return False


def is_straight(total_hand):
    """
    case1. A 13 12 11 10
    case2. normal

    Args:
        total_hand

    Returns:
        True

    """
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    # special case: A 13 12 11 10
    ace_high_count = 0
    for num in [1, 13, 12, 11, 10]:
        if num in values:
            ace_high_count += 1
        if ace_high_count == 5:
            return(True)


    # other:

    values.sort(reverse=True)
    hand = [values[0]]
    for i in range(1, len(values)):
        if len(hand) >= 5:
            break
        elif values[i] == values[i-1] - 1:
            hand.append(values[i])
        else:
            hand = [values[i]]
    if len(hand) >= 5:
        return(True)
    else:
        return(False)





def is_flush(total_hand):
    
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]


    for suit in set(suits):
        if suits.count(suit) >= 5:
            return True
    return False


def is_full_house(total_hand):
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    three = 0
    pair = 0
    for num in set(values):
        if values.count(num) == 2:
            pair += 1
        elif values.count(num) >= 3:
            three += 1
    return (three >= 1 and pair >= 1) or (three >= 2)


def is_four_of_a_kind(total_hand):
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    for num in set(values):
        if values.count(num) >= 4:
            return True
    return False


def is_straight_flush(total_hand):
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]
     


    cards = zip(values, suits)
    hand = []
    if suits.count('club') >= 5:
        for num, suit in cards:
            if suit == 'club':
                hand.append(num)
    elif suits.count('diamond') >= 5:
        for num, suit in cards:
            if suit == 'diamond':
                hand.append(num)
    elif suits.count('heart') >= 5:
        for num, suit in cards:
            if suit == 'heart':
                hand.append(num)
    elif suits.count('spade') >= 5:
        for num, suit in cards:
            if suit == 'spade':
                hand.append(num)
    else:
        return False
    return(is_straight(total_hand))


def is_royal_flush(total_hand):
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    royal_num = [10, 11, 12, 13, 1]
    cnt = 0
    if is_straight_flush(total_hand):
        for num in royal_num:
            if num in values:
                cnt += 1
    return cnt == 5


# ======================== functions below use to get cards ========================
# return below hand in descending order
def get_high_card(total_hand):
    """
    Just need to compare value only.
    Args:
        total_hand
        suits
        values

    Returns:
        (list): five cards with value in descending order

    """
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    number_rank = get_number_rank()

    return sorted(values, key=lambda x: -number_rank[x])[:5]

    
def get_one_pair(total_hand):
    """
    Just need to compare value only.
    Args:
        total_hand


    Returns:
        (list): five cards with value in descending order

    """
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    number_rank = get_number_rank()

    hand = []
    for num in sorted(set(values), key=lambda x: -number_rank[x]):
        cnt = values.count(num)
        if cnt >= 2:
            hand += [num] * cnt
    if len(hand) < 5:
        values.sort(key=lambda x: -number_rank[x])
        for num in values:
            if num in hand:
                continue
            hand.append(num)
            if len(hand) == 5:
                break
    return hand


def get_two_pair(total_hand):
    """
    Just need to compare value only.
    Args:
        total_hand


    Returns:
        (list): five cards with value in descending order

    """
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    number_rank = get_number_rank()

    hand = []
    for num in sorted(set(values), key=lambda x: -number_rank[x]):
        cnt = values.count(num)
        if cnt >= 2:
            hand += [num] * cnt
    if len(hand) < 5:
        values.sort(key=lambda x: -number_rank[x])
        for num in values:
            if num in hand:
                continue
            hand.append(num)
            if len(hand) == 5:
                break
    if len(hand) > 5:
        hand.sort(key=lambda x: -number_rank[x])
        hand.pop()
    return hand


def get_three_of_a_kind(total_hand):
    """
    Just need to compare value only.
    Args:
        total_hand
        suits
        values

    Returns:
        (list): five cards with value in descending order

    """
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    number_rank = get_number_rank()

    hand = []
    for num in sorted(set(values), key=lambda x: -number_rank[x]):
        cnt = values.count(num)
        if cnt >= 3:
            hand += [num] * cnt
    if len(hand) < 5:
        values.sort(key=lambda x: -number_rank[x])
        for num in values:
            if num in hand:
                continue
            hand.append(num)
            if len(hand) == 5:
                break
    return hand


def get_straight(total_hand):
    """
    special cases:
    1. A 13 12 11 10


    Args:
        total_hand
        suits
        values

    Returns:
        (list): five cards with value in descending order

    """
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    # special case: A 13 12 11 10
    ace_high_count = 0
    for num in [1, 13, 12, 11, 10]:
        if num in values:
            ace_high_count += 1
        if ace_high_count == 5:
            return([1, 13, 12, 11, 10])


    # other:
    
    values.sort(reverse=True)
    hand = [values[0]]
    for i in range(1, len(values)):
        if len(hand) >= 5:
            break
        elif values[i] == values[i-1] - 1:
            hand.append(values[i])
        else:
            hand = [values[i]]
    if len(hand) >= 5:
        return(hand[:5])
    else:
        raise




def get_flush(total_hand):
    """

    Args:
        total_hand
        suits
        values

    Returns:
        (list): five cards with value in descending order

    """

    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    number_rank = get_number_rank()
    hand = []
    res = ''
    for suit in set(suits):
        if suits.count(suit) >= 5:
            res = suit
            break
    for s, v in zip(suits, values):
        if s == res:
            hand.append(v)

    return sorted(hand, key=lambda x: -number_rank[x])[:5]


def get_full_house(total_hand):
    """

    Args:
        total_hand
        suits
        values

    Returns:
        (list): five cards with value in descending order

    """
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    number_rank = get_number_rank()
    hand = []
    pair, three = list(), list()
    for num in sorted(set(values), key=lambda x: -number_rank[x]):
        if values.count(num) == 2:
            pair.append(num)
        elif values.count(num) >= 3:
            three.append(num)
    three.sort(key=lambda x: -number_rank[x])
    pair.sort(key=lambda x: -number_rank[x])


    # we already make sure it is full house

    if len(three) == 2:
        # case1: 2 threes
        return([three[0]] * 3 + [three[1]] * 2)
    else:
        # case2: 1 three and 2 pairs
        # case3: 1 three and 1 pair  
        return([three[0]] * 3 + [pair[0]] * 2)


def get_four_of_a_kind(total_hand):
    """

    Args:
        total_hand
        suits
        values

    Returns:
        (list): five cards with value in descending order

    """

    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    number_rank = get_number_rank()
    hand = []
    for num in sorted(set(values), key=lambda x: -number_rank[x]):
        cnt = values.count(num)
        if cnt >= 4:
            hand += [num] * cnt

    values.sort(key=lambda x: -number_rank[x])
    if len(hand) < 5:
        for num in values:
            if num in hand:
                continue
            hand.append(num)
            if len(hand) == 5:
                break

    return hand


def get_straight_flush(total_hand):
    

    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    return get_straight(total_hand)


def get_royal_flush(total_hand):
    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]

    return get_straight(total_hand)

