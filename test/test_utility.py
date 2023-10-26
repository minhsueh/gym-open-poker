import matplotlib.pyplot as plt


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


hand = []
utility_list = []
for ht in hand_type_utility.keys():
    for num in [1] + list(range(13, 1, -1)):
        hand.append(ht + '_' + str(num))
        utility_list.append(calculate_utitliy_for_given_hand_type(ht, num))
plt.figure(figsize=(15,8))
plt.scatter(hand, utility_list)
plt.xticks(rotation=90)
plt.grid()
plt.tight_layout()
plt.savefig('test.png')

print(len(utility_list))

print(max(utility_list))
print(min(utility_list))
print(len(set(utility_list)))




