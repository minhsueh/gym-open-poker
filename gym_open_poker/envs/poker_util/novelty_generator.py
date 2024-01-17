import sys
from gym_open_poker.envs.poker_util.novelty import NOVELTY_LIST
import gym_open_poker
import random
import logging

logger = logging.getLogger('gym_open_poker.envs.poker_util.logging_info.novelty_generator')

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
            self._logging(novelty)
            novel_env = novelty(env)


        else:
            # check if all novelies in novelty_list in self._novelties
            for novelty_string in novelty_list:
                if novelty_string not in self._novelties:
                    raise ValueError(f'{novelty_string} is not supported, please use NoveltyGenerator.get_support_novelties() to check supported novelties.')

            # inject novelties
            novelty_index = 1
            for novelty_string in novelty_list:
                novelty = getattr(novelty_module, novelty_string, None)
                self._logging(novelty, novelty_index)
                novel_env = novelty(env)
                novelty_index += 1

        return(novel_env)

    def _logging(self, novelty, novelty_index=None):
        """
        Args:
            novelty(gym.Wrapper): An wrapper object with doc string
            novelty_index(int): an novelty index to record in log
        """
        logger.debug("-------------------")
        if novelty_index is not None:
            logger.debug(f'{str(novelty_index)} NOVELTY INJECTING:')
        else:
            logger.debug("NOVELTY INJECTING:")
        logger.debug(novelty.__doc__)
        logger.debug("-------------------")