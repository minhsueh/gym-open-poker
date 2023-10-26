
def decision_on_out(out_dict):
    """
    Args:
        out_dict(dict): the output from agent_helper_funciton.get_out_probability

    Returns:
        one of the funcion: [call, bet/raise_bet, fold]
    """
    hand_type_utility = {
        'royal_flush': 10,
        'straight_flush': 9,
        'four_of_a_kind': 8,
        'full_house': 7,
        'flush': 6,
        'straight': 5,
        'three_of_a_kind': 4,
        'two_pairs': 3,
        'one_pair': 2,
        'high_card': 1
    }


def calculate_utitliy_for_given_hand_type(hand_type, number):
    """ 
    Hand utility:
        formula = U(number) * U(hand_type) + offset, 
        where U(number)is bounded between 2(2)~14(A) and U(hand_type) is bounded between 1 (high_card)~ 10 (royal_flush)
        
        constraint:
            U(HT^{+1}_2) = U(HT_14) + offset. 
            the utility of lowest number of higher hand_type > the utility of highest number of lower hand_type
            For exapmle, U(three 2s) >  U(ace pair)

            With such constraint, we can have offset = [
                0,
                -107,
                -202,
                -285,
                -356,
                -415,
                -462,
                -497,
                -520,
                -531] from royal_flush to high_card, respectively.

        The lower and higher bound of U. Just mathematical calculation
        min(U) = 2 * 1 - 531 = -533 (2 as a high card ,this is impossible combination if we consider five cards) 
        max(U) = 14 * 10 = 140 (royal_flush) 

    Args:
        hand_type(str)
        number(float/int): bounded between 1~13. float only if hand_type == 'two_pair'

    Returns:

    """
    if hand_type != 'two_pair':
        # we will get the average of two_pair number
        assert number in range(1, 14)

    offset_dic = {
        'royal_flush': 0,
        'straight_flush': -107,
        'four_of_a_kind': -202,
        'full_house': -285,
        'flush': -356,
        'straight': -415,
        'three_of_a_kind': -462,
        'two_pairs': -497,
        'one_pair': -520,
        'high_card': -531
    }

    # number_utility
    number_utility = {i: i for i in range(2, 14)}
    number_utility[1] = 14
    if number not in number_utility:
        number_utility[number] = number


    # hand_type_utility
    hand_type_utility = {
        'royal_flush': 10,
        'straight_flush': 9,
        'four_of_a_kind': 8,
        'full_house': 7,
        'flush': 6,
        'straight': 5,
        'three_of_a_kind': 4,
        'two_pairs': 3,
        'one_pair': 2,
        'high_card': 1
    }

    U_total =  hand_type_utility[hand_type] * number_utility[number] + offset_dic[hand_type]
    U_max = 140
    U_min = -533

    return(format_float_precision((U_total-U_min)/(U_max-U_min)))



def get_out_utility(current_gameboard, total_hand):
    """ 
    The logic is similar to agent_helper_function.get_out_probability
    Instead of getting probability, we get utility in this function

    Args:
        current_gameboard
        total_hand


    Returns:
        (dictionary): 
    """
    deck = current_gameboard['deck']
    hand_rank_funcs = current_gameboard['hand_rank_funcs']

    out_utility = dict()

    for check_function, get_function, hand_name in hand_rank_funcs:
        total_utility = 0
        total_left_card = 0

        for out_card in deck:
            if not is_out_in_hand(out_card, total_hand):
                total_left_card += 1
                next_total_hand = total_hand + [out_card]
                if check_function(next_total_hand):   
                    hadn_card_num = get_function(next_total_hand)
                    if hand_name == 'two_pairs':
                        number = (hadn_card_num[0] + hadn_card_num[2])/2
                    else:
                        number = hadn_card_num[0]
                    total_utility += calculate_utitliy_for_given_hand_type(hand_name, number)

        out_utility[hand_name] = format_float_precision(total_utility/total_left_card)
    return(format_float_precision(np.mean(list(out_utility.values()))))


