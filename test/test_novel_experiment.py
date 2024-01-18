import gym
import gym_open_poker
import yaml
import os
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

# print out supported novelies
# print(ng.get_support_novelties())
# injecting
if config_dict['novelty_list'] and len(config_dict['novelty_list']) > 0:
    env = ng.inject(env, config_dict['novelty_list'])

# start gaming
observation, info = env.reset(seed=65)
print('============================')
print('---observation---')
print(observation)
print('---info---')
print(info)

while(True):
    print('============================')
    print('Enter your action:')
    user_action = input()
    if int(user_action) not in range(6):
        print('It is not a valid action, current value = ' + user_action)
        continue
    #print('----------------')
    observation, reward, terminated, truncated, info = env.step(int(user_action))
    print('---observation---')
    print(observation)
    print('---reward---')
    print(reward)
    print('---info---')
    print(info)
    if truncated:
        print('Meet termination condition! Over!')
        break
    if terminated:
        if observation['player_status'][observation['position'][1]] == 1:
            print('WINNNN!')
        else:
            if reward == -999:
                print('Use an invalid move! LOST!')
            else:
                print('LOST!')
        break



# env.close()