from open_poker.envs.poker_util.agent_helper_function import *
import unittest
from open_poker.envs.poker_util.card import Card
from open_poker.envs.poker_util.initialize_game_elements import initialize_game_element
from open_poker.envs.poker_util.agents import dump_agent
from open_poker.envs.poker_util.agent import Agent

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

class TestProb(unittest.TestCase):
    def test_get_out_probability(self):
        player_list = [dump_agent]
        player_decision_agents = dict()
        player_decision_agents['player_1'] = 'player_1'
        for player_idx, player in enumerate(player_list):
            player_decision_agents['player_' + str(player_idx+2)] = Agent(**player.decision_agent_methods)
        current_gameboard = initialize_game_element(player_decision_agents, 5)

        # 5 card, three of a kind
        total_hand = [Card('club', 1), Card('diamond', 1), Card('heart', 1), Card('club', 4), Card('club', 5)]
        self.assertEqual(get_out_probability(current_gameboard, total_hand), format_float_precision(7/47), "")
        
        # 5 card, four of a kind
        total_hand = [Card('club', 1), Card('diamond', 1), Card('heart', 1), Card('spade', 1), Card('club', 5)]
        self.assertEqual(get_out_probability(current_gameboard, total_hand), format_float_precision(0), "")
        
        # 6 card, two three of a kind
        total_hand = [Card('club', 1), Card('diamond', 1), Card('heart', 1), Card('spade', 5), Card('club', 5), Card('heart', 5)]
        self.assertEqual(get_out_probability(current_gameboard, total_hand), format_float_precision(2/46), "")

        # 5 card, royal flush except 1 card
        total_hand = [Card('spade', 1), Card('spade', 13), Card('spade', 12), Card('spade', 11), Card('club', 5)]
        self.assertEqual(get_out_probability(current_gameboard, total_hand), format_float_precision(26/47), "")

        # 5 card, royal flush except 1 card
        total_hand = [Card('spade', 1), Card('spade', 13), Card('spade', 12), Card('spade', 11), Card('club', 5)]
        self.assertEqual(get_out_probability(current_gameboard, total_hand, 'three_of_a_kind'), format_float_precision(12/47), "")
        
        print(get_out_probability(current_gameboard, total_hand))

"""
class TestProb(unittest.TestCase):
    def test_get_probability_four_of_a_kind(self):

        # 5 singles
        total_hand = [Card('club', 1), Card('club', 2), Card('club', 3), Card('club', 4), Card('club', 5)]
        self.assertEqual(get_probability_four_of_a_kind(total_hand), format_float_precision(0), "")
        # 5 card, two pairs
        total_hand = [Caard('club', 1), Card('diamond', 1), Card('club', 2), Card('diamond', 2), Card('club', 6)]
        self.assertEqual(get_probability_four_of_a_kind(total_hand), format_float_precision(2/47/46), "")
        # 5 card, one pair
        total_hand = [Card('club', 9), Card('diamond', 3), Card('club', 2), Card('diamond', 2), Card('club', 4)]
        hand_value = [9, 2, 2, 3, 4]
        self.assertEqual(get_probability_four_of_a_kind(total_hand), format_float_precision(1/47/46), "")
        # 5 card, three of a kind
        hand_value = [2, 2, 2, 3, 4]
        self.assertEqual(get_probability_four_of_a_kind(total_hand), format_float_precision(1/47), "")  
        # 5 card, four of a kind
        hand_value = [2, 2, 2, 2, 4]
        self.assertEqual(get_probability_four_of_a_kind(total_hand), format_float_precision(1), "")    
        # 6 card, three pair
        hand_value = [9, 9, 2, 2, 12, 12]
        self.assertEqual(get_probability_four_of_a_kind(total_hand), format_float_precision(0), "")   
        # 6 card, three of a kind
        hand_value = [9, 9, 9, 2, 12, 12]
        self.assertEqual(get_probability_four_of_a_kind(total_hand), format_float_precision(1/46), "") 
        # 7 card, four of a kind
        hand_value = [9, 9, 9, 9, 12, 12, 1]
        self.assertEqual(get_probability_four_of_a_kind(total_hand), format_float_precision(1), "")    
        # 7 card, nothing
        hand_value = [9, 9, 9, 8, 12, 12, 1]
        self.assertEqual(get_probability_four_of_a_kind(total_hand), format_float_precision(0), "") 
 
"""

