


import gym
from gym import spaces
import pygame
import numpy as np
import logging
import math
import time

import open_poker.envs.gnome_poker 
import open_poker.envs.poker_util as poker_util

import sys, os
sys.path.append(os.path.dirname(poker_util .__file__)) 

from open_poker.envs.poker_util.agent import Agent

from open_poker.envs.poker_util.phase import Phase
from open_poker.envs.poker_util.action_choices import (check, bet, raise_bet, fold, call)
from open_poker.envs.poker_util.initialize_game_elements import initialize_game_element
from open_poker.envs.poker_util.tournament_status import TournamentStatus
from open_poker.envs.poker_util.logging_info import log_file_create
from open_poker.envs.poker_util.flag_config import flag_config_dict
from open_poker.envs.poker_util.dealer import _get_players_last_move_list_string

from open_poker.envs.poker_util.agents import example_agent_check_fold, example_agent_random, example_agent_call, example_agent_raise_bet
from open_poker.envs.poker_util.agents import agent_call_AJ, agent_raise_AJ, agent_call_toppair_AJ, agent_raise_aggressive_AJ
from open_poker.envs.poker_util.agents import agent_call_AJ_flop, background_agent_v1, background_agent_v2

from phase import Phase
from action import Action
import action_choices
from card import Card
import dealer


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
            background_agents_list: list=[example_agent_raise_bet, example_agent_raise_bet, example_agent_raise_bet], 
 



            max_raise_count=3,
            small_bet=2,
            big_bet=4,
            render_mode=None,
            size=5):
        """
        PARAMS:
            number_of_players(int): The number of player join the game.
            background_agent(list): a list of the background agent.

        """
        # general poker rules

        self.background_agents_list = background_agents_list
        self.number_of_players = len(background_agents_list) + 1 

        self.player_decision_agents = dict()
        self.player_decision_agents['player_1'] = 'player_1'
        for player_idx, player in enumerate(background_agents_list):
            self.player_decision_agents['player_' + str(player_idx+2)] = Agent(**player.decision_agent_methods)
        logger.debug('Player_1 is assign as code user.')

        self.small_bet = small_bet
        self.big_bet = big_bet
        self.small_blind = small_bet//2
        self.big_blind = small_bet



        # Limit Texas Hold'em poker rules
        self.max_raise_limit = max_raise_count

        



        # restrictions
        self.bankroll_limit = 1500



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
                "player_status": spaces.Box(0, 1, shape=(self.number_of_players,), dtype=np.int64),
                "bankroll": spaces.Box(-1, self.bankroll_limit, shape=(self.number_of_players,), dtype=np.int64),
                "position": spaces.Box(0, self.number_of_players-1, shape=(2,), dtype=np.int64),
                "hole_cards": spaces.Box(1, 52, shape=(2,), dtype=np.int64), 
                "community_card": spaces.Box(-1, 52, shape=(5,), dtype=np.int64), 
                "bet": spaces.Box(-1, 4, shape=(self.number_of_players,), dtype=np.int64)
            }
        )

        # We have 7 actions, corresponding to "call", "bet", "raise", "check", "fold"
        self.action_space = spaces.Discrete(5, start=0)

        """
        TBM
        """
        self._action_encoder = {
            'LOSE': -1,
            'NONE': -1,
            'CALL': 0,
            'BET': 1,
            'RAISE_BET': 2,
            'CHECK': 3,
            'FOLD': 4
        }





        # visulaization
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """

        
        self.window = None
        self.clock = None
        self.window_width = 1000  # The width of the PyGame window
        self.window_height = 500  # The height of the PyGame window
        
    def _action_decoder(self, player, action):
        """
        Decode integer action into function and the correspongind parameters
        Args:
            player(Player): the Player object representing gym user
            action(int): the action got from gym user
        Returns:
            action_function
            parameters
        """

        current_phase = self.game_elements['cur_phase']

        parameters = dict()
        parameters['player'] = player
        parameters['current_gameboard'] = self.game_elements



        if action == 0:
            action_function = action_choices.call
        elif action == 1:
            action_function = action_choices.bet
            if current_phase in [Phase.PRE_FLOP, Phase.FLOP]:
                parameters['first_bet'] = self.game_elements['small_bet']
            elif current_phase in [Phase.TURN, Phase.RIVER]:
                parameters['first_bet'] = self.game_elements['big_bet']
            else:
                raise

        elif action == 2:
            action_function = action_choices.raise_bet
            if current_phase in [Phase.PRE_FLOP, Phase.FLOP]:
                parameters['amount_to_raise'] = self.game_elements['small_bet']
            elif current_phase in [Phase.TURN, Phase.RIVER]:
                parameters['amount_to_raise'] = self.game_elements['big_bet']
            else:
                raise
        elif action == 3:
            action_function = action_choices.check
        elif action == 4:
            action_function = action_choices.fold
        else:
            raise
        return(action_function, parameters)


    def _card_decoder(self, card):
        """ decode Card object into int
        Args:
            card: Card object

        Returns:
            card_code:int (1~52)

        Raises:


        """
        assert isinstance(card, Card)
        if card.suit == 'spade':
            suit_idx = 0
        elif card.suit == 'heart':
            suit_idx = 1
        elif card.suit == 'diamond':
            suit_idx = 2
        elif card.suit == 'club':
            suit_idx = 3
        else:
            raise ('please check card.suit, current value = ' + card.suit)

        return(int(suit_idx * 13 + card.number))

    def _phase_decoder(self, phase):
        """ decode Phase object into int
        Args:
            phase: Phase object

        Returns:
            phase_idx:int 

        Raises:


        """
        assert isinstance(phase, Phase)
        
        phase_idx = int(phase.value)

        return(phase_idx)

    def _phase_encoder(self, phase_idx):
        """ decode Phase object into int
        Args:
            phase_idx: int

        Returns:
            phase:Phase object

        Raises:


        """
        assert isinstance(phase_idx, int)

        phase = Phase(phase_idx)

        return(phase)



    def _get_status_and_bankroll_info(self):
        # size = self.number_of_players
        player_status_list = []
        bankroll_list = []
        for player in self.game_elements['players']:
            if player.status == 'lost':
                player_status_list.append(0)
                bankroll_list.append(-1)
            else:
                player_status_list.append(1)
                bankroll_list.append(player.current_cash)
        return(np.array(player_status_list, dtype=np.int64), np.array(bankroll_list, dtype=np.int64))

    def _get_position_info(self):
        # [dealer position, player_position]
        player_position_idx = -1
        for idx, player in enumerate(self.game_elements['players']):
            if player.player_name == 'player_1':
                player_position_idx = idx
                break
        if player_position_idx == -1:
            raise ("player_position_idx should not be -1, please check _get_position_info")

        return(np.array([self.game_elements['board'].dealer_position, player_position_idx], dtype=np.int64))


    def _get_hole_cards_info(self):
        # [card1, card2]
        hole_cards = []
        for idx, player in enumerate(self.game_elements['players']):
            if player.player_name == 'player_1':
                hole_cards = player.hole_cards
                break
        if not hole_cards:
            raise ("player's hole_cards should not be empty, please check _get_hole_cards_info")

        card_list = []
        for card in hole_cards:
            card_list.append(self._card_decoder(card))
        return(np.array(card_list, dtype=np.int64))

    def _get_community_card_info(self):
        # [flop1. flop2, flop3, turn, river]
        current_community_card = []
        for card in self.game_elements['board'].community_cards:
            current_community_card.append(self._card_decoder(card))

        return(np.array(current_community_card + [-1] * (5 - len(current_community_card)), dtype=np.int64))

    def _get_bet_info(self):
        # size = self.number_of_players
        players_last_move_list_encode = []
        for move in self.game_elements['players_last_move_list']:
            if move in ['SMALL_BLIND', 'BIG_BLIND']:
                # which mean they didn't move
                players_last_move_list_encode.append(-1)
            else:
                players_last_move_list_encode.append(self._action_encoder[move])


        return(np.array(players_last_move_list_encode, dtype=np.int64))


    def _get_obs(self):
        player_status, bankroll = self._get_status_and_bankroll_info()
        return {
            "player_status": player_status,
            "bankroll": bankroll,
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
        # We have 5 actions, corresponding to 
        'CALL': 0,
        'BET': 1,
        'RAISE_BET': 2,
        'CHECK': 3,
        'FOLD': 4

        for idx, player in enumerate(self.game_elements['players']):
            if player.player_name == 'player_1' and idx == ((self.game_elements['dealer_position']+1)%self.game_elements['number_of_players']):
                # small blind
                return()
            elif player.player_name == 'player_1' and idx == ((self.game_elements['dealer_position']+2)%self.game_elements['number_of_players']):
                # big blind
        return([])
        """
        output_info_dict = dict()


        # action_masks
        player_1 = self.game_elements['players_dict']['player_1']
        if player_1.status == 'lost':
            raise

        if self.game_elements['cur_phase'] == Phase.PRE_FLOP:
            allowable_actions = player_1.compute_allowable_pre_flop_actions(self.game_elements)
        elif self.game_elements['cur_phase'] == Phase.FLOP:
            allowable_actions = player_1.compute_allowable_flop_actions(self.game_elements)
        elif self.game_elements['cur_phase'] == Phase.TURN:
            allowable_actions = player_1.compute_allowable_turn_actions(self.game_elements)
        elif self.game_elements['cur_phase'] == Phase.RIVER:
            allowable_actions = player_1.compute_allowable_river_actions(self.game_elements)
        else:
            raise

        allowable_string = [action.__name__ for action in allowable_actions]
        action_masks = []
        for action in ['call', 'bet', 'raise_bet', 'check', 'fold']:
            if action in allowable_string:
                action_masks.append(1)
            else:
                action_masks.append(0)



        # return
        output_info_dict['action_masks'] = np.array(action_masks)

        return(output_info_dict)





        

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random



        

        self.game_elements = self.set_up_board(self.player_decision_agents)

        if self.render_mode == "human":
            self.render()
            time.sleep(1)

        super().reset(seed=seed)
        np.random.seed(seed)
        np.random.shuffle(self.game_elements['players'])
        np.random.shuffle(self.game_elements['deck'])

        player_seq = ""
        for idx, player in enumerate(self.game_elements['players']):
            player.position = idx
            player_seq += player.player_name + ' -> '
        logger.debug(player_seq[:-4])



        # Deal the hole card
        dealer.check_and_deal_hole_cards(self.game_elements)

        # force_small_big_blind_bet
        dealer.force_small_big_blind_bet(self.game_elements)

        # initialize_betting
        dealer.initialize_betting(self.game_elements)



        # start perform pre-flop betting
        if self.game_elements['players'][self.game_elements['current_betting_idx']].player_name != 'player_1':
            self._betting()


        observation = self._get_obs()
        info = self._get_info()


        if self.render_mode == "human":
            self._render_frame()
            time.sleep(1)

        return observation, info

    def step(self, action):
        """
        either round ending or continue bedding




        pre-flop:
            deal hole card
            force_small_big_blind_bet
            initialize_betting
            bet
            conclude_round
        flop:
            initialize_betting
            bet
            conclude_round
        turn:
            initialize_betting
            bet
            conclude_round
        river:
            initialize_betting
            bet
            conclude_round

            

        Args:
            
        Returns:

        Raises:
        

        """
        # get the player object
        player = None
        for player_idx, player in enumerate(self.game_elements['players']):
            if player.player_name == 'player_1':
                break
        assert player is not None
        print(self.game_elements['current_bet_count'])

        execute_res = self.execute_player_1_action(player, action)
        if execute_res:
            return(execute_res[0])

        while(True):
            # continue betting
            if not dealer.check_betting_over(self.game_elements):
                 # continue betting
                is_over = self._betting()
                if not is_over and self.game_elements['players_last_move_list'][player_idx] != 'FOLD':
                    observation = self._get_obs()
                    reward = 0
                    terminated = False
                    truncated = False
                    info = self._get_info()
                    if self.render_mode == "human":
                        self.render()
                        time.sleep(1)
                    return observation, reward, terminated, truncated, info
                elif not is_over:
                    # player_1 fold
                    continue
            else:

                dealer.conclude_round(self.game_elements)
                # The betting is over, change the phase
                new_phase = dealer.change_phase(self.game_elements)

                # 
                if new_phase != Phase.PRE_FLOP:
                    # deal community card
                    dealer.check_and_deal_community_card(self.game_elements)

                    # initialize_betting
                    dealer.initialize_betting(self.game_elements)

                    # betting
                    self._betting()
                    if self.render_mode == "human":
                        self.render()
                        time.sleep(1)
                    if self.game_elements['players_last_move_list'][player_idx] != 'FOLD':
                        return self._get_obs(), 0, False, False, self._get_info()


                elif new_phase == Phase.PRE_FLOP or current_gameboard['early_stop']:
                    # conclude this game
                    dealer.find_winner(self.game_elements)
            
                    dealer.log_best_card(self.game_elements)
                    dealer.log_ranking(self.game_elements)
                    is_end = dealer.conclude_game(self.game_elements)

                    if is_end:
                        if self.render_mode == "human":
                            self.render()
                        return self._get_obs(), 0, True, False, self._get_info()

                    # srart the new game
                    # Deal the hole card
                    dealer.check_and_deal_hole_cards(self.game_elements)

                    # force_small_big_blind_bet
                    dealer.force_small_big_blind_bet(self.game_elements)

                    # initialize_betting
                    dealer.initialize_betting(self.game_elements)
  
        if self.render_mode == "human":
            self.render()



       
    def execute_player_1_action(self, player, action):
        # action_decode:
        action_to_execute, parameters = self._action_decoder(player, action)

        # execute player_1's action
        code = player._execute_action(action_to_execute, parameters, self.game_elements)
        last_move = action_to_execute.__name__.upper()
        current_betting_idx = self.game_elements['current_betting_idx']
        total_number_of_players = self.game_elements['total_number_of_players']

        if code == flag_config_dict['failure_code']:
            logger.debug(f'Board: {player.player_name} tries an invalid move, assign to lost')
            self.game_elements['players_last_move_list'][current_betting_idx] = 'LOSE'
            player.assign_status(self.game_elements, 'lost')
            current_betting_idx = (current_betting_idx + 1) % total_number_of_players
            self.game_elements['current_betting_idx'] = current_betting_idx
            logger.debug('The current players_last_move_list is: ' + str(_get_players_last_move_list_string(self.game_elements)))

            if self.render_mode == "human":
                self.render()
            return [self._get_obs(), -100, True, False, self._get_info()]

        
        self.game_elements['players_last_move_list'][current_betting_idx] = last_move
        logger.debug(f'Board: {player.player_name} do the {last_move}')
        dealer.print_single_player_cash_info(self.game_elements, player.player_name)
        current_betting_idx = (current_betting_idx + 1) % total_number_of_players
        self.game_elements['current_betting_idx'] = current_betting_idx
        logger.debug('The current players_last_move_list is: ' + str(_get_players_last_move_list_string(self.game_elements)))
        return([])

    
    
    def _betting(self):
        """ 
        use 
            current_bet_count, 
            current_raise_count, 
            current_betting_idx, 
            dealer_position,
            num_active_player_on_table


        when to stop betting:
            1. all players check/call
            2. reach max bet and raise
            3. num_active_player_on_table == 1 -> winner -> _concluded_game

        
        Args:
            
        Returns:

        Raises:
        """
        logger.debug('------------Non-player_1 players start to bet. ------------')

        # start from current_betting_idx: current_betting_idx + total_number_of_players
        # record every action
        # determine stop betting or return to player_1
        current_betting_idx = self.game_elements['current_betting_idx']
        total_number_of_players = self.game_elements['total_number_of_players']
        while(not dealer.check_betting_over(self.game_elements)):
            if self.render_mode == "human":
                self.render()
                time.sleep(1)
            player = self.game_elements['players'][current_betting_idx]
            if player.status != 'lose':
                logger.debug(player.player_name + ' start to move.')
                if player.player_name == 'player_1' and self.game_elements['players_last_move_list'][current_betting_idx] != 'FOLD':
                    # this is gym user, return and wait for the next step
                    return(False) # meaning the betting is still continue
                elif player.player_name == 'player_1':
                    current_betting_idx = (current_betting_idx + 1) % total_number_of_players
                    self.game_elements['current_betting_idx'] = current_betting_idx
                    continue

                else:
                    code, last_move  = self._get_background_agent_action(player, self.game_elements['cur_phase'])
                    if code == flag_config_dict['failure_code']:
                        logger.debug(f'Board: {player.player_name} tries an invalid move, assign to lost')
                        self.game_elements['players_last_move_list'][current_betting_idx] = 'LOSE'
                        player.assign_status(self.game_elements, 'lost')
                        current_betting_idx = (current_betting_idx + 1) % total_number_of_players
                        self.game_elements['current_betting_idx'] = current_betting_idx
                        logger.debug('The current players_last_move_list is: ' + str(_get_players_last_move_list_string(self.game_elements)))
                        continue
                    self.game_elements['players_last_move_list'][current_betting_idx] = last_move
                    logger.debug(f'Board: {player.player_name} do the {last_move}')
                    dealer.print_single_player_cash_info(self.game_elements, player.player_name)


            current_betting_idx = (current_betting_idx + 1) % total_number_of_players
            self.game_elements['current_betting_idx'] = current_betting_idx
            logger.debug('The current players_last_move_list is: ' + str(_get_players_last_move_list_string(self.game_elements)))
        logger.debug('This betting is over.')
        if self.render_mode == "human":
            self.render()
            time.sleep(1)
        return(True) # meaning the betting is over

        
    
    def _get_background_agent_action(self, player, phase):
        """ 
        use 
            self.game_elements['player_last_move']


        when to stop betting:
            1. all players check/call
            2. reach max bet and raise
            3. num_active_player_on_table == 1 -> winner -> _concluded_game

        
        Args:
            player(Player)
            phase(Phase)
            
        Returns:

        Raises:
        """
        if phase == Phase.PRE_FLOP:
            code = player.make_pre_flop_moves(self.game_elements)
        elif phase == Phase.FLOP:
            code = player.make_flop_moves(self.game_elements)
        elif phase == Phase.TURN:
            code = player.make_turn_moves(self.game_elements)
        elif phase == Phase.RIVER:
            code = player.make_river_moves(self.game_elements)
        else:
            raise('This phase is invalid, current = ' + str(phase))


        player_last_move = self.game_elements['player_last_move']

        if player_last_move is None:
            raise ('player_last_move is wrong. please check')


        self.game_elements['player_last_move'] = None

        return(code, player_last_move.upper())





    def render(self):
        if self.render_mode == "human":
            return self._render_frame()


    def _render_frame(self):
        """
        ellipse shape
        pot
            main pot
            side pot
        dealer 
        players
            status
            card
            money


        """
        suit_map = {
            'spade': 'S',
            'heart': 'H',
            'diamond': 'D',
            'club': 'C'
        }

        number_map = {i: str(i) for i in range(2, 10)}
        number_map[1] = 'A'
        number_map[10] = 'T'
        number_map[11] = 'J'
        number_map[12] = 'Q'
        number_map[13] = 'K'



        pygame.init()
        pygame.display.init()
        self.window = pygame.display.set_mode((self.window_width, self.window_height))

        background_color = (0, 0, 0)
        text_color = (255, 255, 255)

        self.window.fill(background_color)
        pygame.display.flip()



        # board
        board_color = (39, 99, 55)
        
        board_b = self.window_height*3.5/5
        board_a = self.window_width*3.5/5
        player_info_a = self.window_width*4.5/5
        player_info_b = self.window_height*4.5/5
        card_info_a = self.window_width*2.5/5
        card_info_b = self.window_height*2.5/5
        line_spacing = self.window_height/25
        board_center_x = self.window_width/2
        board_center_y = self.window_height/2
        board_x = board_center_x - board_a/2
        board_y = board_center_y - board_b/2
        card_img_height = board_b //6
        card_img_width = board_a //12
        card_spacing = card_img_width//10
        community_card_x = board_center_x - card_spacing*2 - card_img_width*5/2
        community_card_y = board_center_y - card_img_height/2
        action_box_height = board_b //15
        action_box_width = board_a //12
        action_box_spacing = card_spacing
        action_box_x = self.window_width*8.5/10
        action_box_y = self.window_height*2//3
        game_index_box_x = self.window_width/10
        game_index_box_y = self.window_height/10


        def get_ellipse_position(a, b, degree, type = 'player_info'):
            """
            ref: https://math.stackexchange.com/questions/22064/calculating-a-point-that-lies-on-an-ellipse-given-an-angle
            Args:
                a(float): major axis 
                b(float): minor axis
                degree(float): the angle between point and x axis
                type(str): 'player_info' or 'card_info'

            Returns:
                x, y
            """
            assert type in ['player_info', 'card_info']  
            if type == 'player_info':
                return(board_center_x - a*math.cos(degree), board_center_y - b*math.sin(degree))
            elif type == 'card_info':
                return(board_center_x - a*math.cos(degree) - card_img_width, board_center_y - b*math.sin(degree) - card_img_height/2)
            else:
                raise

        def get_img_name(card):
            """
            Args:
                card(Card)

            Returns:
                img_name(str)
            """

            suit_map = {
                'spade': 'S',
                'heart': 'H',
                'diamond': 'D',
                'club': 'C'
            }

            number_map = {i: str(i) for i in range(2, 10)}
            number_map[1] = 'A'
            number_map[10] = 'T'
            number_map[11] = 'J'
            number_map[12] = 'Q'
            number_map[13] = 'K'

            suit = card.suit
            number = card.number
            return(suit_map[suit] + number_map[number])



        def get_image(path):
            cwd = os.path.dirname(__file__)
            image = pygame.image.load(os.path.join(cwd, path))
            return image

        def scale_card_img(card_img):
            return pygame.transform.scale(card_img, (card_img_width, card_img_height))


        # board
        pygame.draw.ellipse(self.window, board_color, pygame.Rect(board_x, board_y, board_a, board_b))
        font = pygame.font.Font(None, 28)
        

        
        # dealer position
        dealer_idx = self.game_elements['board'].dealer_position

        # player
        player_number = len(self.game_elements['players'])
        degree_list = np.linspace(np.pi/2, 5*np.pi/2, player_number+1)

        
        player_info_x_y = [get_ellipse_position(player_info_a//2, player_info_b//2, degree) for degree in degree_list]
        hole_card_info_x_y = [get_ellipse_position(card_info_a//2, card_info_b//2, degree, 'card_info') for degree in degree_list]
        community_card_info_x_y = [(community_card_x + i*(card_img_width+card_spacing), community_card_y) for i in range(5)]


        player_list = [player.player_name for player in self.game_elements['players']]
        for pidx in range(len(player_list)):

            # player info
            player_string_list = [player_list[pidx]]
            if player_list[pidx] == 'player_1':
                player_string_list.append('(you)')
            if self.game_elements['players'][pidx].status == 'lost':
                player_string_list.append('(lost)')
            else:
                player_string_list.append(f"${self.game_elements['players'][pidx].current_cash}")
            if pidx == dealer_idx:
                player_string_list.append('(dealer)')
            last_move = self.game_elements['players_last_move_list'][pidx]
            if last_move not in ['LOST', 'NONE']:
                player_string_list.append(last_move)
            

            for player_info_idx in range(len(player_string_list)):
                text = font.render(player_string_list[player_info_idx], True, text_color)
                text_rect = text.get_rect(center=(player_info_x_y[pidx][0], player_info_x_y[pidx][1] + line_spacing*player_info_idx))
                self.window.blit(text, text_rect)

            # card info
            hole_card = self.game_elements['players'][pidx].hole_cards
            for card_idx, card in enumerate(hole_card):
                card_img = scale_card_img(get_image(os.path.join("img",f"{get_img_name(card)}.png")))
                dealer_card_rect = self.window.blit(card_img, (hole_card_info_x_y[pidx][0]+card_idx*(card_img_width+card_spacing), hole_card_info_x_y[pidx][1]))
        
        # community card
        community_cards = self.game_elements['board'].community_cards
        community_cards = community_cards + [None] * (5 - len(community_cards))
        community_cards_object = None
        for community_card_idx, community_card in enumerate(community_cards):
            if community_card:
                tem_card_img = scale_card_img(get_image(os.path.join("img",f"{get_img_name(community_card)}.png")))
            else:
                tem_card_img = scale_card_img(get_image(os.path.join("img",f"empty_card.png")))

            dealer_card_rect = self.window.blit(tem_card_img, (community_card_info_x_y[community_card_idx][0], community_card_info_x_y[community_card_idx][1]))


        # pot
        pot_amount_string = "Pot: $" + str(self.game_elements['board'].total_cash_on_table)
        text_surface = font.render(pot_amount_string, True, text_color)
        self.window.blit(text_surface, text_surface.get_rect(center = (board_center_x, dealer_card_rect.bottom + card_img_height/2)))

        # game index
        game_index_string = "Game: " + str(self.game_elements['board'].game_idx)
        text_surface = font.render(game_index_string, True, text_color)
        self.window.blit(text_surface, text_surface.get_rect(center = (game_index_box_x, game_index_box_y)))


        # action mask
        action_masks = self._get_info()['action_masks'].tolist()
        action_box_x_y = [(action_box_x, action_box_y + i*(action_box_height+action_box_spacing)) for i in range(5)]

        for action_idx, action in enumerate(['Call(0)', 'Bet(1)', 'Raise_bet(2)', 'Check(3)', 'Fold(4)']):
            if action_masks[action_idx] == 1:
                # allow action
                text_backgound_color = (7, 250, 2)
                text_color = (0, 0, 0)
            else:
                # not allow action
                text_backgound_color = (250, 2, 2)
                text_color = (181, 184, 178)

            text = font.render(action, True, text_color, text_backgound_color)
            text_rect = text.get_rect(topleft=action_box_x_y[action_idx])
            self.window.blit(text, text_rect)




        # 
        pygame.display.update()
        
    def close(self):
        pass
        """
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
        """
