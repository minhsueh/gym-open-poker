from gym_open_poker.envs.poker_util.agents import (agent_p, agent_dump)
import unittest
from gym_open_poker.envs.poker_util.agent import Agent
from gym_open_poker.envs.poker_util.card import Card
from gym_open_poker.envs.poker_util.initialize_game_elements import initialize_game_element
from gym_open_poker.envs.poker_util.dealer import *


class TestDealer(unittest.TestCase):
    def test_get_player_rank_and_cash(self):
        player_list = [agent_dump, agent_p, agent_p]
        player_decision_agents = dict()
        player_decision_agents['player_1'] = 'player_1'
        for player_idx, player in enumerate(player_list):
            player_decision_agents['player_' + str(player_idx+2)] = Agent(**player.decision_agent_methods)
        current_gameboard = initialize_game_element(player_decision_agents, {}, 5)

        
        print(get_player_rank_and_cash(current_gameboard))



if __name__ == '__main__':
    unittest.main()