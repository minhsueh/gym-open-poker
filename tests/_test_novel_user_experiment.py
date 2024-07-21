import gym

# import gym_open_poker
import yaml
import os
from gym_open_poker.envs.poker_util.novelty_generator import NoveltyGenerator
import numpy as np

# from typing import Dict, List

# load config parameters

config_path = "./config.yaml"
if os.path.exists(config_path):
    with open(config_path, "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
else:
    config_dict = dict()

# config_dict: Dict[str, List] = dict()
print(config_dict)

# original environment
env = gym.make("gym_open_poker/OpenPoker-v0", **config_dict)
# env = gym.make("gym_open_poker/OpenPoker-v0")

# novelty injection
ng = NoveltyGenerator()
print(ng.get_support_novelties())

# print out supported novelies
print(ng.get_support_novelties())
# injecting
if "novelty_list" in config_dict and config_dict["novelty_list"] and len(config_dict["novelty_list"]) > 0:
    env = ng.inject(env, config_dict["novelty_list"])

seed = 65
if "seed" in config_dict:
    seed = config_dict["seed"]

# start gaming
observation, info = env.reset(seed=seed)
print("============================")
print("---observation---")
print(observation)
print("---info---")
print(info)

while True:
    print("============================")
    print("Enter your action:")
    action_mask = info["action_masks"].astype(bool)
    all_action_list = np.array(list(range(6)))
    allowable_actions = all_action_list[action_mask]
    print(f"allowable_actions = {allowable_actions}")
    # user_action = np.random.choice(allowable_actions, size=1).item()
    user_action = input()
    print(user_action)
    # print('----------------')
    observation, reward, terminated, truncated, info = env.step(int(user_action))
    print("---observation---")
    print(observation)
    print("---reward---")
    print(reward)
    print("---info---")
    print(info)
    if truncated:
        print("Meet termination condition! Over!")
        break
    if terminated:
        if observation["player_status"][observation["position"][1]] == 1:
            print("WINNNN!")
        else:
            if reward == -999:
                print("Use an invalid move! LOST!")
            else:
                print("LOST!")
        break


history = env.get_tournament_summary()
action_history = history["action_history"]
# print(action_history)


# env.close()
