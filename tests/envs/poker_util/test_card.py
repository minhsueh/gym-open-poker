from gym_open_poker.envs.poker_util.card_utility_actions import (
    is_one_pair,
    is_two_pair,
    is_three_of_a_kind,
    is_straight,
    is_flush,
    is_full_house,
    is_four_of_a_kind,
    is_straight_flush,
    is_royal_flush,
    get_high_card,
    get_one_pair,
    get_two_pair,
    get_three_of_a_kind,
    get_straight,
    get_flush,
    get_full_house,
    get_four_of_a_kind
)
from gym_open_poker.envs.poker_util.card import Card
import unittest


class TestIs(unittest.TestCase):
    def test_is_one_pair(self):
        total_hand = [Card('club', 1),
                      Card('diamond', 13),
                      Card('heart', 12),
                      Card('club', 11),
                      Card('club', 10),
                      Card('club', 9),
                      Card('club', 8)]
        self.assertEqual(is_one_pair(total_hand), False, "1")
        total_hand = [Card('club', 1),
                      Card('diamond', 3),
                      Card('heart', 2),
                      Card('club', 7),
                      Card('club', 12),
                      Card('club', 9),
                      Card('club', 8)]
        self.assertEqual(is_one_pair(total_hand), False, "2")
        total_hand = [Card('club', 1),
                      Card('diamond', 1),
                      Card('heart', 9),
                      Card('club', 2),
                      Card('club', 7),
                      Card('club', 6),
                      Card('club', 3)]
        self.assertEqual(is_one_pair(total_hand), True, "3")
        total_hand = [Card('club', 1),
                      Card('diamond', 9),
                      Card('heart', 9),
                      Card('club', 2),
                      Card('club', 7),
                      Card('club', 6),
                      Card('club', 3)]
        self.assertEqual(is_one_pair(total_hand), True, "4")
        total_hand = [Card('club', 2),
                      Card('diamond', 9),
                      Card('heart', 8),
                      Card('club', 2),
                      Card('club', 7),
                      Card('club', 6),
                      Card('club', 3)]
        self.assertEqual(is_one_pair(total_hand), True, "5")
        total_hand = [Card('club', ),
                      Card('diamond', 9),
                      Card('heart', 8),
                      Card('club', 1),
                      Card('club', 7),
                      Card('club', 6),
                      Card('club', 3)]
        self.assertEqual(is_one_pair(total_hand), False, "6")

    def test_is_two_pair(self):
        total_hand = [Card('club', 1),
                      Card('diamond', 1),
                      Card('heart', 11),
                      Card('club', 11),
                      Card('club', 10),
                      Card('heart', 10),
                      Card('club', 8)]
        self.assertEqual(is_two_pair(total_hand), True, "3 pairs")
        total_hand = [Card('club', 1),
                      Card('diamond', 1),
                      Card('heart', 11),
                      Card('club', 11),
                      Card('club', 10),
                      Card('club', 9),
                      Card('club', 8)]
        self.assertEqual(is_two_pair(total_hand), True, "2 pairs")
        total_hand = [Card('club', 1),
                      Card('diamond', 1),
                      Card('heart', 9),
                      Card('club', 2),
                      Card('club', 7),
                      Card('club', 6),
                      Card('club', 3)]
        self.assertEqual(is_two_pair(total_hand), False, "1 pairs")
        total_hand = [Card('club', 1),
                      Card('diamond', 9),
                      Card('heart', 8),
                      Card('club', 2),
                      Card('club', 7),
                      Card('club', 6),
                      Card('club', 3)]
        self.assertEqual(is_two_pair(total_hand), False, "0 pairs")

    def test_is_three_of_a_kind(self):
        total_hand = [Card('club', 1),
                      Card('diamond', 1),
                      Card('heart', 1),
                      Card('club', 11),
                      Card('club', 10),
                      Card('heart', 10),
                      Card('club', 8)]
        self.assertEqual(is_three_of_a_kind(total_hand), True, "1 three")
        total_hand = [Card('club', 1),
                      Card('diamond', 1),
                      Card('heart', 1),
                      Card('spade', 9),
                      Card('club', 9),
                      Card('heart', 9),
                      Card('club', 8)]
        self.assertEqual(is_three_of_a_kind(total_hand), True, "2 threes")
        total_hand = [Card('club', 1),
                      Card('diamond', 1),
                      Card('heart', 11),
                      Card('spade', 11),
                      Card('club', 10),
                      Card('heart', 10),
                      Card('club', 8)]
        self.assertEqual(is_three_of_a_kind(total_hand), False, "3 pairs")

    def test_is_straight(self):
        total_hand = [Card('club', 1),
                      Card('diamond', 10),
                      Card('heart', 1),
                      Card('spade', 11),
                      Card('club', 10),
                      Card('heart', 13),
                      Card('club', 12)]
        self.assertEqual(is_straight(total_hand), True, "A to 10")
        total_hand = [Card('club', 1),
                      Card('diamond', 5),
                      Card('heart', 1),
                      Card('spade', 2),
                      Card('club', 10),
                      Card('heart', 3),
                      Card('club', 4)]
        self.assertEqual(is_straight(total_hand), True, "1 to 5")
        total_hand = [Card('club', 7),
                      Card('diamond', 6),
                      Card('heart', 11),
                      Card('spade', 9),
                      Card('club', 10),
                      Card('heart', 10),
                      Card('club', 8)]
        self.assertEqual(is_straight(total_hand), True, "6 to 10")
        total_hand = [Card('club', 7),
                      Card('diamond', 1),
                      Card('heart', 11),
                      Card('spade', 4),
                      Card('club', 10),
                      Card('heart', 10),
                      Card('club', 8)]
        self.assertEqual(is_straight(total_hand), False, "No straight")
    
    def test_is_flush(self):
        total_hand = [Card('diamond', 1),
                      Card('diamond', 10),
                      Card('heart', 1),
                      Card('diamond', 11),
                      Card('club', 10),
                      Card('diamond', 13),
                      Card('diamond', 12)]
        self.assertEqual(is_flush(total_hand), True, "diamond flush")
        total_hand = [Card('diamond', 1),
                      Card('diamond', 5),
                      Card('heart', 1),
                      Card('diamond', 2),
                      Card('club', 10),
                      Card('diamond', 3),
                      Card('club', 4)]
        self.assertEqual(is_flush(total_hand), False, "4 diamonds")

    def test_is_full_house(self):
        # 2 threes
        total_hand = [Card('diamond', 9),
                      Card('diamond', 6),
                      Card('heart', 9),
                      Card('spade', 9),
                      Card('club', 6),
                      Card('spade', 6),
                      Card('club', 8)]
        self.assertEqual(is_full_house(total_hand), True, "2 threes")
        # 1 three and 2 pairs
        total_hand = [Card('diamond', 2),
                      Card('diamond', 6),
                      Card('heart', 2),
                      Card('spade', 2),
                      Card('club', 6),
                      Card('spade', 1),
                      Card('club', 1)]
        self.assertEqual(is_full_house(total_hand), True, "1 three and 2 pairs")
        # 1 three and 1 pair
        total_hand = [Card('diamond', 2),
                      Card('diamond', 6),
                      Card('heart', 2),
                      Card('spade', 2),
                      Card('club', 6),
                      Card('spade', 8),
                      Card('club', 7)]
        self.assertEqual(is_full_house(total_hand), True, "1 three and 1 pair")
        # 3 pair
        total_hand = [Card('diamond', 2),
                      Card('diamond', 6),
                      Card('heart', 2),
                      Card('spade', 3),
                      Card('club', 6),
                      Card('heart', 3),
                      Card('club', 7)]
        self.assertEqual(is_full_house(total_hand), False, "3 pairs")
        # 7 single
        total_hand = [Card('diamond', 2),
                      Card('diamond', 6),
                      Card('heart', 3),
                      Card('spade', 8),
                      Card('club', 13),
                      Card('heart', 1),
                      Card('club', 7)]
        self.assertEqual(is_full_house(total_hand), False, "7 single")
    
    def test_is_four_of_a_kind(self):
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('heart', 1),
                      Card('spade', 1),
                      Card('club', 10),
                      Card('heart', 11),
                      Card('club', 12)]
        self.assertEqual(is_four_of_a_kind(total_hand), True, "1 fours")
        total_hand = [Card('diamond', 9),
                      Card('club', 9),
                      Card('heart', 9),
                      Card('spade', 6),
                      Card('club', 6),
                      Card('heart', 6),
                      Card('club', 8)]
        self.assertEqual(is_four_of_a_kind(total_hand), False, "2 threes")
        total_hand = [Card('diamond', 2),
                      Card('club', 2),
                      Card('heart', 3),
                      Card('spade', 3),
                      Card('club', 6),
                      Card('heart', 6),
                      Card('club', 7)]
        self.assertEqual(is_four_of_a_kind(total_hand), False, "3 pairs")

    def test_is_straight_flush(self):
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('diamond', 10),
                      Card('spade', 10),
                      Card('diamond', 11),
                      Card('diamond', 12),
                      Card('diamond', 13)]
        self.assertEqual(is_straight_flush(total_hand), True, "A to 10")
        total_hand = [Card('heart', 1),
                      Card('club', 1),
                      Card('diamond', 10),
                      Card('heart', 10),
                      Card('diamond', 11),
                      Card('diamond', 12),
                      Card('diamond', 13)]
        self.assertEqual(is_straight_flush(total_hand), False, "A to 10 but suit not match")
        total_hand = [Card('heart', 1),
                      Card('club', 1),
                      Card('diamond', 2),
                      Card('diamond', 3),
                      Card('diamond', 4),
                      Card('diamond', 5),
                      Card('heart', 10)]
        self.assertEqual(is_straight_flush(total_hand), False, "1 to 5 but suit not match")
        total_hand = [Card('diamond', 1),
                      Card('diamond', 6),
                      Card('diamond', 7),
                      Card('diamond', 8),
                      Card('diamond', 9),
                      Card('diamond', 10),
                      Card('diamond', 11)]
        self.assertEqual(is_straight(total_hand), True, "6 to 10")
        total_hand = [Card('diamond', 1),
                      Card('diamond', 4),
                      Card('diamond', 7),
                      Card('diamond', 8),
                      Card('diamond', 10),
                      Card('club', 10),
                      Card('diamond', 11)]
        self.assertEqual(is_straight_flush(total_hand), False, "No straight")

    def test_is_royal_flush(self):
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('diamond', 10),
                      Card('club', 10),
                      Card('diamond', 11),
                      Card('diamond', 12),
                      Card('diamond', 13)]
        self.assertEqual(is_royal_flush(total_hand), True, "diamond A to 10")
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('diamond', 10),
                      Card('club', 10),
                      Card('club', 11),
                      Card('club', 12),
                      Card('club', 13)]
        self.assertEqual(is_royal_flush(total_hand), True, "club A to 10")
        total_hand = [Card('heart', 1),
                      Card('club', 1),
                      Card('diamond', 10),
                      Card('heart', 10),
                      Card('diamond', 11),
                      Card('diamond', 12),
                      Card('diamond', 13)]
        self.assertEqual(is_royal_flush(total_hand), False, "A to 10 but suit not match")
        total_hand = [Card('heart', 1),
                      Card('club', 1),
                      Card('diamond', 2),
                      Card('diamond', 3),
                      Card('diamond', 4),
                      Card('diamond', 5),
                      Card('diamond', 10)]
        self.assertEqual(is_royal_flush(total_hand), False, "1 to 5 but suit not match")
        total_hand = [Card('diamond', 1),
                      Card('diamond', 6),
                      Card('diamond', 7),
                      Card('diamond', 8),
                      Card('diamond', 9),
                      Card('diamond', 10),
                      Card('diamond', 11)]
        self.assertEqual(is_royal_flush(total_hand), False, "6 to 10")
        total_hand = [Card('diamond', 1),
                      Card('diamond', 4),
                      Card('diamond', 7),
                      Card('diamond', 8),
                      Card('club', 10),
                      Card('diamond', 10),
                      Card('diamond', 11)]
        self.assertEqual(is_royal_flush(total_hand), False, "No straight")
        total_hand = [Card('heart', 1),
                      Card('diamond', 2),
                      Card('heart', 3),
                      Card('heart', 4),
                      Card('heart', 5),
                      Card('diamond', 7),
                      Card('heart', 9)]
        self.assertEqual(is_royal_flush(total_hand), False, "No flush at 2")


