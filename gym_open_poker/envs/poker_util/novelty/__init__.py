from gym_open_poker.envs.poker_util.novelty.action1 import Action1
from gym_open_poker.envs.poker_util.novelty.card_dist_high import CardDistHigh
from gym_open_poker.envs.poker_util.novelty.card_dist_low import CardDistLow
from gym_open_poker.envs.poker_util.novelty.card1 import Card1
from gym_open_poker.envs.poker_util.novelty.environment1 import Environment1
from gym_open_poker.envs.poker_util.novelty.environment2 import Environment2
from gym_open_poker.envs.poker_util.novelty.agent1 import Agent1
from gym_open_poker.envs.poker_util.novelty.agent2 import Agent2
from gym_open_poker.envs.poker_util.novelty.agent3 import Agent3
from gym_open_poker.envs.poker_util.novelty.event1 import Event1

# from .rule1 import Rule1
from gym_open_poker.envs.poker_util.novelty.rule2 import Rule2
from gym_open_poker.envs.poker_util.novelty.rule3 import Rule3
from gym_open_poker.envs.poker_util.novelty.event2 import Event2
from gym_open_poker.envs.poker_util.novelty.rule4 import Rule4
from gym_open_poker.envs.poker_util.novelty.card2 import Card2
from gym_open_poker.envs.poker_util.novelty.card3 import Card3

NOVELTY_LIST = [cls for cls in locals().values() if isinstance(cls, type)]
# NOVELTY_LIST.append("RANDOM")

__all__ = [
    "Action1",
    "CardDistHigh",
    "CardDistLow",
    "Card1",
    "Environment1",
    "Environment2",
    "Agent1",
    "Agent2",
    "Agent3",
    "Event1",
    "Rule2",
    "Rule3",
    "Event2",
    "Rule4",
    "Card2",
    "Card3",
]
