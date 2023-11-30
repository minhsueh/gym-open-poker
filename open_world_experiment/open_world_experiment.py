"""
This module is one level higher than open_poker; in other words, we utilize open_poker to test the AI agent's novelty detection and accommodation. 

Specifically, this experiment has two portions, including first non_novle(NN), and followed by novel(N) tournaments. Note that each
tournament call open_poker once, where novel tournaments utilize wrapper to inject novelty.

1. The first NN_count tournaments are original poker without any novelties.
2. The next N_count tournaments contain (N_ratio * N_count) novel tournaments and ((1 - N_ratio) * N_count) non_novelty tournaments

For example,
If we set NN_count = N_count = 30, and N_ratio = 0.6:
1. The first 30 tournaments are original poker without any novelties.
2. The next 30 tournaments contain 18 novel and 12 non_novelty tournaments. Note that we select novel tournaments randomly with N_ratio.



Hyperparameters:
NN_count(int), default = 30
N_count(int), default = 30
N_ratio(float), this value is bounded between 0 to 1. default = 0.6


"""

import gym
import open_poker
import yaml
import random
from open_poker.wrappers import CardDistHigh, CardDistLow

try:
    from importlib import resources as impresources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as impresources

class OpenWorldExpt():
    def __init__(self, NN_count=30, N_count=30, N_ratio=0.6, random_seed=15):
        """
        PARAMS:
            NN_count(int): the first starting tournaments number for non_novelty 
            N_count(int): the latter tournaments number
            N_ratio(float): the ratio for novel tournament in N_count
        """
        assert isinstance(NN_count, int) 
        assert isinstance(N_count, int) 
        assert 0 <= N_ratio <= 1

        self.NN_count = NN_count
        self.N_count = N_count
        self.N_ratio = N_ratio
        self.random_seed = random_seed


        # summary 
        self.win_list = [None] * (NN_count+N_ratio)


        self.executed = False

    def execute(self, config_path=None):
        """
        The main experiment
        PARAMS:
            config_path
        
        """
        # load config parameters
        if config_path:
            with open(config_path, "r") as stream:
                try:
                    config_dict = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        else:
            from . import default_setting
            try:
                deafault_file = (impresources.files(default_setting) / 'default_config.yaml')
                with open(deafault_file, "r") as stream:
                    try:
                        config_dict = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        print(exc)
            except AttributeError:
                print('Please check Python version >= 3.7')
                raise

        # random seed list
        random.seed(self.random_seed)
        num_list = list(range(100000))
        random.shuffle(num_list)
        rand_seed_list = num_list[:(self.NN_count + self.N_count)]

        ## novelty_inject_list
        novel_tournament_count = N_ratio * self.N_count
        NN_novelty_inject_list = [1] * novel_tournament_count + [0] * (self.N_count - novel_tournament_count)
        random.shuffle(NN_novelty_inject_list)
        novelty_inject_list = [0] * self.NN_count + NN_novelty_inject_list



        ## 
        for tournament_idx in range(NN_count, NN_count+N_count):
            if novelty_inject_list[tournament_idx] == 1:
                # novelty inject
                env = CardDistHigh(gym.make("open_poker/OpenPoker-v0", **config_dict))
            else:
                env = gym.make("open_poker/OpenPoker-v0", **config_dict)

            observation, info = env.reset(seed=rand_seed_list[tournament_idx])
            #print('============================')
            #print('---observation---')
            #print(observation)
            #print('---info---')
            #print(info)
            while(True):
               #print('============================')
                #print('Enter your action:')
                # user_action = input()
                action_mask = info['action_masks'].astype(bool)
                all_action_list = np.array(list(range(6)))
                user_action = np.random.choice(all_action_list[action_mask], size=1).item()

                if int(user_action) not in range(6):
                    print('It is not a valid action, current value = ' + user_action)
                    continue
                #print('----------------')
                observation, reward, terminated, truncated, info = env.step(int(user_action))
                #print('---observation---')
                #print(observation)
                #print('---reward---')
                #print(reward)
                #print('---info---')
                #print(info)
                if truncated or terminated:
                    if observation['player_status'][observation['position'][1]] == 1:
                        self.win_list[tournament_idx] = 1
                    else:
                        self.win_list[tournament_idx] = 0
                    break




        self.executed = True


    def get_summary(self):
        if not self.executed:
            print('OpenWorldExpt has not executed yet, please call execute first')
            raise

        return(self.win_list)


