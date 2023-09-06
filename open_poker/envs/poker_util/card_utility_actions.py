import copy
from itertools import groupby
from operator import itemgetter
from flag_config import flag_config_dict


# def identify_dealer(current_gameboard):
#     pass
#
#
# def identify_start_player(current_gameboard):
#     # if preflop, then player to the left of big blind
#     # else starts with single blind
#     pass
#
#
# def should_this_phase_go_on_for_another_round(current_gameboard):
#     # return true or false, based on:
#     # - false if all players checked
#     # - false if amount put in the pot by all players are equal in that round
#     # - false if all players but one folded , ie, that player WINS the pot  --> number_of_folded_player()
#     # - else true
#     pass
#
#
# def number_of_folded_players(current_gameboard):
#     # calculate number of players that folded at the end of a round from among the active players
#     # return int
#     pass


def number_cards_to_draw(phase):
    """
    determine number of cards need to be draw from the deck for each round
    :param phase: name of current round
    :return: number of cards
    :rtype: int
    """
    if phase == 'pre_flop_phase':
        return 2
    elif phase == 'flop_phase':
        return 3
    else:
        return 1


# functions below is used for calculating best hand for each player
def calculate_best_hand(current_gameboard, player):
    """
    computing the best hand of this player
    :param current_gameboard:
    :param player:
    :return:
    """
    if current_gameboard['cur_phase'] != 'concluding_phase':
        raise Exception

    print(f'{player.player_name} is now calculating its best hand with community cards')
    board = current_gameboard['board']
    community_cards = copy.copy(board.community_cards)
    hole_cards = copy.copy(player.hole_cards)

    total_hand = community_cards + hole_cards
    if len(total_hand) != 7:
        raise Exception

    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]
    for c in total_hand:
        print(c)

    rank_type, hand = check_hands(current_gameboard, total_hand, suits, values, player)

    # recording best hand with corresponding player name
    current_gameboard['hands_of_players'][-1][player.player_name] = (rank_type, hand)

    return flag_config_dict['successful_action']


def check_hands(current_gameboard, total_hand, suits, values, player):
    """
    New version of check hand for flexibility with novelty
    the function use to determine player current highest hand and hand's ranking type
    as hand ranking: royal flush > straight flush > ... > one pair > highest card
    the rank type are: 10, 9, ..., 2, 1 in order
    :param current_gameboard:
    :param total_hand:
    :param suits:
    :param values:
    :param player:
    :return:
    """

    hand_rank_functions = current_gameboard['hand_rank_funcs']
    hand = rank_type = None

    # loop start from the highest rank to the lowest, so always the highest would be return
    for cur_check_func, cur_get_func, rank_name in hand_rank_functions:
        if cur_check_func(total_hand, suits, values):  # detect a hand rank
            hand = cur_get_func(total_hand, suits, values)
            rank_type = current_gameboard['hand_rank_type'][rank_name]
            print(f'{player.player_name} has {rank_name} in hand: {hand}!')
            break  # break if find one rank

    # if not other hand rank detect, compute the highest card
    if not hand or not rank_type:
        hand = get_high_card(total_hand, suits, values)
        rank_type = current_gameboard['hand_rank_type']['highest_card']
        print(f'{player.player_name} has nothing, have to use the highest card: {hand}!')

    return rank_type, hand


