from .action1 import Action1
from .card_dist_high import CardDistHigh
from .card_dist_low import CardDistLow
from .card1 import Card1
from .environment1 import Environment1
from .environment2 import Environment2
from .agent1 import Agent1
from .agent2 import Agent2
from .agent3 import Agent3
from .event1 import Event1
# from .rule1 import Rule1
from .rule2 import Rule2
from .rule3 import Rule3
from .event2 import Event2
from .rule4 import Rule4
from .card2 import Card2
from .card3 import Card3

NOVELTY_LIST = [cls for cls in locals().values() if isinstance(cls, type)]
NOVELTY_LIST.append('RANDOM')