class TestGet(unittest.TestCase):
    def test_get_high_card(self):
        total_hand = [Card('diamond', 1),
                      Card('diamond', 13),
                      Card('diamond', 12),
                      Card('diamond', 11),
                      Card('club', 10),
                      Card('diamond', 9),
                      Card('diamond', 8)]
        self.assertEqual(get_high_card(total_hand), [1, 13, 12, 11, 10], "")
        total_hand = [Card('diamond', 1),
                      Card('diamond', 2),
                      Card('diamond', 3),
                      Card('diamond', 7),
                      Card('club', 8),
                      Card('diamond', 9),
                      Card('diamond', 12)]
        self.assertEqual(get_high_card(total_hand), [1, 12, 9, 8, 7], "")
        total_hand = [Card('diamond', 2),
                      Card('diamond', 3),
                      Card('diamond', 7),
                      Card('diamond', 8),
                      Card('club', 9),
                      Card('diamond', 10),
                      Card('diamond', 12)]
        self.assertEqual(get_high_card(total_hand), [12, 10, 9, 8, 7], "")

    def test_get_one_pair(self):
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('diamond', 2),
                      Card('diamond', 3),
                      Card('club', 6),
                      Card('diamond', 7),
                      Card('diamond', 9)]
        self.assertEqual(get_one_pair(total_hand), [1, 1, 9, 7, 6], "")
        total_hand = [Card('diamond', 1),
                      Card('club', 2),
                      Card('diamond', 3),
                      Card('diamond', 6),
                      Card('club', 7),
                      Card('club', 9),
                      Card('diamond', 9)]
        self.assertEqual(get_one_pair(total_hand), [9, 9, 1, 7, 6], "")
        total_hand = [Card('diamond', 2),
                      Card('club', 2),
                      Card('diamond', 3),
                      Card('diamond', 6),
                      Card('club', 7),
                      Card('club', 8),
                      Card('diamond', 9)]
        self.assertEqual(get_one_pair(total_hand), [2, 2, 9, 8, 7], "")

    def test_get_two_pair(self):
        # three pair
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('diamond', 2),
                      Card('diamond', 3),
                      Card('club', 3),
                      Card('club', 7),
                      Card('diamond', 7)]
        self.assertEqual(get_two_pair(total_hand), [1, 1, 7, 7, 3], "")
        # Ace pair
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('club', 2),
                      Card('diamond', 2),
                      Card('club', 3),
                      Card('club', 6),
                      Card('diamond', 7)]
        self.assertEqual(get_two_pair(total_hand), [1, 1, 2, 2, 7], "")
        # single Ace
        total_hand = [Card('diamond', 1),
                      Card('club', 2),
                      Card('club', 3),
                      Card('diamond', 3),
                      Card('club', 6),
                      Card('club', 9),
                      Card('diamond', 9)]
        self.assertEqual(get_two_pair(total_hand), [9, 9, 3, 3, 1], "")

    def test_get_three_of_a_kind(self):
        # three of Ace
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('spade', 1),
                      Card('diamond', 6),
                      Card('club', 7),
                      Card('club', 8),
                      Card('diamond', 9)]
        self.assertEqual(get_three_of_a_kind(total_hand), [1, 1, 1, 9, 8], "")
        # single Ace
        total_hand = [Card('diamond', 1),
                      Card('club', 2),
                      Card('spade', 5),
                      Card('diamond', 6),
                      Card('heart', 8),
                      Card('club', 8),
                      Card('diamond', 8)]
        self.assertEqual(get_three_of_a_kind(total_hand), [8, 8, 8, 1, 6], "")
    
    def test_get_straight(self):
        # A 13 12 11 10
        total_hand = [Card('diamond', 1),
                      Card('club', 13),
                      Card('spade', 12),
                      Card('diamond', 11),
                      Card('heart', 10),
                      Card('club', 9),
                      Card('diamond', 8)]
        self.assertEqual(get_straight(total_hand), [1, 13, 12, 11, 10], "")
        # 5 4 3 2 A
        total_hand = [Card('diamond', 1),
                      Card('club', 2),
                      Card('spade', 3),
                      Card('diamond', 4),
                      Card('heart', 5),
                      Card('club', 8),
                      Card('diamond', 10)]
        ans = get_straight(total_hand)
        self.assertEqual(ans, [5, 4, 3, 2, 1], "")
        # 6 5 4 3 2 
        total_hand = [Card('diamond', 1),
                      Card('club', 2),
                      Card('spade', 3),
                      Card('diamond', 4),
                      Card('heart', 5),
                      Card('club', 6),
                      Card('diamond', 8)]
        ans = get_straight(total_hand)
        self.assertEqual(ans, [6, 5, 4, 3, 2], "")
        total_hand = [Card('diamond', 2),
                      Card('club', 7),
                      Card('spade', 8),
                      Card('diamond', 9),
                      Card('heart', 10),
                      Card('club', 11),
                      Card('diamond', 12)]
        self.assertEqual(get_straight(total_hand), [12, 11, 10, 9, 8], "")

    def test_get_flush(self):
        total_hand = [Card('diamond', 1),
                      Card('diamond', 2),
                      Card('diamond', 6),
                      Card('diamond', 7),
                      Card('diamond', 8),
                      Card('diamond', 9),
                      Card('diamond', 13)]
        self.assertEqual(get_flush(total_hand), [1, 13, 9, 8, 7], "")
        total_hand = [Card('club', 2),
                      Card('club', 3),
                      Card('club', 6),
                      Card('club', 7),
                      Card('club', 8),
                      Card('club', 9),
                      Card('club', 13)]
        self.assertEqual(get_flush(total_hand), [13, 9, 8, 7, 6], "")
        total_hand = [Card('diamond', 2),
                      Card('club', 3),
                      Card('club', 6),
                      Card('club', 7),
                      Card('club', 8),
                      Card('club', 9),
                      Card('diamond', 13)]
        self.assertEqual(get_flush(total_hand), [9, 8, 7, 6, 3], "")

    def test_get_full_house(self):
        # 2 threes
        total_hand = [Card('diamond', 6),
                      Card('club', 6),
                      Card('spade', 6),
                      Card('club', 8),
                      Card('spade', 9),
                      Card('club', 9),
                      Card('diamond', 9)]
        self.assertEqual(get_full_house(total_hand), [9, 9, 9, 6, 6], "")
        # 2 threes
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('spade', 1),
                      Card('club', 6),
                      Card('spade', 6),
                      Card('diamond', 6),
                      Card('diamond', 8)]
        self.assertEqual(get_full_house(total_hand), [1, 1, 1, 6, 6], "")
        # 1 three and 2 pairs
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('spade', 6),
                      Card('club', 6),
                      Card('spade', 9),
                      Card('diamond', 9),
                      Card('club', 9)]
        self.assertEqual(get_full_house(total_hand), [9, 9, 9, 1, 1], "")
        # 1 three and 2 pairs
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('spade', 2),
                      Card('club', 2),
                      Card('diamond', 2),
                      Card('diamond', 6),
                      Card('club', 6)]
        self.assertEqual(get_full_house(total_hand), [2, 2, 2, 1, 1], "")
        # 1 three and 1 pair
        total_hand = [Card('diamond', 2),
                      Card('club', 2),
                      Card('spade', 2),
                      Card('club', 6),
                      Card('diamond', 6),
                      Card('diamond', 7),
                      Card('club', 8)]
        self.assertEqual(get_full_house(total_hand), [2, 2, 2, 6, 6], "")
        # 1 three and 1 pair
        total_hand = [Card('diamond', 1),
                      Card('club', 2),
                      Card('spade', 2),
                      Card('diamond', 2),
                      Card('spade', 6),
                      Card('diamond', 6),
                      Card('club', 7)]
        self.assertEqual(get_full_house(total_hand), [2, 2, 2, 6, 6], "")

    def test_get_four_of_a_kind(self):
        # single A
        total_hand = [Card('diamond', 1),
                      Card('club', 6),
                      Card('heart', 6),
                      Card('diamond', 6),
                      Card('spade', 6),
                      Card('diamond', 7),
                      Card('club', 8)]
        self.assertEqual(get_four_of_a_kind(total_hand), [6, 6, 6, 6, 1], "")
        # 4 As
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('heart', 1),
                      Card('spade', 1),
                      Card('spade', 6),
                      Card('diamond', 6),
                      Card('club', 13)]
        self.assertEqual(get_four_of_a_kind(total_hand), [1, 1, 1, 1, 13], "")
        # 4 2
        total_hand = [Card('diamond', 1),
                      Card('club', 1),
                      Card('heart', 2),
                      Card('club', 2),
                      Card('spade', 2),
                      Card('diamond', 2),
                      Card('club', 9)]
        self.assertEqual(get_four_of_a_kind(total_hand), [2, 2, 2, 2, 1], "")
        # 1 three and 2 pairs
        total_hand = [Card('diamond', 2),
                      Card('club', 2),
                      Card('heart', 2),
                      Card('spade', 2),
                      Card('spade', 9),
                      Card('diamond', 12),
                      Card('club', 13)]
        self.assertEqual(get_four_of_a_kind(total_hand), [2, 2, 2, 2, 13], "")


if __name__ == '__main__':
    unittest.main()
