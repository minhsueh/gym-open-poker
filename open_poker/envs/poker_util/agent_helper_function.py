import copy
from itertools import groupby
from operator import itemgetter


def get_hand_type(values, suits):
    """
    This functions help agent to check whether their current hand is strong or weak

    Rank of hand below in order (first one the weakest), extra rule for equal hand is that whose hand has the highest hand win:
    1. single
    2. one pair
    3. two pairs
    4. three of a kind
    5. straight
    6. flush (five of same suit)
    7. full house (3 + 2)
    8. four of a kind
    9. straight flush
    10. royal flush
    :param values: list of numbers of current hand
    :param suits: list of suits of current hand
    :return:
    """

    if is_royal_flush(suits, values):
        rank_type = 10

    elif is_straight_flush(suits, values):
        rank_type = 9

    elif is_four_of_a_kind(suits, values):
        rank_type = 8

    elif is_full_house(suits, values):
        rank_type = 7

    elif is_flush(suits, values):
        rank_type = 6

    elif is_straight(suits, values):
        rank_type = 5

    elif is_three_of_a_kind(suits, values):
        rank_type = 4

    elif is_two_pair(suits, values):
        rank_type = 3

    elif is_one_pair(suits, values):
        rank_type = 2

    else:  # this one is only high card
        rank_type = 1

    return rank_type


def is_one_pair(suits, values):
    """
    if hand contains one pairs, return True. Otherwise, return False
    :param suits: list of current suits
    :param values: list of current values
    :return: True if have one pair, otherwise False
    """
    for num in set(values):
        if values.count(num) >= 2:
            return True
    return False


def is_two_pair(suits, values):
    """
    if hand contains two pairs, return True. Otherwise, return False
    :param suits:
    :param values:
    :return:
    """
    cnt = 0
    for num in set(values):
        if values.count(num) >= 2:
            cnt += 1
    return cnt >= 2


def is_three_of_a_kind(suits, values):
    """
    if hand contains three same number card, return True. Otherwise, return False
    :param suits:
    :param values:
    :return:
    """
    for num in set(values):
        if values.count(num) >= 3:
            return True
    return False


def is_straight(suits, values):
    """
    if hand contains straight e.x 23456, return True. Otherwise, return False
    :param suits:
    :param values:
    :return:
    """
    copy_values = copy.copy(values)
    if 1 in copy_values:
        copy_values.append(14)
    copy_values.sort()
    cnt = 1
    for i in range(len(copy_values) - 1):
        if copy_values[i] == copy_values[i+1] - 1:
            cnt += 1
        elif cnt >= 5:
            return True
        else:
            cnt = 1
    return cnt >= 5


def is_flush(suits, values):
    """
    if hand contains 5 same suit, return True. Otherwise, return False
    :param suits:
    :param values:
    :return:
    """
    for suit in set(suits):
        if suits.count(suit) >= 5:
            return True
    return False


def is_full_house(suits, values):
    """
    if hand contains 3 same number cards and another 2 same number cards, return True. Otherwise, return False
    :param suits:
    :param values:
    :return:
    """
    three = 0
    pair = 0
    for num in set(values):
        if values.count(num) == 2:
            pair += 1
        elif values.count(num) >= 3:
            three += 1
    return (three >= 1 and pair >= 1) or (three >= 2)


def is_four_of_a_kind(suits, values):
    """
    if hand contains 4 same number cards, return True. Otherwise, return False
    :param suits:
    :param values:
    :return:
    """
    for num in set(values):
        if values.count(num) >= 4:
            return True
    return False


def is_straight_flush(suits, values):
    """
    if hand has flush and straight at same time, return True. Otherwise, return False
    'club',  'diamond', 'heart', 'spade'
    :param suits:
    :param values:
    :return:
    """
    # cards = [(c.get_number(), c.get_suit()) for c in total_hand]
    cards = [(val, s) for val, s in zip(values, suits)]
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

    if 1 in hand:
        hand.append(14)

    hand.sort(key=lambda x: -x)
    for key, group in groupby(enumerate(hand), key=lambda x: x[0]-x[1]):
        candidate = list(map(itemgetter(1), group))
        if len(candidate) >= 5:
            return True

    return False


def is_royal_flush(suits, values):
    """
    if hand is straight flush and number cards is 10, 11, 12, 13, and A, return True. Otherwise, return False
    :param suits:
    :param values:
    :return:
    """
    royal_num = [10, 11, 12, 13, 1]
    cnt = 0
    if is_straight_flush(suits, values):
        for num in royal_num:
            if num in values:
                cnt += 1
    return cnt == 5