# def check_hands(current_gameboard, total_hand, suits, values, player):
#     """
#     the function use to determine player current highest hand and hand's ranking type
#     as hand ranking: royal flush > straight flush > ... > one pair > highest card
#     the rank type are: 10, 9, ..., 2, 1 in order
#     :param total_hand: list of 7 cards contain card object
#     :param suits: list of 7 suits from total hand
#     :param values: list of 7 values from total hand
#     :param player: current player obj
#     :return: rank_type, highest hand list
#     """
#     if is_royal_flush(total_hand, suits, values):
#         hand = get_royal_flush(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['royal_hand']
#         print(f'{player.player_name} has royal flush in hand: {hand}!')
#     elif is_straight_flush(total_hand, suits, values):
#         hand = get_straight_flush(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['straight_flush']
#         print(f'{player.player_name} has straight flush in hand: {hand}!')
#     elif is_four_of_a_kind(total_hand, suits, values):
#         hand = get_four_of_a_kind(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['four_of_a_kind']
#         print(f'{player.player_name} has four of a kind in hand: {hand}!')
#     elif is_full_house(total_hand, suits, values):
#         hand = get_full_house(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['full_house']
#         print(f'{player.player_name} has full house in hand: {hand}!')
#     elif is_flush(total_hand, suits, values):
#         hand = get_flush(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['flush']
#         print(f'{player.player_name} has flush in hand: {hand}!')
#     elif is_straight(total_hand, suits, values):
#         hand = get_straight(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['straight']
#         print(f'{player.player_name} has straight in hand: {hand}!')
#     elif is_three_of_a_kind(total_hand, suits, values):
#         hand = get_three_of_a_kind(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['three_of_a_kind']
#         print(f'{player.player_name} has three of a kind in hand: {hand}!')
#     elif is_two_pair(total_hand, suits, values):
#         hand = get_two_pair(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['two_pairs']
#         print(f'{player.player_name} has two pairs in hand: {hand}!')
#     elif is_one_pair(total_hand, suits, values):
#         hand = get_one_pair(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['one_pair']
#         print(f'{player.player_name} has one pair in hand: {hand}!')
#     else:  # this one is only high card
#         hand = get_high_card(total_hand, suits, values)
#         rank_type = current_gameboard['hand_rank_type']['highest_card']
#         print(f'{player.player_name} has nothing, have to use the highest card: {hand}!')
#
#     return rank_type, hand


"""
Rank of hand below in order (first one the weakest), 
extra rule for equal hand is that whose hand has the highest hand win:
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
"""


def is_one_pair(total_hand, suits, values):
    """
    if hand contains one pairs, return True. Otherwise, return False
    :param total_hand: list of current contains class object
    :param suits: list of current suits
    :param values: list of current values
    :return: True if have one pair, otherwise False
    """
    for num in set(values):
        if values.count(num) >= 2:
            return True
    return False


def is_two_pair(total_hand, suits, values):
    """
    if hand contains two pairs, return True. Otherwise, return False
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    cnt = 0
    for num in set(values):
        if values.count(num) >= 2:
            cnt += 1
    return cnt >= 2


def is_three_of_a_kind(total_hand, suits, values):
    """
    if hand contains three same number card, return True. Otherwise, return False
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    for num in set(values):
        if values.count(num) >= 3:
            return True
    return False


def is_straight(total_hand, suits, values):
    """
    if hand contains straight e.x 23456, return True. Otherwise, return False
    :param total_hand:
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


def is_flush(total_hand, suits, values):
    """
    if hand contains 5 same suit, return True. Otherwise, return False
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    for suit in set(suits):
        if suits.count(suit) >= 5:
            return True
    return False


def is_full_house(total_hand, suits, values):
    """
    if hand contains 3 same number cards and another 2 same number cards, return True. Otherwise, return False
    :param total_hand:
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


def is_four_of_a_kind(total_hand, suits, values):
    """
    if hand contains 4 same number cards, return True. Otherwise, return False
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    for num in set(values):
        if values.count(num) >= 4:
            return True
    return False


def is_straight_flush(total_hand, suits, values):
    """
    if hand has flush and straight at same time, return True. Otherwise, return False
    'club',  'diamond', 'heart', 'spade'
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    cards = [(c.get_number(), c.get_suit()) for c in total_hand]
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


def is_royal_flush(total_hand, suits, values):
    """
    if hand is straight flush and number cards is 10, 11, 12, 13, and A, return True. Otherwise, return False
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    royal_num = [10, 11, 12, 13, 1]
    cnt = 0
    if is_straight_flush(total_hand, suits, values):
        for num in royal_num:
            if num in values:
                cnt += 1
    return cnt == 5


# ======================== functions below use to get cards ========================
# return below hand in descending order
def get_high_card(total_hand, suits, values):
    """
    get 5 cards of high cards
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    hand = []
    if 1 in values:
        hand.append(1)
        return hand + sorted(values, key=lambda x: -x)[:4]
    return sorted(values, key=lambda x: -x)[:5]


def get_one_pair(total_hand, suits, values):
    """
    get a hand contain one pair
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    hand = []
    for num in sorted(set(values), key=lambda x: -x):
        cnt = values.count(num)
        if cnt >= 2:
            hand += [num] * cnt
    if len(hand) < 5:
        values.sort(key=lambda x: -x)
        for num in values:
            if num in hand:
                continue
            hand.append(num)
            if len(hand) == 5:
                break
    return hand


