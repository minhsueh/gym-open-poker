import copy
import collections
from card_utility_actions import *


def format_float_precision(val, significant_digit = 5):
    """ 
    Args:
        val(int|float)
        significant_digit

    Returns:
        float
    """

    if round(float(val), significant_digit) < 0:
        return(round(0, significant_digit))
    elif round(float(val), significant_digit) > 1:
        return(round(1, significant_digit))
    else:
        return(round(float(val), significant_digit))

def is_out_in_hand(out_card, total_hand):
    """ 
    Args:
        out_card(Card)
        total_hand(list[Card])

    Returns:
        (bool)
    """

    for hand_card in total_hand:
        if hand_card.suit == out_card.suit and hand_card.number == out_card.number:
            return(True)
    return(False)


def get_out_probability(current_gameboard, total_hand, desired_hand = None):
    """ 
    calculate the probability of out card which is giving better hand

    current_gameboard['deck'] 
    current_gameboard['hand_rank_funcs'] is the list where each element contains function is_hand_type, function get_hand_type, hand_type_name(str)

    process:
    out_probability = dict() # key: hand_type(str), value: (float) probability to get specific hand after next card 
    
    count_hand = 0
    total_left_card = 0
    iterate out_card in whole deck:
        if out_card not in total_hand:
            total_left_card += 1

            iterate hand_type in current_gameboard['hand_rank_funcs']:
                if (total_hand + out_card) is hand_type:
                    count_hand += 1
        out_probability[hand_type] = round(count_hand/total_left_card, 2)


    Args:
        current_gameboard
        total_hand


    Returns:
        out_probability (float)
    """
    deck = current_gameboard['deck']
    hand_rank_funcs = current_gameboard['hand_rank_funcs']
    hand_rank_type = current_gameboard['hand_rank_type']

    # calculate current best hand
    current_rank_type, _ = get_best_hand(current_gameboard, total_hand)

    if desired_hand and hand_rank_type[desired_hand] > hand_rank_type[current_rank_type]:
        current_rank_type = desired_hand


    # get out_probability
    out_probability = dict()

    count_hand = 0
    total_left_card = 0


    for out_card in deck:
        if not is_out_in_hand(out_card, total_hand):
            total_left_card += 1
            next_total_hand = total_hand + [out_card]
            found_better = False
            for check_function, get_function, hand_name in hand_rank_funcs:
                if hand_name == current_rank_type:
                    break
                if check_function(next_total_hand):
                    found_better = True
                    break
            if found_better:
                count_hand += 1
    out_probability = format_float_precision(count_hand/total_left_card)
    return(out_probability)



def get_probability_royal_flush():
    pass

def get_probability_straight_flush():
    pass

def get_probability_four_of_a_kind(total_hand, suits, values):
    """ 
    Just consider player's hole card and community card

    Args:
        current_gameboard

    Returns:

    """
    # assert len(suits) == len(values)
    hand_count = len(values) # flop: count_dif = 5, turn: count_dif = 6, river:count_dif = 7
    other_card_count = 52 - hand_count # we don't consider other players' hand becasue we don't have any info
    assert 5 <= hand_count <=7
    value_counter = collections.Counter(values)
    max_count = max(value_counter.values())
    if max_count == 1:
        # early stop
        return(format_float_precision(0))

    if hand_count == 5:
        # flop
        if max_count == 2:
            # have pair
            if len(value_counter) == 3:
                # two pairs
                return(format_float_precision(2/other_card_count/(other_card_count-1)))
            elif len(value_counter) == 4:
                # one pair
                return(format_float_precision(1/other_card_count/(other_card_count-1)))

        elif max_count == 3:
            # have three of a kind
            return(format_float_precision(1/other_card_count))

        elif max_count == 4:
            return(format_float_precision(1))

        else:
            raise


    elif hand_count == 6:
        # turn
        if max_count == 2:
            # have pair
            return(format_float_precision(0))

        elif max_count == 3:
            # have three of a kind
            return(format_float_precision(1/other_card_count))

        elif max_count == 4:
            return(format_float_precision(1))

        else:
            raise
    elif hand_count == 7:
        # river
        if max_count == 4:
            return(format_float_precision(1))
        else:
            return(format_float_precision(0))
    else:
        raise





def get_probability_full_house():
    hand_count = len(values) # flop: count_dif = 5, turn: count_dif = 6, river:count_dif = 7
    other_card_count = 52 - hand_count # we don't consider other players' hand becasue we don't have any info
    assert 5 <= hand_count <=7
    value_counter = collections.Counter(values)
    max_count = max(value_counter.values())
    if max_count == 1:
        # early stop
        return(format_float_precision(0))

    if hand_count == 5:
        # flop
        if max_count == 2:
            # have pair
            if len(value_counter) == 3:
                # two pairs
                return(format_float_precision(2/other_card_count/(other_card_count-1)))
            elif len(value_counter) == 4:
                # one pair
                return(format_float_precision(1/other_card_count/(other_card_count-1)))

        elif max_count == 3:
            # have three of a kind
            return(format_float_precision(1/other_card_count))

        elif max_count == 4:
            return(format_float_precision(1))

        else:
            raise


    elif hand_count == 6:
        # turn
        if max_count == 2:
            # have pair
            return(format_float_precision(0))

        elif max_count == 3:
            # have three of a kind
            return(format_float_precision(1/other_card_count))

        elif max_count == 4:
            return(format_float_precision(1))

        else:
            raise
    elif hand_count == 7:
        # river
        if max_count == 4:
            return(format_float_precision(1))
        else:
            return(format_float_precision(0))
    else:
        raise

def get_probability_flush():
    pass

def get_probability_straight():
    pass

def get_probability_three_of_a_kind():
    pass

def get_probability_two_pair():
    pass

def get_probability_one_pair():
    pass




