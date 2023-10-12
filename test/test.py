import gym
import open_poker

from open_poker.envs.poker_util.agents import example_agent_check_fold, example_agent_random, example_agent_call, example_agent_raise_bet
from open_poker.envs.poker_util.agents import agent_call_AJ, agent_raise_AJ, agent_call_toppair_AJ, agent_raise_aggressive_AJ
from open_poker.envs.poker_util.agents import agent_call_AJ_flop, background_agent_v1, background_agent_v2, dump_agent


# background_agents_list = [example_agent_call, example_agent_call, example_agent_call]
background_agents_list = [dump_agent, dump_agent, dump_agent, dump_agent]

SLEEP = False

env = gym.make("open_poker/OpenPoker-v0", background_agents_list=background_agents_list, render_mode='human', sleep_mode=SLEEP)
observation, info = env.reset(seed=42)
print(observation)
"""
for _ in range(1000):
    action = env.action_space.sample()
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()

print('--------------------------')
print('PRE-FLOP')
observation, reward, terminated, truncated, info = env.step(0)
print(observation)

print('--------------------------')
print('FLOP')
observation, reward, terminated, truncated, info = env.step(1)
print(observation)

print('--------------------------')
print('TURN')
observation, reward, terminated, truncated, info = env.step(1)
print(observation)

print('--------------------------')
print('RIVER')
observation, reward, terminated, truncated, info = env.step(1)
print(observation)

"""
while(True):
    print('--------------------------')
    print('Enter your action:')
    user_action = int(input())
    print('---------')
    observation, reward, terminated, truncated, info = env.step(user_action)
    print(observation)
    if terminated or truncated:
        print('LOSTTTTTTTTTTT!')
        break



# env.close()