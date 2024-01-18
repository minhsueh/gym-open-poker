import gym
import numpy as np
import sys

import collections
import logging

from agent import Agent
from agents import agent_p, agent_dump, agent_random

logger = logging.getLogger('gym_open_poker.envs.poker_util.logging_info.novelty.agent3')

class Agent3(gym.Wrapper):
    """
    This novelty, named Agent2, introduces fifteen more players, agent_p, to the tournament.
    """
    def __init__(self, env):


        super().__init__(env)

        add_player_number = 15

        # add one new player
        last_player_index = env.number_of_players

        for p_idx in range(1, add_player_number+1):
            new_player_methods = getattr(sys.modules[__name__], 'agent_p')
            env.player_decision_agents['player_' + str(last_player_index+p_idx)] = Agent(**new_player_methods.decision_agent_methods)


        # modify number_of_players
        env.number_of_players += add_player_number
