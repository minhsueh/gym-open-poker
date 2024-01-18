import gym
import numpy as np
import sys

import collections
import logging

from agent import Agent
from agents import agent_p, agent_dump, agent_random

logger = logging.getLogger('gym_open_poker.envs.poker_util.logging_info.novelty.agent2')

class Agent2(gym.Wrapper):
    """
    This novelty, named Agent2, introduces one more player, agent_p, to the tournament.
    """
    def __init__(self, env):


        super().__init__(env)


        # add one new player
        last_player_index = env.number_of_players
        new_player_methods = getattr(sys.modules[__name__], 'agent_p')
        env.player_decision_agents['player_' + str(last_player_index+1)] = Agent(**new_player_methods.decision_agent_methods)


        # modify number_of_players
        env.number_of_players += 1
