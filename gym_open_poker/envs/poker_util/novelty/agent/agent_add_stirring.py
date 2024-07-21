import gym
import sys
import logging
from agent import Agent
from gym_open_poker.envs.poker_util.agents import agent_stirring

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.novelty.agent.agent_add_stirring")


class AddAgentStirring(gym.Wrapper):
    """
    This novelty introduces {add_player_number} more agent_stirring in the tournament.

    """

    def __init__(self, env, add_player_number=2):

        super().__init__(env)

        # add one new player
        last_player_index = env.number_of_players

        for p_idx in range(1, add_player_number + 1):
            new_player_methods = getattr(sys.modules[__name__], "agent_stirring")
            env.player_decision_agents["player_" + str(last_player_index + p_idx)] = Agent(
                **new_player_methods.decision_agent_methods
            )

        logger.debug(f"Novelty! {add_player_number} more agent_conservative joined in this tournament.")

        # modify number_of_players
        env.number_of_players += add_player_number
