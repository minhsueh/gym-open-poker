


import gym
from gym import spaces
import pygame
import numpy as np
import logging

import open_poker.envs.gnome_poker 
import open_poker.envs.poker_util as poker_util

import sys, os
sys.path.append(os.path.dirname(poker_util .__file__)) 

from open_poker.envs.poker_util.agent import Agent

from open_poker.envs.poker_util.phase import Phase
from open_poker.envs.poker_util.initialize_game_elements import initialize_game_element
from open_poker.envs.poker_util.tournament_status import TournamentStatus
from open_poker.envs.poker_util.logging_info import log_file_create

from open_poker.envs.poker_util.agents import example_agent_check_fold, example_agent_random, example_agent_call, example_agent_raise_bet
from open_poker.envs.poker_util.agents import agent_call_AJ, agent_raise_AJ, agent_call_toppair_AJ, agent_raise_aggressive_AJ
from open_poker.envs.poker_util.agents import agent_call_AJ_flop, background_agent_v1, background_agent_v2


logger = log_file_create('./test.log')
# logger = logging.getLogger('open_poker.envs.poker_util.logging_info')

logger.debug("Let's get started!!!!")


class OpenPokerEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}
    """
    ----------------------------------------
    Poker introduction: 
    There are (number_of_players) games in a tournament. Specifically, the dealer's position will change after each hand(game). 
    One tournament is finished when the dealer position is repeated to the person who already did a dealer.

    In each of the games, there are four rounds/bets(pre-flop, flop, turn, river)

    In short, the terms are used in this implementation: 
    A "tournament" contains (number_of_players) "games"; each "game" contains four "rounds."

    ----------------------------------------
    Limit Texas Hold'em poker 
    Reference:
    1. https://poker.fandom.com/wiki/Fixed-limit
    2. https://www.pokerlistings.com/limit-texas-holdem
    3. https://www.winamax.fr/en/poker-school_rules_limit-texas-hold--em#:~:text=Limit%20Texas%20Hold'em%20is%20played%20Limit%3A%20the%20amount%20of,%2C%20final%20raise%20(3).
    
    1. betting rules: 
    In Hold 'em and Omaha, there are four betting rounds: preflop, flop, turn, and river. 
    If a game with four betting rounds is structured as fixed-limit with two bet sizes, 
    the small bet size refers to the betting preflop and on the flop, 
    while the big bet size refers to the betting on the turn and river.



    For example, if it is "2/4" game, small blind = $1, big blind = $4.
    (1) In the betting preflop and on the flop, only constant raise is allowed: $2(bet) -> $4(raise) -> $6(re-raise) -> $8(final-raise) -> $8
    (2) In the betting on the turn and river, only constant raise is allowed: $4(bet) -> $8(raise) -> $12(re-raise) -> $16(final-raise) -> $8


    



    """

    def __init__(self, 
            background_agents_list: list=[], 
 



            max_raise_count=3,
            small_bet=2,
            big_bet=4,
            render_mode=None):
        """
        PARAMS:
            number_of_players(int): The number of player join the game.
            background_agent(list): a list of the background agent.

        """
        # general poker rules

        self.background_agents_list = background_agents_list
        self.number_of_players = len(background_agents_list) + 1 

        self.small_bet = small_bet
        self.big_bet = big_bet
        self.small_blind = small_bet//2
        self.big_blind = small_bet



        # Limit Texas Hold'em poker rules
        self.max_raise_limit = max_raise_count

        



        # restrictions
        self.bankroll_limit = 999.0



        # gnome poker variables
        self.dealer_position = 0
        self.raise_count = 0
        self.cur_phase = Phase.PRE_FLOP
        self.tournament_status = TournamentStatus.TRUNCATED





        
        


        # Global level: Player's bankroll. spaces.Box. size = (number_of_players,)  
        # Tournament level info: dealer's position, player's position
        # Game level info: community card, hand
        # Round level info: spaces.Box. size = (number_of_players,)  
        #   each value indicate the bet in previous round


        self.observation_space = spaces.Dict(
            {
                "bankroll": spaces.Box(-1.0, self.bankroll_limit, shape=(self.number_of_players,), dtype=np.float32),
                "position": spaces.Box(0, self.number_of_players, shape=(2,), dtype=int),
                "hole_cards": spaces.Box(1, 52, shape=(5,), dtype=int), 
                "community_card": spaces.Box(1, 52, shape=(5,), dtype=int), 
                "bet": spaces.Box(-1.0, self.bankroll_limit, shape=(self.number_of_players,), dtype=np.float32)
            }
        )

        # We have 4 actions, corresponding to "call", "raise", "check", "fold"
        self.action_space = spaces.Discrete(4)

        """
        TBM
        """
        self._action_decoder = {
            0: "funciton call",
            1: "function raise",
            2: "function check",
            3: "funciton fold",
        }

        """
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        
        self.window = None
        self.clock = None
        """


    def _phase_decoder(self):
        phase_decoder_dict = {
            0: 'pre-flop',
            1: 'flop',
            2: 'turn',
            3: 'river'
        }



    def _get_bankroll_info(self):
        # size = self.number_of_players
        pass

    def _get_position_info(self):
        # [dealer position, player_position]
        pass

    def _get_hole_cards_info(self):
        # [card1, card2]
        pass

    def _get_community_card_info(self):
        # [flop1. flop2, flop3, turn, river]
        pass

    def _get_bet_info(self):
        # size = self.number_of_players
        pass


    def _get_obs(self):
        return {
            "bankroll": self._get_bankroll_info(),
            "position": self._get_position_info(),
            "hole_cards": self._get_hole_cards_info(),
            "community_card": self._get_community_card_info(),
            "bet": self._get_bet_info()
        }

    def set_up_board(self, player_decision_agents):
        """
        The function to set up game elements`
        :param player_decision_agents: dictionary of player name and its corresponding agent
        :return: game elements
        :rtype: dict
        """
        return initialize_game_element(player_decision_agents)

    def _get_info(self):

        """
        info = get action mask
        """
        return(dict())
        

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        player_decision_agents = dict()
        player_decision_agents['player_raise'] = Agent(**example_agent_raise_bet.decision_agent_methods)
        player_decision_agents['player_call'] = Agent(**example_agent_call.decision_agent_methods)
        player_decision_agents['player_random'] = Agent(**example_agent_random.decision_agent_methods)

        self.board = self.set_up_board(player_decision_agents)

        print(self.board.keys())

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        """

        """

        # action_decode:


        # check player status, lost, blind, and current_cash -> actions mask or terminated/truncated
        # info = aciton_mask


        # get reward


        # get observation


        







        if condition:
            # everybody has called or checked
            self.cur_phase = (self.cur_phase + 1) % 4






        return observation, reward, terminated, False, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (
            self.window_size / self.size
        )  # The size of a single grid square in pixels

        # First we draw the target
        pygame.draw.rect(
            canvas,
            (255, 0, 0),
            pygame.Rect(
                pix_square_size * self._target_location,
                (pix_square_size, pix_square_size),
            ),
        )
        # Now we draw the agent
        pygame.draw.circle(
            canvas,
            (0, 0, 255),
            (self._agent_location + 0.5) * pix_square_size,
            pix_square_size / 3,
        )

        # Finally, add some gridlines
        for x in range(self.size + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=3,
            )
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=3,
            )

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        pass
        """
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
        """
