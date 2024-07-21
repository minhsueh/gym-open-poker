import gym
import sys

import gym_open_poker
from action import Action

# import action_choices
from action_choices import call, all_in, raise_bet, bet, check, fold
from phase import Phase
from flag_config import flag_config_dict
from player import Player


import logging

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.novelty.action.action_hierarchy")


class ActionHierarchy(gym.Wrapper):
    """
    This novelty alters the default novelty hierarchy. The default novelty hierarchy is used when a player performs an
     allowable action. The default novelty hierarchy follows: fold -> check -> call -> bet -> raise_bet -> all_in.

    """

    def __init__(self, env):

        super().__init__(env)

        sys.modules["player"].Player._action_validator = getattr(sys.modules[__name__], "_alter_action_validator")


def _alter_action_validator(self, action, allowable_actions):
    """
    Check if the agent inputs valid action. If not, set a default action for the player.
    The default action hierarchy involve: fold -> check -> call -> bet -> raise_bet -> all_in
    The default action is set:
    1. Choose the action with the highest priority but lower than the original action.
    For example, if allowable_actions = [fold, check, bet], but player's orginal action is raise_bet, then
    the modified_action is bet.

    2. If no allowable actions are lower than the original action, choose the most conservative one.
    For example, if allowable_actions = [call, raise_bet], but the player's original action is check, then
    the modified_action is call. Note: This situation will occur when novelty is injected. Or folding is usually allowed.


    Args:
        action(function from action_choices): the action got from gym user
        allowable_actions(set)
    Returns:
        action_function:

    """
    if len(allowable_actions) == 0 or action in allowable_actions:
        # This might happen if there is conflict in composite novelty
        # In this case, just return the original action because it will fail no matter what action
        return action

    default_action_hierarchy = [
        Action.FOLD,
        Action.CHECK,
        Action.CALL,
        Action.BET,
        Action.RAISE_BET,
        Action.ALL_IN,
    ]
    # novelty!
    default_action_hierarchy = default_action_hierarchy[::-1]

    original_idx = default_action_hierarchy.index(action)

    for action_idx in range(original_idx, 6):
        if default_action_hierarchy[action_idx] in allowable_actions:
            modified_action = default_action_hierarchy[action_idx]
            logger.debug(
                f"Novelty! Action hierarchy has been changed!"
                f"{self.player_name} try to {action.name} which is invalid, the system automatically "
                f"modify to {modified_action.name}"
            )
            return modified_action

    for action_idx in range(original_idx, -1, -1):
        if default_action_hierarchy[action_idx] in allowable_actions:
            modified_action = default_action_hierarchy[action_idx]
            logger.debug(
                f"{self.player_name} try to {action.name} which is invalid, the system automatically "
                f"modify to {modified_action.name}"
            )
            return modified_action
    raise  # it is impossible to get here
