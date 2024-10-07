"""
This is the simplest version of Q reinforcement learning.

We embed basic observations only, encoded observations including:
1. game index: size 1: potential values (1~30)
2. phase: size 1 with 4 potential values
3. pot amount: size 1: potential values (0~1600)
4. community cards: size 5 with 53 potential valus (-1 in pre-flop) 
5. position: size 2
6. hole cards: size 2 with 53 potential valus (-1 in pre-flop)
7. player's bankroll: size 10 (defualt that there are 8 players in game, -1 if no player)
8. player's action: size 10 (defualt that there are 8 players in game, -1 if no player)



Data format:

self.tournament_his
    X: encoded observation (size = self.state_space_size ) 
    y: y_raw[a] + reward



self.game_his  
    X: encoded observation (size = self.state_space_size )
    y_raw: action value (size = self.aciton_space_size)
    a: chosen action(not necessary be the maximum of y, it might be affected by action masks)

"""


import numpy as np
import pandas as pd
import os
import sys

# for agent calculation
# from gym_open_poker.envs.poker_util.action_choices import *
# from gym_open_poker.envs.poker_util.card_utility_actions import *
from itertools import combinations

# from gym_open_poker.envs.poker_util.agent_helper_function import (format_float_precision, get_out_probability, is_out_in_hand)
from collections import Counter, deque

# from gym_open_poker.envs.poker_util.phase import *
# from gym_open_poker.envs.poker_util.card import Card

import matplotlib.pyplot as plt


# tf
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Masking, Reshape, Input, Dropout, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras import initializers
from tensorflow.keras.optimizers.legacy import Adam
from tensorflow.keras.callbacks import Callback

import random



class OweAgent:
    def __init__(self):
        self.name = 'owe_agent'

    def action(self, observation, info, reward=None, terminated=None, truncated=None):
        raise NotImplementedError

    def novelty_detection(self):
        raise NotImplementedError




random.seed(5)

STATE_SIZE = 1 + 1 + 1 + 5 + 2 + 2 + 10 + 10

"""
class BehaviorPolicy:
    def __init__(self):



    def random(state, action_mask):
        action_mask = info['action_masks'].astype(bool)
        all_action_list = np.array(list(range(6)))
        allowable_actions = all_action_list[action_mask]
        return(np.random.choice(allowable_actions))
"""


# OUTPUT_FILE_PATH = './results/'


class LossHistory(Callback):
    def on_train_begin(self, logs={}):
        self.losses = []
        self.val_losses = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get("loss"))


