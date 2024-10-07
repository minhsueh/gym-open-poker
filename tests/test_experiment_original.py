import gym
import gym_open_poker
import numpy as np
import os
import yaml
from gym_open_poker.envs.poker_util.novelty_generator import NoveltyGenerator


config_dict = dict()

# original environment
env = gym.make("gym_open_poker/OpenPoker-v0", **config_dict)


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
    user_action = input()
    while(int(user_action) not in range(6)):
        print(f'It is not a valid action, current value = {user_action}, please enter 0~5')
        user_action = input()


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