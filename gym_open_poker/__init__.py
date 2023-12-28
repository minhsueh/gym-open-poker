from gym.envs.registration import register

register(
    id="gym_open_poker/OpenPoker-v0",
    entry_point="gym_open_poker.envs:OpenPokerEnv",
)
