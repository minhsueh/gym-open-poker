from open_poker.envs.poker_util.card_utility_actions import *
import unittest



class TestIs(unittest.TestCase):
    def test_is_one_pair(self):
        hand_value = [1, 13, 12, 11, 10, 9, 8]
        suits = []
        total_hand = []
        self.assertEqual(is_one_pair(total_hand, suits, hand_value), False, "1")
        hand_value = [1, 3, 2, 7, 12, 9, 8]
        self.assertEqual(is_one_pair(total_hand, suits, hand_value), False, "2")
        hand_value = [1, 1, 9, 2, 7, 6, 3]
        self.assertEqual(is_one_pair(total_hand, suits, hand_value), True, "3")
        hand_value = [1, 9, 9, 2, 7, 6, 3]
        self.assertEqual(is_one_pair(total_hand, suits, hand_value), True, "4")
        hand_value = [2, 9, 8, 2, 7, 6, 3]
        self.assertEqual(is_one_pair(total_hand, suits, hand_value), True, "5")
        hand_value = [2, 9, 8, 1, 7, 6, 3]
        self.assertEqual(is_one_pair(total_hand, suits, hand_value), False, "6")

    def test_is_two_pair(self):
        hand_value = [1, 1, 11, 11, 10, 10, 8]
        suits = []
        total_hand = []
        self.assertEqual(is_two_pair(total_hand, suits, hand_value), True, "3 pairs")
        hand_value = [1, 1, 11, 11, 10, 9, 8]
        self.assertEqual(is_two_pair(total_hand, suits, hand_value), True, "2 pairs")
        hand_value = [1, 1, 9, 2, 7, 6, 3]
        self.assertEqual(is_two_pair(total_hand, suits, hand_value), False, "1 pairs")
        hand_value = [1, 9, 8, 2, 7, 6, 3]
        self.assertEqual(is_two_pair(total_hand, suits, hand_value), False, "0 pairs")

    def test_is_three_of_a_kind(self):
        hand_value = [1, 1, 1, 11, 10, 10, 8]
        suits = []
        total_hand = []
        self.assertEqual(is_three_of_a_kind(total_hand, suits, hand_value), True, "1 three")
        hand_value = [1, 1, 1, 9, 9, 9, 8]
        self.assertEqual(is_three_of_a_kind(total_hand, suits, hand_value), True, "2 threes")
        hand_value = [1, 1, 11, 11, 10, 10, 8]
        self.assertEqual(is_three_of_a_kind(total_hand, suits, hand_value), False, "3 pairs")

    def test_is_straight(self):
        suits = []
        total_hand = []
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        self.assertEqual(is_straight(total_hand, suits, hand_value), True, "A to 10")
        hand_value = [1, 5, 1, 2, 10, 3, 4]
        self.assertEqual(is_straight(total_hand, suits, hand_value), True, "1 to 5")
        hand_value = [7, 6, 11, 9, 10, 10, 8]
        self.assertEqual(is_straight(total_hand, suits, hand_value), True, "6 to 10")
        hand_value = [7, 1, 11, 4, 10, 10, 8]
        self.assertEqual(is_straight(total_hand, suits, hand_value), False, "No straight")

    def test_is_flush(self):
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = []
        total_hand = []
        suits = ['diamond'] * len(hand_value) 
        self.assertEqual(is_flush(total_hand, suits, hand_value), True, "diamond flush")
        hand_value = [1, 5, 1, 2, 10, 3, 4]
        suits = ['diamond'] * 4 + ['club'] * 3
        self.assertEqual(is_flush(total_hand, suits, hand_value), False, "4 diamonds")

    def test_is_full_house(self):
        suits = []
        total_hand = []
        # 2 threes
        hand_value = [9, 6, 9, 9, 6, 6, 8]
        self.assertEqual(is_full_house(total_hand, suits, hand_value), True, "2 threes")
        # 1 three and 2 pairs
        hand_value = [2, 6, 2, 2, 6, 1, 1]
        self.assertEqual(is_full_house(total_hand, suits, hand_value), True, "1 three and 2 pairs")       
        # 1 three and 1 pair
        hand_value = [2, 6, 2, 2, 6, 8, 7]
        self.assertEqual(is_full_house(total_hand, suits, hand_value), True, "1 three and 1 pair")   
        # 3 pair
        hand_value = [2, 6, 2, 3, 6, 3, 7]
        self.assertEqual(is_full_house(total_hand, suits, hand_value), False, "3 pairs")  
        # 7 single
        hand_value = [2, 6, 3, 8, 13, 1, 7]
        self.assertEqual(is_full_house(total_hand, suits, hand_value), False, "7 single")  

    def test_is_four_of_a_kind(self):
        hand_value = [1, 1, 1, 11, 10, 1, 12]
        suits = []
        total_hand = []
        self.assertEqual(is_four_of_a_kind(total_hand, suits, hand_value), True, "1 fours")
        hand_value = [9, 6, 9, 9, 6, 6, 8]
        self.assertEqual(is_four_of_a_kind(total_hand, suits, hand_value), False, "2 threes")
        hand_value = [2, 6, 2, 3, 6, 3, 7]
        self.assertEqual(is_four_of_a_kind(total_hand, suits, hand_value), False, "3 pairs")

    def test_is_straight_flush(self):
        total_hand = []
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['diamond'] * 7
        self.assertEqual(is_straight_flush(total_hand, suits, hand_value), True, "A to 10")
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['heart', 'diamond', 'club', 'diamond', 'heart', 'diamond', 'diamond']
        self.assertEqual(is_straight_flush(total_hand, suits, hand_value), False, "A to 10 but suit not match")
        hand_value = [1, 5, 1, 2, 10, 3, 4]
        suits = ['heart', 'diamond', 'club', 'diamond', 'heart', 'diamond', 'diamond']
        self.assertEqual(is_straight_flush(total_hand, suits, hand_value), False, "1 to 5 but suit not match")
        hand_value = [7, 6, 11, 9, 10, 1, 8]
        suits = ['diamond'] * 7
        self.assertEqual(is_straight(total_hand, suits, hand_value), True, "6 to 10")
        hand_value = [7, 1, 11, 4, 10, 10, 8]
        suits = ['diamond'] * 7
        self.assertEqual(is_straight_flush(total_hand, suits, hand_value), False, "No straight") 

    def test_is_royal_flush(self):
        total_hand = []
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['diamond'] * 7
        self.assertEqual(is_royal_flush(total_hand, suits, hand_value), True, "diamond A to 10")
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['club'] * 7
        self.assertEqual(is_royal_flush(total_hand, suits, hand_value), True, "club A to 10")
        hand_value = [1, 10, 1, 11, 10, 13, 12]
        suits = ['heart', 'diamond', 'club', 'diamond', 'heart', 'diamond', 'diamond']
        self.assertEqual(is_royal_flush(total_hand, suits, hand_value), False, "A to 10 but suit not match")
        hand_value = [1, 5, 1, 2, 10, 3, 4]
        suits = ['heart', 'diamond', 'club', 'diamond', 'heart', 'diamond', 'diamond']
        self.assertEqual(is_royal_flush(total_hand, suits, hand_value), False, "1 to 5 but suit not match")
        hand_value = [7, 6, 11, 9, 10, 1, 8]
        suits = ['diamond'] * 7
        self.assertEqual(is_royal_flush(total_hand, suits, hand_value), False, "6 to 10")
        hand_value = [7, 1, 11, 4, 10, 10, 8]
        suits = ['diamond'] * 7
        self.assertEqual(is_royal_flush(total_hand, suits, hand_value), False, "No straight") 

