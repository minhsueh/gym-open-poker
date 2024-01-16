"""
This is the higher-level module to inject novelty into the original environment.
So, the user can directly assign novelty in the config file without modifying the execution script.
"""
import sys
from gym_open_poker.envs.poker_util.novelty import NOVELTY_LIST
import gym_open_poker
import random


class NoveltyGenerator():
    def __init__(self):
        self._novelties = [novelty.__name__ for novelty in NOVELTY_LIST if novelty != 'RANDOM'] 


    def get_support_novelties(self):
        return(self._novelties)

    def inject(self, env, novelty_list: list[str]):
        """
        Args:
            env(gym.Env): the original environment object create by gym.make
            novelty_list(list[str]): a novlety_list assigned by user in config file
        Return:
            novel_env(gym.Env): the environment object with novelty injected
        """
        novelty_module = __import__('novelty')

        if 'RANDOM' in novelty_list:
            # we randomly inject one of the novelty in NOVELTY_LIST
            novelty_string = random.choice([novelty_string for novelty_string in self._novelties])
            novelty = getattr(novelty_module, novelty_string, None)
            novel_env = novelty(env)

        else:
            # check if all novelies in novelty_list in self._novelties
            for novelty_string in novelty_list:
                if novelty_string not in self._novelties:
                    raise ValueError(f'{novelty_string} is not supported, please use NoveltyGenerator.get_support_novelties() to check supported novelties.')

            # inject novelties
            for novelty_string in novelty_list:
                novelty = getattr(novelty_module, novelty_string, None)
                novel_env = novelty(env)

        return(novel_env)