class AgentDQNReplayFrame(OweAgent):
    def __init__(
        self,
        epsilon=0.05,
        state_space_size=STATE_SIZE,
        aciton_space_size=6,
        alpha=0.9,
        gamma=0.99,  # q learning reward discount factor
        delta=0.1,  # reward assigment factor
        random_seed=5,
        storing_folder_name=None,
    ):
        self.random_seed = random_seed
        self.initialized = False
        self.epsilon = epsilon

        self.state_space_size = state_space_size
        self.aciton_space_size = aciton_space_size

        if alpha is None:
            self.alpha = 0.9
        else:
            self.alpha = alpha

        self.gamma = gamma

        if delta is None:
            self.delta = 0.1
        else:
            self.delta = delta

        self.tournament_his = {"x": [], "y": []}
        self.game_his = {"encoded_observation": [], "action": [], "encoded_observaion_next": [], "done": []}
        self.pre_game_idx = -1
        self.cur_game_idx = None

        if storing_folder_name:
            self._storing_path = os.path.dirname(os.path.abspath(__file__)) + "/results/" + storing_folder_name + "/"
        else:
            self._storing_path = os.path.dirname(os.path.abspath(__file__)) + "/results/"

        if not os.path.exists(self._storing_path):
            os.makedirs(self._storing_path)

        self.cash_his = []
        self.mse_his = []
        self.cash_episode_index = []
        self.mse_episode_index = []

        self.callback_mse_history = LossHistory()

        # replay memory
        self.replay_memory = ReplayMemory(50000)
        self.replay_sampling_size = 256
        self.learning_step_counter = 0
        self.C = 32  # steps to update dqn_target
        self.frame_size = 4
        self.observation_hist = []

    def _create_empty_dqn(self):
        opt = Adam(learning_rate=self.alpha)

        initializer = initializers.RandomNormal(mean=0.0, stddev=0.05, seed=5)
        bias_initializer = initializers.Zeros()

        dqn = Sequential()
        dqn.add(Masking(mask_value=-1, input_shape=(self.frame_size, self.state_space_size)))
        # dqn.add(Reshape((-1, 1)))
        # dqn.add(Input(shape=(32,)))
        dqn.add(Dense(512, activation="sigmoid", kernel_initializer=initializer, bias_initializer=bias_initializer))
        # dqn.add(Dense(500, activation='sigmoid'))
        dqn.add(Dense(512, activation="sigmoid", kernel_initializer=initializer, bias_initializer=bias_initializer))
        dqn.add(Dense(self.aciton_space_size, activation="linear"))

        dqn.compile(loss="mse", optimizer=opt, metrics=["mse"])

        # print(dqn.summary())

        return dqn

    def _create_empty_dqn_w_dropout(self):
        opt = Adam(learning_rate=self.alpha)

        initializer = initializers.RandomNormal(mean=0.0, stddev=0.05, seed=5)
        bias_initializer = initializers.Zeros()

        dqn = Sequential()
        # dqn.add(Input(shape=(self.frame_size, self.state_space_size)))
        dqn.add(Masking(mask_value=-1, input_shape=(self.frame_size, self.state_space_size)))
        dqn.add(Flatten())
        # dqn.add(Reshape((-1, 1)))
        # dqn.add(Input(shape=(32,)))
        dqn.add(Dense(512, activation="sigmoid", kernel_initializer=initializer, bias_initializer=bias_initializer))
        dqn.add(Dropout(0.2))
        dqn.add(Dense(512, activation="sigmoid", kernel_initializer=initializer, bias_initializer=bias_initializer))
        dqn.add(Dropout(0.2))
        # dqn.add(Dense(self.aciton_space_size, activation="linear"))
        dqn.add(Dense(self.aciton_space_size, activation="softmax"))

        dqn.compile(loss="mse", optimizer=opt, metrics=["mse"])

        print(dqn.summary())

        return dqn

    def initialize(self, learning=False, read_dqn_path=None):
        if read_dqn_path is not None:
            print("model loading...")
            self.dqn = tf.keras.saving.load_model(read_dqn_path)
            self.target_dqn = tf.keras.saving.load_model(read_dqn_path)
            # print('-----')
            # for layer in self.dqn.layers:
            #    print(layer.get_weights())
        else:
            self.dqn = self._create_empty_dqn_w_dropout()
            self.target_dqn = self._create_empty_dqn_w_dropout()

        self.learning = learning

        self.initialized = True

    def observation_encoder(self, observation, info):
        """
        Args:
            observation(np.array): the observation returned by gym
            info(np.array): the info returned by gym
        Return:
            (keras tensor)
        """
        """
        In this agent, I just use fully connected layer, so the order of inpuut does not matter.
        1. game index: size 1: potential values (1~30)
        2. phase: size 1 with 4 potential values
        3. pot amount: size 1: potential values (0~1600)
        4. community cards: size 5 with 53 potential valus (-1 in pre-flop) 
        5. position: size 2
        6. hole cards: size 2 with 53 potential valus (-1 in pre-flop)
        7. player's bankroll: size 10 (defualt that there are 10 players in game, -1 if no player)
        8. player's action: size 10 (defualt that there are 10 players in game, -1 if no player)
        """
        obs = []
        # 1. game_index
        game_index = observation["game_idx"].tolist()
        # 2. phase
        if observation["community_card"][4] != -1:
            # river
            phase = [3]
        elif observation["community_card"][3] != -1:
            # turn
            phase = [2]
        elif observation["community_card"][0] != -1:
            # flop
            phase = [1]
        elif observation["community_card"][0] == -1:
            # pre-flop
            phase = [0]
        else:
            raise
        # 3. pot amount
        pot_amount = observation["pot_amount"].tolist()
        # 4. community cards:
        community_card = observation["community_card"].tolist()
        # 5. position
        position = observation["position"].tolist()
        # 6. hole cards:
        hole_cards = observation["hole_cards"].tolist()
        # 7. player's bankroll
        bankroll_raw = observation["bankroll"].tolist()
        if len(bankroll_raw) <= 10:
            bankroll = bankroll_raw + [-1] * (10 - len(bankroll_raw))
        else:
            bankroll = bankroll_raw[:10]
        # 8. player's action
        player_action_raw = observation["action"].tolist()
        if len(bankroll_raw) <= 10:
            player_action = player_action_raw + [-1] * (10 - len(player_action_raw))
        else:
            player_action = player_action_raw[:10]

        observation_encoded_list = (
            game_index + phase + pot_amount + community_card + position + hole_cards + bankroll + player_action
        )
        observation_encoded = tf.convert_to_tensor(observation_encoded_list, dtype=tf.float32)
        self.observation_hist.append(observation_encoded)
        frame = self.frame_processor()

        return frame

    def dummy_observation(self):
        dummy_list = [-1] * STATE_SIZE
        dummy_observation_encoded = tf.convert_to_tensor(dummy_list, dtype=tf.float32)
        return dummy_observation_encoded

    def frame_processor(self):
        # concate self.frame_size of observation
        # if len(self.observation_hist < self.frame_size, then concat dummy observation
        process_frame = []
        cur_obs_len = len(self.observation_hist)
        if cur_obs_len < self.frame_size:
            process_frame = [self.dummy_observation()] * (self.frame_size - cur_obs_len) + self.observation_hist[
                -(cur_obs_len):
            ]
        else:
            process_frame = self.observation_hist[-(self.frame_size) :]
        frame = tf.convert_to_tensor(process_frame, dtype=tf.float32)
        # print(frame)
        # frame = tf.expand_dims(frame, axis=0)
        frame = tf.reshape(frame, shape=(-1, self.frame_size, STATE_SIZE))
        # print(frame)
        return frame

    def action(self, observation, reward, terminated, truncated, info):
        action_mask = info["action_masks"]
        action_mask_bool = info["action_masks"].astype(bool)
        all_action_list = np.array(list(range(6)))
        allowable_actions = all_action_list[action_mask_bool]

        encoded_observation = self.observation_encoder(observation, info)
        predicted = self.dqn.predict(encoded_observation)


        # epsilon_greedy
        p = np.random.random()
        if p < self.epsilon:
            user_action = np.random.choice(allowable_actions)
        else:
            sorted_predicted = tf.argsort(predicted, direction="DESCENDING").numpy()

            for action_idx in np.nditer(sorted_predicted):
                # if action_mask[action_idx].item() == 1:
                if action_idx in allowable_actions:
                    user_action = action_idx
                    break

        return user_action



    def train(self, env, seed):

        observation, info = env.reset(seed=seed)
        while True:

            # process observaion to state
            action_mask = info["action_masks"]
            action_mask_bool = info["action_masks"].astype(bool)
            all_action_list = np.array(list(range(6)))
            allowable_actions = all_action_list[action_mask_bool]
            encoded_observation = self.observation_encoder(observation, info)
            predicted = self.dqn.predict(encoded_observation)
            # print("==+=")
            # print(encoded_observation.shape)
            # print(predicted)

            # select action by using epsilon_greedy
            p = np.random.random()
            if p < self.epsilon:
                user_action = np.random.choice(allowable_actions)
            else:
                sorted_predicted = tf.argsort(predicted, direction="DESCENDING").numpy()

                for action_idx in np.nditer(sorted_predicted):
                    # if action_mask[action_idx].item() == 1:
                    if action_idx in allowable_actions:
                        user_action = action_idx
                        break

            # perform action
            observation_next, reward, terminated, truncated, info_next = env.step(int(user_action))
            action_list = []
            for i in range(self.aciton_space_size):
                if i == user_action:
                    action_list.append(1)
                else:
                    action_list.append(0)

            encoded_observation_next = self.observation_encoder(observation_next, info_next)

            # recording tem results for plotting
            # record self.cash_his
            cur_cash = observation["bankroll"].tolist()[observation["position"].tolist()[1]]
            self.cash_his.append(cur_cash)
            # game_index
            self.cur_game_idx = int(observation["game_idx"])
            if self.cur_game_idx == 1 and self.cur_game_idx != self.pre_game_idx:
                # record self.episode_index
                self.cash_episode_index.append(len(self.cash_his) - 1)
                self.mse_episode_index.append(len(self.mse_his) - 1)

            # record game history
            self.game_his["encoded_observation"].append(encoded_observation)
            self.game_his["action"].append(action_list)
            self.game_his["encoded_observaion_next"].append(encoded_observation_next)
            if info_next["pre_game_last_observation"] != [] or terminated or truncated:
                self.game_his["done"].append(1)
            else:
                self.game_his["done"].append(0)
            # calculate reward with reward shaping
            if info_next["pre_game_last_observation"] != [] or terminated or truncated:
                # calculate rewards in episode with gamma
                reward_list = [0] * len(self.game_his["action"])
                reward_list[-1] = reward
                for ri in range(len(self.game_his["action"]) - 2, -1, -1):
                    reward_list[ri] = reward_list[ri + 1] * self.delta

                assert (
                    len(self.game_his["encoded_observation"])
                    == len(self.game_his["action"])
                    == len(self.game_his["encoded_observaion_next"])
                    == len(self.game_his["done"])
                )
                for a_idx in range(len(self.game_his["action"])):
                    tem_state = self.game_his["encoded_observation"][a_idx]
                    tem_action = self.game_his["action"][a_idx]
                    tem_state_next = self.game_his["encoded_observaion_next"][a_idx]
                    tem_done = self.game_his["done"][a_idx]
                    tem_reward = reward_list[a_idx]

                    self.replay_memory.push(tem_state, tem_action, tem_reward, tem_done, tem_state_next)

                self.game_his = {"encoded_observation": [], "action": [], "encoded_observaion_next": [], "done": []}
                self.observation_hist = []

            # replay memory learning
            if self.replay_memory.can_sample():
                sampled_memory = self.replay_memory.sample(self.replay_sampling_size)
                """
                # stochastic gradient descent
                for tem_encoded_observation, tem_action, tem_reward, tem_done, tem_encoded_observation_next in sampled_memory:
                    if tem_done == 1:
                        tem_y = [np.array(tem_action) * tem_reward]
                    else:
                        tem_q_target_predicted = max(self.target_dqn.predict(tem_encoded_observation_next))
                        tem_y = [np.array(tem_action) * (tem_reward + self.gamma * tem_q_target_predicted)]
                    tem_y = np.array(tem_y).reshape(1, -1)
                    self.dqn.fit(tem_encoded_observation, tem_y, callbacks=[self.callback_mse_history])
                    self.mse_his += self.callback_mse_history.losses
                """
                """
                # mini batch gradient descent with batch size 16
                tem_x = []
                tem_y = []
                for tem_encoded_observation, tem_action, tem_reward, tem_done, tem_encoded_observation_next in sampled_memory:
                    # print("--------")
                    # print(tem_encoded_observation)
                    # print(tem_done)
                    tem_x.append(tem_encoded_observation)
                    if tem_done == 1:
                        tem_y.append([np.array(tem_action) * tem_reward])
                    else:
                        # print(self.target_dqn.predict(tem_encoded_observation_next))
                        tem_q_target_predicted = max(max(self.target_dqn.predict(tem_encoded_observation_next)))
                        # print("-.-")
                        # print(tem_q_target_predicted)
                        tem_y.append([np.array(tem_action) * (tem_reward + self.gamma * tem_q_target_predicted)])
                # print(np.array(tem_x).shape)
                # print(tem_y)
                # print(np.array(tem_y).shape)
                tem_x = np.array(tem_x).reshape(len(sampled_memory), self.frame_size, -1)
                # print(tem_x.shape)
                tem_y = np.array(tem_y).reshape(len(sampled_memory), -1)
                # print(tem_y.shape)
                print("---")
                print(tem_y)
                print("---")
                """

                # matrix way
                # print(sampled_memory)
                # print("---")
                tem_encoded_observation = [row[0] for row in sampled_memory]
                tem_encoded_observation = np.array(tem_encoded_observation).reshape(len(sampled_memory), self.frame_size, -1)
                tem_action = [row[1] for row in sampled_memory]
                tem_action = np.array(tem_action).reshape(len(sampled_memory), -1)
                tem_reward = [row[2] for row in sampled_memory]
                tem_reward = np.array(tem_reward).reshape(len(sampled_memory), -1)

                # tem_done = [row[3] for row in sampled_memory]
                tem_not_done = [abs(row[3] - 1) for row in sampled_memory]
                tem_not_done = np.array(tem_not_done).reshape(len(sampled_memory), -1)
                tem_encoded_observation_next = [row[4] for row in sampled_memory]
                tem_encoded_observation_next = np.array(tem_encoded_observation_next).reshape(
                    len(sampled_memory), self.frame_size, -1
                )

                # print(self.target_dqn.predict(tem_encoded_observation_next))
                # print("---")
                # print(tf.reduce_max(self.target_dqn.predict(tem_encoded_observation_next), axis=1))
                tem_q_target_predicted = tf.reduce_max(self.target_dqn.predict(tem_encoded_observation_next), axis=1)[
                    :, tf.newaxis
                ]

                tem_x = tem_encoded_observation
                tem_x = np.array(tem_x).reshape(len(sampled_memory), self.frame_size, -1)
                tem_y = tem_action * (tem_reward + self.gamma * tem_not_done * tem_q_target_predicted)

                self.dqn.fit(tem_x, tem_y, batch_size=16, callbacks=[self.callback_mse_history])
                self.mse_his += self.callback_mse_history.losses
                self.learning_step_counter += 1

            # update target_dqn as dqn's parameter
            if self.learning_step_counter % self.C == 0 or terminated or truncated:
                self.target_dqn.set_weights(self.dqn.get_weights())

            # update
            observation = observation_next
            info = info_next
            self.pre_game_idx = self.cur_game_idx

            # ending
            if truncated or terminated:
                # self.owe_agent.action(observation, reward, terminated, truncated, info) # for rl agent final observation
                break

    def save_model(self, model_name):

        self.target_dqn.save(self._storing_path + model_name + ".keras")
        # save data
        # train_x = tf.stack(self.tournament_his["x"])
        # train_y = tf.stack(self.tournament_his["y"])
        # np.savetxt(self._storing_path + model_name + "_x.csv", train_x, delimiter=",")
        # np.savetxt(self._storing_path + model_name + "_y.csv", train_y, delimiter=",")

    def get_cash_graph(self, model_name, episode_line=True):
        """
        x axis: action performed count,
        y axis: cash amount
        vertical line: indicate the different episode
        """
        if not self.learning:
            print("This agent is not learning")
            raise
        x = list(range(len(self.cash_his)))
        plt.plot(x, self.cash_his, marker="o")
        plt.xlabel("Step")
        plt.ylabel("Cash")
        if episode_line:
            for episode_x in self.cash_episode_index:
                plt.axvline(x=episode_x, color="red")
            plt.savefig(self._storing_path + model_name + "_cash_Eline.png")
        else:
            plt.savefig(self._storing_path + model_name + "_cash.png")
        plt.cla()
        output_cash_df = pd.DataFrame({"cash": self.cash_his})
        output_cash_df.to_csv(self._storing_path + model_name + "_cash.csv")
        output_cash_episode_df = pd.DataFrame({"episode_index": self.cash_episode_index})
        output_cash_episode_df.to_csv(self._storing_path + model_name + "_cash_episode_idx.csv")

        game_list = []
        end_game_list = []
        for epi_idx, episode_x in enumerate(self.cash_episode_index):
            if epi_idx != 0:
                game_list.append(epi_idx)
                end_game_list.append(self.cash_his[episode_x - 1])
        game_list.append(game_list[-1] + 1)
        end_game_list.append(self.cash_his[-1])
        plt.scatter(game_list, end_game_list, marker="o")
        plt.xlabel("Game")
        plt.ylabel("Cash")
        plt.grid()
        plt.savefig(self._storing_path + model_name + "_game_cash.png")
        plt.cla()

    def get_mse_graph(self, model_name, episode_line=True):
        """
        x axis: action performed count,
        y axis: mse
        vertical line: indicate the different episode
        """
        if not self.learning:
            print("This agent is not learning")
            raise
        x = list(range(len(self.mse_his)))
        plt.plot(x, self.mse_his, marker="o")
        plt.xlabel("Step")
        plt.ylabel("MSE")
        if episode_line:
            for episode_x in self.mse_episode_index:
                plt.axvline(x=episode_x, color="red")
            plt.savefig(self._storing_path + model_name + "_mse_Eline.png")
        else:
            plt.savefig(self._storing_path + model_name + "_mse.png")
        plt.cla()
        output_mse_df = pd.DataFrame({"mse": self.mse_his})
        output_mse_df.to_csv(self._storing_path + model_name + "_mse.csv")
        output_mse_episode_df = pd.DataFrame({"episode_index": self.mse_episode_index})
        output_mse_episode_df.to_csv(self._storing_path + model_name + "_mse_episode_idx.csv")

    def novelty_detection(self):
        return 0


class ReplayMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = deque([])

    def push(self, encoded_observation, action, reward, done, encoded_observation_next):
        experience = [encoded_observation, action, reward, done, encoded_observation_next]
        if len(self.memory) == self.capacity:
            self.memory.popleft()

        self.memory.append(experience)

    def sample(self, batch_size):
        if len(self.memory) > batch_size:
            return random.sample(self.memory, batch_size)
        else:
            return self.memory

    def can_sample(self):
        return len(self.memory) != 0