class TestGet(unittest.TestCase):
    def test_get_high_card(self):
        hand_value = [1, 13, 12, 11, 10, 9, 8]
        suits = []
        total_hand = []
        self.assertEqual(get_high_card(total_hand, suits, hand_value), [1, 13, 12, 11, 10], "")
        hand_value = [1, 3, 2, 7, 12, 9, 8]
        self.assertEqual(get_high_card(total_hand, suits, hand_value), [1, 12, 9, 8, 7], "")
        hand_value = [10, 3, 2, 7, 12, 9, 8]
        self.assertEqual(get_high_card(total_hand, suits, hand_value), [12, 10, 9, 8, 7], "")
    
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
        self.assertEqual(get_two_pair(total_hand, suits, hand_value), [1, 1, 7, 7, 3], "")
        # Ace pair
        hand_value = [1, 1, 2, 2, 7, 6, 3]
        self.assertEqual(get_two_pair(total_hand, suits, hand_value), [1, 1, 2, 2, 7], "")
        # single Ace
        hand_value = [1, 9, 9, 2, 3, 6, 3]
        self.assertEqual(get_two_pair(total_hand, suits, hand_value), [9, 9, 3, 3, 1], "")

    def test_get_three_of_a_kind(self):
        
        suits = []
        total_hand = []
        # three of Ace
        hand_value = [1, 1, 1, 8, 7, 6, 9]
        self.assertEqual(get_three_of_a_kind(total_hand, suits, hand_value), [1, 1, 1, 9, 8], "")
        # single Ace
        hand_value = [1, 5, 2, 8, 8, 6, 8]
        self.assertEqual(get_three_of_a_kind(total_hand, suits, hand_value), [8, 8, 8, 1, 6], "")
    
    def test_get_straight(self):
        
        suits = []
        total_hand = []
        # A 13 12 11 10
        hand_value = [1, 13, 12, 11, 10, 9, 8]
        self.assertEqual(get_straight(total_hand, suits, hand_value), [1, 13, 12, 11, 10], "")
        # 5 4 3 2 A
        hand_value = [2, 1, 3, 8, 10, 4, 5]
        ans = get_straight(total_hand, suits, hand_value)
        self.assertEqual(ans, [5, 4, 3, 2, 1], "")
        # 6 5 4 3 2 
        hand_value = [2, 1, 3, 8, 6, 4, 5]
        ans = get_straight(total_hand, suits, hand_value)
        self.assertEqual(ans, [6, 5, 4, 3, 2], "")
        hand_value = [2, 11, 12, 8, 10, 9, 7]
        self.assertEqual(get_straight(total_hand, suits, hand_value), [12, 11, 10, 9, 8], "")
    
    def test_get_flush(self):
        total_hand = []

        # 
        hand_value = [9, 6, 1, 8, 7, 2, 13]
        suits = ['diamond'] * len(hand_value)
        self.assertEqual(get_flush(total_hand, suits, hand_value), [1, 13, 9, 8, 7], "") 

        hand_value = [9, 6, 3, 8, 7, 2, 13]
        suits = ['club'] * len(hand_value)
        self.assertEqual(get_flush(total_hand, suits, hand_value), [13, 9, 8, 7, 6], "") 

        hand_value = [9, 6, 3, 8, 7, 2, 13]
        suits = ['club'] * 5 + ['diamond'] * 2
        self.assertEqual(get_flush(total_hand, suits, hand_value), [9, 8, 7, 6, 3], "") 
    

    
    def test_get_full_house(self):

        suits = []
        total_hand = []
        # 2 threes
        hand_value = [9, 6, 9, 9, 6, 6, 8]
        self.assertEqual(get_full_house(total_hand, suits, hand_value), [9, 9, 9, 6, 6], "")
        # 2 threes
        hand_value = [1, 6, 1, 1, 6, 6, 8]
        self.assertEqual(get_full_house(total_hand, suits, hand_value), [1, 1, 1, 6, 6], "")
        # 1 three and 2 pairs
        hand_value = [9, 6, 9, 9, 6, 1, 1]
        self.assertEqual(get_full_house(total_hand, suits, hand_value), [9, 9, 9, 1, 1], "")    
        # 1 three and 2 pairs
        hand_value = [2, 6, 2, 2, 6, 1, 1]
        self.assertEqual(get_full_house(total_hand, suits, hand_value), [2, 2, 2, 1, 1], "")       
        # 1 three and 1 pair
        hand_value = [2, 6, 2, 2, 6, 8, 7]
        self.assertEqual(get_full_house(total_hand, suits, hand_value), [2, 2, 2, 6, 6], "")   
        # 1 three and 1 pair
        hand_value = [2, 6, 2, 2, 6, 1, 7]
        self.assertEqual(get_full_house(total_hand, suits, hand_value), [2, 2, 2, 6, 6], "")  

    def test_get_four_of_a_kind(self):

        suits = []
        total_hand = []
        # single A
        hand_value = [1, 6, 6, 6, 6, 7, 8]
        self.assertEqual(get_four_of_a_kind(total_hand, suits, hand_value), [6, 6, 6, 6, 1], "")
        # 4 As
        hand_value = [1, 1, 1, 1, 6, 6, 13]
        self.assertEqual(get_four_of_a_kind(total_hand, suits, hand_value), [1, 1, 1, 1, 13], "")
        # 
        hand_value = [9, 2, 2, 2, 2, 1, 1]
        self.assertEqual(get_four_of_a_kind(total_hand, suits, hand_value), [2, 2, 2, 2, 1], "")    
        # 1 three and 2 pairs
        hand_value = [9, 2, 2, 2, 2, 12, 13]
        self.assertEqual(get_four_of_a_kind(total_hand, suits, hand_value), [2, 2, 2, 2, 13], "")       
 



    
    

if __name__ == '__main__':
    unittest.main()