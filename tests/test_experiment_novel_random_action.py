import gym
import gym_open_poker
import numpy as np
import os
import yaml
from gym_open_poker.envs.poker_util.novelty_generator import NoveltyGenerator

# load config parameters
config_path = './config.yaml'
if os.path.exists(config_path):
    with open(config_path, "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
else:
    config_dict = dict()

# original environment
env = gym.make("gym_open_poker/OpenPoker-v0", **config_dict)

# novelty injection
ng = NoveltyGenerator()

## print out supported novelies
print(ng.get_support_novelties())
## injecting
if config_dict['novelty_list'] and len(config_dict['novelty_list']) > 0:
    env = ng.inject(env, config_dict['novelty_list'])

# start gaming
observation, info = env.reset(seed=42)
print('============================')
print('---observation---')
print(observation)
print('---info---')
print(info)

while(True):
    print('============================')
    print('Enter your action:')
    # random
    action_mask = info['action_masks'].astype(bool)
    all_action_list = np.array(list(range(6)))
    user_action = np.random.choice(all_action_list[action_mask], size=1).item()


    #print('----------------')
    observation, reward, terminated, truncated, info = env.step(int(user_action))
    print('---observation---')
    print(observation)
    print('---reward---')
    print(reward)
    print('---info---')
    print(info)
    if truncated:
        print('meet termination condition! Over!')
        break
    if terminated:
        if observation['player_status'][observation['position'][1]] == 1:
            print('WINNNN!')
        else:
            print('LOST!')
        break