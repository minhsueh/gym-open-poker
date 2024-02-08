import copy
import collections
from card_utility_actions import *
from dealer import compare_two_hands


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
    current_rank_type, current_best_hand = get_best_hand(current_gameboard, total_hand)
    want_type = current_rank_type

    if desired_hand and hand_rank_type[desired_hand] > hand_rank_type[current_rank_type]:
        want_type = desired_hand


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
                if hand_rank_type[hand_name] < hand_rank_type[want_type]:
                    break

                if hand_name == current_rank_type:
                    next_rank_type, next_best_hand = get_best_hand(current_gameboard, next_total_hand)
                    
                    if compare_two_hands(current_gameboard, current_best_hand, next_best_hand) == -1:
                        found_better = True
                    break
                    
                if check_function(next_total_hand):
                    found_better = True
                    break
            if found_better:
                count_hand += 1
    out_probability = format_float_precision(count_hand/total_left_card)
    return(out_probability)