def get_two_pair(total_hand, suits, values):
    """
    get a hand contain two pairs
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    hand = []
    for num in sorted(set(values), key=lambda x: -x):
        cnt = values.count(num)
        if cnt >= 2:
            hand += [num] * cnt
    if len(hand) < 5:
        values.sort(key=lambda x: -x)
        for num in values:
            if num in hand:
                continue
            hand.append(num)
            if len(hand) == 5:
                break
    if len(hand) > 5:
        hand.sort(key=lambda x: -x)
        hand.pop()
    return hand


def get_three_of_a_kind(total_hand, suits, values):
    """
    get a hand contains three of a kind
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    hand = []
    for num in sorted(set(values), key=lambda x: -x):
        cnt = values.count(num)
        if cnt >= 3:
            hand += [num] * cnt
    if len(hand) < 5:
        values.sort(key=lambda x: -x)
        for num in values:
            if num in hand:
                continue
            hand.append(num)
            if len(hand) == 5:
                break
    return hand


def get_straight(total_hand, suits, values):
    """
    get a hand contains a straight
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    hand = []
    if 1 in values:
        values.append(14)
    values.sort()
    for key, group in groupby(enumerate(values), key=lambda x: x[0]-x[1]):
        hand = list(map(itemgetter(1), group))
        if len(hand) >= 5:
            break
    if len(hand) > 5:
        hand = hand[-5:]

    return hand if 14 not in hand else [10, 11, 12, 13, 1]


def get_flush(total_hand, suits, values):
    """
    get a hand contains a flush
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    hand = []
    res = ''
    for suit in set(suits):
        if suits.count(suit) >= 5:
            res = suit
            break
    for s, v in zip(suits, values):
        if s == res:
            hand.append(v)

    return sorted(hand, key=lambda x: -x)[:5]


def get_full_house(total_hand, suits, values):
    hand = []
    pair, three = list(), list()
    for num in sorted(set(values), key=lambda x: -x):
        if values.count(num) == 2:
            pair.append(num)
        elif values.count(num) >= 3:
            three.append(num)
    three.sort(key=lambda x: -x)
    pair.sort(key=lambda x: -x)
    t = p = 0
    while len(hand) < 5:
        if three and pair:
            hand += [three[0]] * 3 + [pair[p]] * 2
        elif three:
            hand += [three[t]] * 3
            t += 1
        elif pair:
            hand += [pair[p]] * 2
            p += 1

    return hand[:5]


# def get_full_house(total_hand, suits, values):
#     """
#     get a hand contain a full house
#     :param total_hand:
#     :param suits:
#     :param values:
#     :return:
#     """
#     hand = []
#     pair, three = list(), list()
#
#     for num in sorted(set(values), key=lambda x: -x):
#         if values.count(num) == 2:
#             pair.append(num)
#         elif values.count(num) >= 3:
#             three.append(num)
#
#     three.sort(key=lambda x: -x)
#     pair.sort(key=lambda x: -x)
#     t, p = 0, 0
#     while len(hand) < 5 and t < len(three) and p < len(pair):
#         if three[t] > pair[p]:
#             hand += [three[t]] * 3
#             t += 1
#         else:
#             hand += [pair[p]] * 2
#             p += 1
#     if len(hand) < 5:
#         if t < len(three) and p < len(pair):
#             cnt = 2 if pair[p] > three[t] else 3
#             num = pair[p] if cnt == 2 else three[t]
#             hand += [num] * cnt
#         elif t < len(three):
#             hand += [three[t]] * 3
#         elif p < len(pair):
#             hand += [pair[p]] * 2
#
#     return hand


def get_four_of_a_kind(total_hand, suits, values):
    """
    get a hand contains four of a kind
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    hand = []
    for num in sorted(set(values), key=lambda x: -x):
        cnt = values.count(num)
        if cnt >= 4:
            hand += [num] * cnt

    values.sort(key=lambda x: -x)
    if len(hand) < 5:
        for num in values:
            if num in hand:
                continue
            hand.append(num)
            if len(hand) == 5:
                break

    return hand


def get_straight_flush(total_hand, suits, values):
    """
    since we have check it is flush and straight previously, at this time we just need to get those straight number
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    return get_straight(total_hand, suits, values)


def get_royal_flush(total_hand, suits, values):
    """
    since we have check it is royal flush previously, just need to get it's number
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    return get_straight(total_hand, suits, values)

