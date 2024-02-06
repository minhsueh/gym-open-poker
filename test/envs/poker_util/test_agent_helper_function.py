from gym_open_poker.envs.poker_util.agents import (agent_p, agent_dump)
import unittest
from gym_open_poker.envs.poker_util.agent import Agent
from gym_open_poker.envs.poker_util.card import Card
from gym_open_poker.envs.poker_util.initialize_game_elements import initialize_game_element
from gym_open_poker.envs.poker_util.agent_helper_function import *


class TestDigit(unittest.TestCase):
    def test_get_out_utility(self):

        self.assertEqual(format_float_precision(1.2, 2), 1.00, "")
        self.assertEqual(format_float_precision(0.62, 2), 0.62, "")
        self.assertEqual(format_float_precision(0.87), 0.87000, "")
        self.assertEqual(format_float_precision(-1.2), 0.00000, "")


"""
class TestProb(unittest.TestCase):
    def test_get_out_utility(self):
        # 5 card, three of a kind
        total_hand = [Card('club', 1), Card('diamond', 1), Card('heart', 3), Card('club', 4), Card('club', 5)]
        #self.assertEqual(get_out_probability(current_gameboard, total_hand)['four_of_a_kind'], format_float_precision(1/47), "")
        print(get_out_probability(current_gameboard, total_hand))
        # 5 card, four of a kind
        total_hand = [Card('club', 1), Card('diamond', 1), Card('heart', 1), Card('spade', 1), Card('club', 5)]
        #self.assertEqual(get_out_probability(current_gameboard, total_hand)['four_of_a_kind'], format_float_precision(1), "")
        print(get_out_probability(current_gameboard, total_hand))
        # 6 card, two three of a kind
        total_hand = [Card('club', 1), Card('diamond', 1), Card('heart', 1), Card('spade', 5), Card('club', 5), Card('heart', 5)]
        #self.assertEqual(get_out_probability(current_gameboard, total_hand)['four_of_a_kind'], format_float_precision(2/46), "")
        print(get_out_probability(current_gameboard, total_hand))
        # 5 card, royal flush except 1 card
        total_hand = [Card('spade', 1), Card('spade', 13), Card('spade', 12), Card('spade', 11), Card('club', 5)]
        #self.assertEqual(get_out_probability(current_gameboard, total_hand)['four_of_a_kind'], format_float_precision(2/46), "")
        
        print(get_out_probability(current_gameboard, total_hand))
"""


if __name__ == '__main__':
    unittest.main()