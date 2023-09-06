from gym.envs.registration import register

register(
    id="open_poker/OpenPoker-v0",
    entry_point="open_poker.envs:OpenPokerEnv",
)
