import gym

# import gym_open_poker
import yaml
import os
from gym_open_poker.envs.poker_util.novelty_generator import NoveltyGenerator
import numpy as np
import unittest
import pytest

testing_arg = [
    ("CardDistHigh", 15),
    ("CardDistLow", 15),
    ("Card1", 15),
    ("Action1", 15),
    ("RANDOM", 15),
    ("Environment1", 15),
    ("Environment2", 15),
    ("Environment1", 15),
    ("Agent1", 15),
    ("Agent2", 15),
    ("Agent3", 15),
    ("Event1", 15),
    ("Rule2", 15),
    ("Rule3", 15),
    ("Event2", 15),
    ("Card2", 15),
    ("Rule4", 15),
    ("Card3", 15),
]


@pytest.mark.parametrize("novelty_name,assert_action_val", testing_arg)
def test_novelty(novelty_name, assert_action_val):
    with open(f"./tests/config/config_{novelty_name}.yaml", "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # config_dict: Dict[str, List] = dict()

    # original environment
    env = gym.make("gym_open_poker/OpenPoker-v0", **config_dict)
    # env = gym.make("gym_open_poker/OpenPoker-v0")

    # novelty injection
    ng = NoveltyGenerator()

    # print out supported novelies
    # print(ng.get_support_novelties())
    # injecting
    if "novelty_list" in config_dict and config_dict["novelty_list"] and len(config_dict["novelty_list"]) > 0:
        env = ng.inject(env, config_dict["novelty_list"])

    # start gaming
    observation, info = env.reset(seed=65)

    count_perform_action = 0

    while True:
        print("============================")
        action_mask = info["action_masks"].astype(bool)
        all_action_list = np.array(list(range(6)))
        user_action = np.random.choice(all_action_list[action_mask], size=1).item()
        # print('----------------')
        observation, reward, terminated, truncated, info = env.step(int(user_action))
        # print("---observation---")
        # print(observation)
        # print("---reward---")
        # print(reward)
        # print("---info---")
        # print(info)
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

        count_perform_action += 1
        if count_perform_action == assert_action_val:
            break
    env.close()
    assert count_perform_action == assert_action_val