"""
class TestIs(unittest.TestCase):
    def test_is_one_pair(self):
        hand_value = [1, 13, 12, 11, 10, 9, 8]
        suits = []
        total_hand = []
        self.assertEqual(is_one_pair(total_hand), False, "1")
        hand_value = [1, 3, 2, 7, 12, 9, 8]
        self.assertEqual(is_one_pair(total_hand), False, "2")
        hand_value = [1, 1, 9, 2, 7, 6, 3]
        self.assertEqual(is_one_pair(total_hand), True, "3")
        hand_value = [1, 9, 9, 2, 7, 6, 3]
        self.assertEqual(is_one_pair(total_hand), True, "4")
        hand_value = [2, 9, 8, 2, 7, 6, 3]
        self.assertEqual(is_one_pair(total_hand), True, "5")
        hand_value = [2, 9, 8, 1, 7, 6, 3]
        self.assertEqual(is_one_pair(total_hand), False, "6")

    def test_is_two_pair(self):
        hand_value = [1, 1, 11, 11, 10, 10, 8]
        suits = []
        total_hand = []
        self.assertEqual(is_two_pair(total_hand), True, "3 pairs")
        hand_value = [1, 1, 11, 11, 10, 9, 8]
        self.assertEqual(is_two_pair(total_hand), True, "2 pairs")
        hand_value = [1, 1, 9, 2, 7, 6, 3]
        self.assertEqual(is_two_pair(total_hand), False, "1 pairs")
        hand_value = [1, 9, 8, 2, 7, 6, 3]
        self.assertEqual(is_two_pair(total_hand), False, "0 pairs")

    def test_is_three_of_a_kind(self):
        hand_value = [1, 1, 1, 11, 10, 10, 8]
        suits = []
        total_hand = []
        self.assertEqual(is_three_of_a_kind(total_hand), True, "1 three")
        hand_value = [1, 1, 1, 9, 9, 9, 8]
        self.assertEqual(is_three_of_a_kind(total_hand), True, "2 threes")
        hand_value = [1, 1, 11, 11, 10, 10, 8]
        self.assertEqual(is_three_of_a_kind(total_hand), False, "3 pairs")

    def test_is_straight(self):
        suits = []
        total_hand = []
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        self.assertEqual(is_straight(total_hand), True, "A to 10")
        hand_value = [1, 5, 1, 2, 10, 3, 4]
        self.assertEqual(is_straight(total_hand), True, "1 to 5")
        hand_value = [7, 6, 11, 9, 10, 10, 8]
        self.assertEqual(is_straight(total_hand), True, "6 to 10")
        hand_value = [7, 1, 11, 4, 10, 10, 8]
        self.assertEqual(is_straight(total_hand), False, "No straight")

    def test_is_flush(self):
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = []
        total_hand = []
        suits = ['diamond'] * len(hand_value) 
        self.assertEqual(is_flush(total_hand), True, "diamond flush")
        hand_value = [1, 5, 1, 2, 10, 3, 4]
        suits = ['diamond'] * 4 + ['club'] * 3
        self.assertEqual(is_flush(total_hand), False, "4 diamonds")

    def test_is_full_house(self):
        suits = []
        total_hand = []
        # 2 threes
        hand_value = [9, 6, 9, 9, 6, 6, 8]
        self.assertEqual(is_full_house(total_hand), True, "2 threes")
        # 1 three and 2 pairs
        hand_value = [2, 6, 2, 2, 6, 1, 1]
        self.assertEqual(is_full_house(total_hand), True, "1 three and 2 pairs")       
        # 1 three and 1 pair
        hand_value = [2, 6, 2, 2, 6, 8, 7]
        self.assertEqual(is_full_house(total_hand), True, "1 three and 1 pair")   
        # 3 pair
        hand_value = [2, 6, 2, 3, 6, 3, 7]
        self.assertEqual(is_full_house(total_hand), False, "3 pairs")  
        # 7 single
        hand_value = [2, 6, 3, 8, 13, 1, 7]
        self.assertEqual(is_full_house(total_hand), False, "7 single")  

    def test_is_four_of_a_kind(self):
        hand_value = [1, 1, 1, 11, 10, 1, 12]
        suits = []
        total_hand = []
        self.assertEqual(is_four_of_a_kind(total_hand), True, "1 fours")
        hand_value = [9, 6, 9, 9, 6, 6, 8]
        self.assertEqual(is_four_of_a_kind(total_hand), False, "2 threes")
        hand_value = [2, 6, 2, 3, 6, 3, 7]
        self.assertEqual(is_four_of_a_kind(total_hand), False, "3 pairs")

    def test_is_straight_flush(self):
        total_hand = []
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['diamond'] * 7
        self.assertEqual(is_straight_flush(total_hand), True, "A to 10")
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['heart', 'diamond', 'club', 'diamond', 'heart', 'diamond', 'diamond']
        self.assertEqual(is_straight_flush(total_hand), False, "A to 10 but suit not match")
        hand_value = [1, 5, 1, 2, 10, 3, 4]
        suits = ['heart', 'diamond', 'club', 'diamond', 'heart', 'diamond', 'diamond']
        self.assertEqual(is_straight_flush(total_hand), False, "1 to 5 but suit not match")
        hand_value = [7, 6, 11, 9, 10, 1, 8]
        suits = ['diamond'] * 7
        self.assertEqual(is_straight(total_hand), True, "6 to 10")
        hand_value = [7, 1, 11, 4, 10, 10, 8]
        suits = ['diamond'] * 7
        self.assertEqual(is_straight_flush(total_hand), False, "No straight") 

    def test_is_royal_flush(self):
        total_hand = []
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['diamond'] * 7
        self.assertEqual(is_royal_flush(total_hand), True, "diamond A to 10")
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['club'] * 7
        self.assertEqual(is_royal_flush(total_hand), True, "club A to 10")
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['heart', 'diamond', 'club', 'diamond', 'heart', 'diamond', 'diamond']
        self.assertEqual(is_royal_flush(total_hand), False, "A to 10 but suit not match")
        hand_value = [1, 5, 1, 2, 10, 3, 4]
        suits = ['heart', 'diamond', 'club', 'diamond', 'heart', 'diamond', 'diamond']
        self.assertEqual(is_royal_flush(total_hand), False, "1 to 5 but suit not match")
        hand_value = [7, 6, 11, 9, 10, 1, 8]
        suits = ['diamond'] * 7
        self.assertEqual(is_royal_flush(total_hand), False, "6 to 10")
        hand_value = [7, 1, 11, 4, 10, 10, 8]
        suits = ['diamond'] * 7
        self.assertEqual(is_royal_flush(total_hand), False, "No straight") 

class TestGet(unittest.TestCase):
    def test_get_high_card(self):
        hand_value = [1, 13, 12, 11, 10, 9, 8]
        suits = []
        total_hand = []
        self.assertEqual(get_high_card(total_hand), [1, 13, 12, 11, 10], "")
        hand_value = [1, 3, 2, 7, 12, 9, 8]
        self.assertEqual(get_high_card(total_hand), [1, 12, 9, 8, 7], "")
        hand_value = [10, 3, 2, 7, 12, 9, 8]
        self.assertEqual(get_high_card(total_hand), [12, 10, 9, 8, 7], "")
    
    def test_get_one_pair(self):
        hand_value1 = [1, 1, 9, 2, 7, 6, 3]
        hand_value2 = [1, 9, 9, 2, 7, 6, 3]
        hand_value3 = [2, 9, 8, 2, 7, 6, 3]
        suits = []
        total_hand = []
        self.assertEqual(get_one_pair(total_hand, suits, hand_value1), [1, 1, 9, 7, 6], "")
        self.assertEqual(get_one_pair(total_hand, suits, hand_value2), [9, 9, 1, 7, 6], "")
        self.assertEqual(get_one_pair(total_hand, suits, hand_value3), [2, 2, 9, 8, 7], "")

    def test_get_two_pair(self):
        
        suits = []
        total_hand = []
        # three pair
        hand_value = [1, 1, 3, 2, 7, 7, 3]
        self.assertEqual(get_two_pair(total_hand), [1, 1, 7, 7, 3], "")
        # Ace pair
        hand_value = [1, 1, 2, 2, 7, 6, 3]
        self.assertEqual(get_two_pair(total_hand), [1, 1, 2, 2, 7], "")
        # single Ace
        hand_value = [1, 9, 9, 2, 3, 6, 3]
        self.assertEqual(get_two_pair(total_hand), [9, 9, 3, 3, 1], "")

    def test_get_three_of_a_kind(self):
        
        suits = []
        total_hand = []
        # three of Ace
        hand_value = [1, 1, 1, 8, 7, 6, 9]
        self.assertEqual(get_three_of_a_kind(total_hand), [1, 1, 1, 9, 8], "")
        # single Ace
        hand_value = [1, 5, 2, 8, 8, 6, 8]
        self.assertEqual(get_three_of_a_kind(total_hand), [8, 8, 8, 1, 6], "")
    
    def test_get_straight(self):
        
        suits = []
        total_hand = []
        # A 13 12 11 10
        hand_value = [1, 13, 12, 11, 10, 9, 8]
        self.assertEqual(get_straight(total_hand), [1, 13, 12, 11, 10], "")
        # 5 4 3 2 A
        hand_value = [2, 1, 3, 8, 10, 4, 5]
        ans = get_straight(total_hand)
        self.assertEqual(ans, [5, 4, 3, 2, 1], "")
        # 6 5 4 3 2 
        hand_value = [2, 1, 3, 8, 6, 4, 5]
        ans = get_straight(total_hand)
        self.assertEqual(ans, [6, 5, 4, 3, 2], "")
        hand_value = [2, 11, 12, 8, 10, 9, 7]
        self.assertEqual(get_straight(total_hand), [12, 11, 10, 9, 8], "")
    
    def test_get_flush(self):
        total_hand = []

        # 
        hand_value = [9, 6, 1, 8, 7, 2, 13]
        suits = ['diamond'] * len(hand_value)
        self.assertEqual(get_flush(total_hand), [1, 13, 9, 8, 7], "") 

        hand_value = [9, 6, 3, 8, 7, 2, 13]
        suits = ['club'] * len(hand_value)
        self.assertEqual(get_flush(total_hand), [13, 9, 8, 7, 6], "") 

        hand_value = [9, 6, 3, 8, 7, 2, 13]
        suits = ['club'] * 5 + ['diamond'] * 2
        self.assertEqual(get_flush(total_hand), [9, 8, 7, 6, 3], "") 
    

    
    def test_get_full_house(self):

        suits = []
        total_hand = []
        # 2 threes
        hand_value = [9, 6, 9, 9, 6, 6, 8]
        self.assertEqual(get_full_house(total_hand), [9, 9, 9, 6, 6], "")
        # 2 threes
        hand_value = [1, 6, 1, 1, 6, 6, 8]
        self.assertEqual(get_full_house(total_hand), [1, 1, 1, 6, 6], "")
        # 1 three and 2 pairs
        hand_value = [9, 6, 9, 9, 6, 1, 1]
        self.assertEqual(get_full_house(total_hand), [9, 9, 9, 1, 1], "")    
        # 1 three and 2 pairs
        hand_value = [2, 6, 2, 2, 6, 1, 1]
        self.assertEqual(get_full_house(total_hand), [2, 2, 2, 1, 1], "")       
        # 1 three and 1 pair
        hand_value = [2, 6, 2, 2, 6, 8, 7]
        self.assertEqual(get_full_house(total_hand), [2, 2, 2, 6, 6], "")   
        # 1 three and 1 pair
        hand_value = [2, 6, 2, 2, 6, 1, 7]
        self.assertEqual(get_full_house(total_hand), [2, 2, 2, 6, 6], "")  

    def test_get_four_of_a_kind(self):

        suits = []
        total_hand = []
        # single A
        hand_value = [1, 6, 6, 6, 6, 7, 8]
        self.assertEqual(get_four_of_a_kind(total_hand), [6, 6, 6, 6, 1], "")
        # 4 As
        hand_value = [1, 1, 1, 1, 6, 6, 13]
        self.assertEqual(get_four_of_a_kind(total_hand), [1, 1, 1, 1, 13], "")
        # 
        hand_value = [9, 2, 2, 2, 2, 1, 1]
        self.assertEqual(get_four_of_a_kind(total_hand), [2, 2, 2, 2, 1], "")    
        # 1 three and 2 pairs
        hand_value = [9, 2, 2, 2, 2, 12, 13]
        self.assertEqual(get_four_of_a_kind(total_hand), [2, 2, 2, 2, 13], "")       
"""


    
    

if __name__ == '__main__':
    unittest.main()