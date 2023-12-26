import gym
import open_poker
from open_poker.wrappers import CardDistHigh, CardDistLow
import yaml



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

env = CardDistHigh(gym.make("open_poker/OpenPoker-v0", **config_dict))
# env = CardDistLow(gym.make("open_poker/OpenPoker-v0", **config_dict))
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
        print('meet termination condition! Over!')
        break
    if terminated:
        if observation['player_status'][observation['position'][1]] == 1:
            print('WINNNN!')
        else:
            print('LOST!')
        break



# env.close()