from action_choices import *
from card_utility_actions import *
from action import Action


import logging

logger = logging.getLogger('open_poker.envs.poker_util.logging_info.player')

class Player:
    def __init__(self, player_name, status, current_cash, hole_cards,
                 current_bet, agent, current_decision):
        """
        Each object is unique player in the game
        :param player_name: name of player
        :param status: lost, active
        :param current_cash: int total cash in hand
        :param hole_cards: 2 card in hand for playing game
        :param current_bet: current bet in the round
        :param agent: agent object of this player
        """
        self.player_name = player_name
        self.status = status #   lost, active
        self.current_cash = current_cash
        self.hole_cards = hole_cards
        self.current_bet = current_bet   # save chips the player has called, bet, raise bet, all-in
        self.agent = agent
        self.current_decision = current_decision  # call/fold/check/all_in/bet/raise_bet in the current round

        self.is_fold = False  # which might skip their turn if is fold
        self.is_all_in = False  # which might skip their turn if is all-in
        self.bet_amount_each_round = 0  # total money the player bet in each round
        self.bet_amount_each_game = 0  # total money the player bet in each game

        self.current_money_in_pot = 0

        # place to store reward
        self.last_game_cash = current_cash
        self.last_reward = 0



        self.position = -1

    def assign_hole_cards(self, cards):
        """
        assign hole cards to player from board
        :param cards:
        :return:
        """
        if not cards:
            logger.debug('Error: cannot assign empty cards list to player')
            raise Exception

        self.hole_cards = cards

    def assign_current_decision(self, decision):
        """
        update player current decision in this round, includes call/bet/raise_bet/check/fold/all_in
        :param decision:
        :return:
        """
        self.current_decision = decision

    def assign_status(self, current_gameboard, assign_to='waiting_for_move'):
        """
        assign player's status, which might skip its turn if lost/win
        :param assign_to:
        :return:
        """
        self.status = assign_to
        if assign_to == 'lost':
            self.current_cash = 0

        


    def assign_to_fold(self, current_gameboard):
        """
        if player decide to fold this game, directly call this function
        :return:
        """
        if current_gameboard['board'].num_active_player_on_table < 1:
            logger.debug('Error: something go wrong')
            raise Exception

        logger.debug(f'{self.player_name} is assigned to fold')
        self.is_fold = True
        current_gameboard['board'].num_active_player_on_table -= 1

    def assign_to_all_in(self, current_gameboard):
        """
        assign this player to all-in status
        :param current_gamebaord:
        :return:
        """
        logger.debug(f'{self.player_name} is assigned to all-in')
        self.is_all_in = True

    def add_current_bet(self, amount, chips):
        """
        current_bet is where player put chips in with corresponding amount, which would be take away later by board
        the function add those chips here
        :param amount:
        :param chips:
        :return:
        """
        if amount < 0:
            logger.debug('Error: cannot add negative chips to current bet')
            raise Exception

        if amount not in self.current_bet:
            self.current_bet[amount] = set()
        for c in copy.copy(chips):
            self.current_bet[amount].add(c)

    def add_bet_amount_each_round(self, current_gameboard, amount):
        """
        add the total amount of money the player bet in this round
        :param amount:
        :return:
        """
        current_gameboard['board'].player_pot[self.player_name] += amount


    def reduce_current_cash(self, amount):
        """
        if bet, current cash amount should be reduced
        :param amount:
        :return:
        """
        self.current_cash -= amount



    def reset_player_each_game(self, current_gameboard):
        """
        Args:
            current_gameboard
            phase(Phase)

        Returns:
            None

        """


        self.small_blind = False
        self.big_blind = False
        self.hole_cards = list()
        self.current_bet = dict()
        self.is_fold = False
        self.is_all_in = False
        self.bet_amount_each_game = 0

    def reset_player_each_round(self, current_gameboard):
        """
        reset those variables to prepare for next round
        :return:
        """
        self.current_bet = dict()
        self.current_decision = None
        self.bet_amount_each_round = 0


        return chips, total_bet

    def force_bet_small_blind(self, current_gameboard):  # what is number?
        """
        Already checked if player have enough money for small blind in dealer.check_and_deal_hole_cards
        Args:
            current_gameboard

        Returns:
            None

        """
        

        small_blind_amount = current_gameboard["small_blind_amount"]
        logger.debug(f'{self.player_name} is forced to bet ${small_blind_amount} as small blind')
        self.current_cash -= small_blind_amount 

        self.add_bet_amount_each_round(current_gameboard, small_blind_amount)


        return 

        


    def force_bet_big_blind(self, current_gameboard, time_raise_from_small_blind=2):
        """
        Already checked if player have enough money for small blind in dealer.check_and_deal_hole_cards
        Args:
            current_gameboard

        Returns:
            None

        """

      
        big_blind_amount = current_gameboard["big_blind_amount"]
        logger.debug(f'{self.player_name} is forced to bet ${big_blind_amount} as big blind')

        self.current_cash -= big_blind_amount 

        self.add_bet_amount_each_round(current_gameboard, big_blind_amount)


        return 

    def assign_small_blind(self, current_gameboard, assign_to=False):
        """
        assigns the player left of the dealer to small blind after river
        :param current_gameboard:
        :param player_name:
        :return:
        """
        if not assign_to and not self.small_blind:
            logger.debug(f'{self.player_name} is already not small blind, something go wrong...')
            raise Exception
        elif assign_to and self.small_blind:
            logger.debug(f'{self.player_name} is already small blind, something go wrong...')
            raise Exception

        self.small_blind = assign_to
        logger.debug(f'{self.player_name} successfully set to small blind')

    def assign_big_blind(self, current_gameboard, assign_to=False):
        """
        assigns the player left of the small blind to small blind after river
        :param current_gameboard:
        :param player_name:
        :return:
        """
        if not assign_to and not self.big_blind:
            logger.debug(f'{self.player_name} is already not big blind, something go wrong...')
            raise Exception
        elif assign_to and self.big_blind:
            logger.debug(f'{self.player_name} is already big blind, something go wrong...')
            raise Exception

        self.big_blind = assign_to
        logger.debug(f'{self.player_name} successfully set to big blind')

    def compute_allowable_pre_flop_actions_old(self, current_gameboard):
        """
        Players in this phase could call, raise, or fold (no all-in in this turn?)
        The phase could finish only if all player who would like to continue put the same amount of money
        :param current_gameboard:
        :return: allowable actions
        :rtype: set
        """
        logger.debug(f'{self.player_name} computes allowable pre-flop round actions...')
        allowable_actions = set()

        # big blind are able to check if no other raise bet in pre-flop
        big_blind_force_bet = current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']
        if self.big_blind and big_blind_force_bet == current_gameboard['board'].current_highest_bet:
            allowable_actions.add(check)

        allowable_actions.add(fold)  # can fold in any case

        allowable_actions.add(call)
        allowable_actions.add(raise_bet)

        return allowable_actions


    def compute_allowable_pre_flop_actions(self, current_gameboard):
        """

        if you are highest bet in the last move, then you cannot raise_bet again

        1. fold
            always
        2. check
            bet/raise_bet not in last_move
        3. bet
            big_blind already bet, so no bet allowed

        The following depends on current_cash:
        if cash < raise_amount:
            # no call and raise_net. only have all_in
            # no one bet before, or someone bet/raise_bet
            if (current_gameboard['board'].current_bet_count == 0) or (bet/raise_bet in last_move)
                4. all_in
        else:
            # no all_in. have call, and raise_bet. 
            5. raise_bet
                current_gameboard['board'].current_raise_count < max
            6. call
                raise_bet in last_move

        
        corner case:
            big blind
            small blind

        Args:
            current_gameboard

        Returns:
            allowable_actions(set)
            

        Raises:

        """
        if current_gameboard['players_dict'][self.player_name].status == 'lost':
            raise

        allowable_actions = set()

        
        # get player_idx
        for player_idx, player in enumerate(current_gameboard['players']):
            if player.player_name == self.player_name:
                break

        # check if it is fold already
        if current_gameboard['board'].players_last_move_list[player_idx] == Action.FOLD:
            raise

        # 1. fold
        allowable_actions.add(fold)  # can fold in any case

        # 2. bet: in the pre-flop, big blind is already considered as bet, so only raise_bet is allowed in pre-flop

        # 3. check
        # only big blind can chcek in pre-flop
        if current_gameboard['board'].players_last_move_list[player_idx] == Action.BIG_BLIND and \
        Action.ALL_IN not in current_gameboard['board'].players_last_move_list:
            allowable_actions.add(check)



        # calculate bet_to_follow:
        if current_gameboard['board'].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
            raise_amount = current_gameboard['small_bet']
        elif current_gameboard['board'].cur_phase in [Phase.TURN, Phase.RIVER]:
            raise_amount = current_gameboard['big_bet']
        else:
            raise
        already_bet = current_gameboard['board'].player_pot[player.player_name]

        # raise_bet, all_in
        if current_gameboard['board'].current_raise_count < current_gameboard['max_raise_count']:
            current_bet_count = 1
            current_raise_count = current_gameboard['board'].current_raise_count + 1
        else:
            current_bet_count = 1
            current_raise_count = current_gameboard['max_raise_count']



        bet_to_follow = raise_amount * (1 + current_raise_count) - already_bet

        if self.current_cash <= bet_to_follow:
            # 4. all_in
            allowable_actions.add(all_in)

        else:
            # 5. raise_bet
            # in pre-flop, we only need to check current_raise_count because big blind is bet already
            if current_gameboard['board'].current_raise_count < current_gameboard['max_raise_count']:
                allowable_actions.add(raise_bet)


        # call, all_in
        bet_to_follow = raise_amount * (1 + current_gameboard['board'].current_raise_count) - already_bet
        if current_gameboard['board'].players_last_move_list[player_idx] != Action.BIG_BLIND:
            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)




        return allowable_actions

    

    def compute_allowable_flop_actions(self, current_gameboard):
        """
        1. fold
            always
        2. check
            bet/raise_bet not in last_move
        

        The following depends on current_cash:
        if cash < raise_amount:
            # no call, bet, and raise_net. only have all_in
            # no one bet before, or someone bet/raise_bet
            if (current_gameboard['board'].current_bet_count == 0) or (bet/raise_bet in last_move)
                6. all_in
        else:
            # no all_in. have call, bet, and raise_net. 
            3. bet
                current_gameboard['board'].current_bet_count == 0
            4. raise_bet
                bet/raise_bet in last_move and current_gameboard['board'].current_raise_count < max
            5. call
                bet/raise_bet in last_move
        
        Args:
        current_gameboard

        Returns:
            bool: True if betting is over

        """
        if current_gameboard['players_dict'][self.player_name].status == 'lost':
            raise

        allowable_actions = set()

        
        # get player_idx
        for player_idx, player in enumerate(current_gameboard['players']):
            if player.player_name == self.player_name:
                break

        # check if it is fold already
        if current_gameboard['board'].players_last_move_list[player_idx] == Action.FOLD:
            raise

        # 1. fold
        allowable_actions.add(fold)  # can fold in any case

        # 2. check
        # if no bet/raise_bet in players_last_move_list
        if Action.RAISE_BET not in current_gameboard['board'].players_last_move_list and \
        Action.BET not in current_gameboard['board'].players_last_move_list and \
        Action.ALL_IN not in current_gameboard['board'].players_last_move_list:
            allowable_actions.add(check)


        # call, bet, raise_bet, all_in
        # calculate bet_to_follow
        if current_gameboard['board'].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
            raise_amount = current_gameboard['small_bet']
        elif current_gameboard['board'].cur_phase in [Phase.TURN, Phase.RIVER]:
            raise_amount = current_gameboard['big_bet']
        else:
            raise

        already_bet = current_gameboard['board'].player_pot[player.player_name]



        # bet, raise_bet, all_in
        # case 1: no bet happened before
        if current_gameboard['board'].current_bet_count == 0:
            # in this case, the player have no enough cash to bet. But for other players, they should consider this player call bet.
            current_bet_count = 1
            current_raise_count = 0
        # case 2: already bet happened before, consider as raise
        elif current_gameboard['board'].current_bet_count == 1 and current_gameboard['board'].current_raise_count < current_gameboard['max_raise_count']:
            current_bet_count = 1
            current_raise_count = current_gameboard['board'].current_raise_count + 1
        else:
            current_bet_count = 1
            current_raise_count = current_gameboard['max_raise_count']

        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(all_in)
        else:
            # 2. bet: 
            if current_gameboard['board'].current_bet_count == 0:
                allowable_actions.add(bet)

            # 3. raise_bet
            # check if bet/raise_bet in players_last_move_list. The following logic should be the same
            elif current_gameboard['board'].current_raise_count < current_gameboard['max_raise_count']:
                allowable_actions.add(raise_bet)

        # call, all_in
        if current_gameboard['board'].current_bet_count != 0:
            bet_to_follow = raise_amount * (1 + current_gameboard['board'].current_raise_count) - already_bet

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)



        return allowable_actions




    def compute_allowable_turn_actions(self, current_gameboard):
        """
        first player: bet or check
        
        Args:
        current_gameboard

        Returns:
            bool: True if betting is over

        """
        if current_gameboard['players_dict'][self.player_name].status == 'lost':
            raise

        allowable_actions = set()

        
        # get player_idx
        for player_idx, player in enumerate(current_gameboard['players']):
            if player.player_name == self.player_name:
                break

        # check if it is fold already
        if current_gameboard['board'].players_last_move_list[player_idx] == Action.FOLD:
            raise

        # 1. fold
        allowable_actions.add(fold)  # can fold in any case

        # 2. check
        # if no bet/raise_bet in players_last_move_list
        if Action.RAISE_BET not in current_gameboard['board'].players_last_move_list and \
        Action.BET not in current_gameboard['board'].players_last_move_list and \
        Action.ALL_IN not in current_gameboard['board'].players_last_move_list:
            allowable_actions.add(check)


        # call, bet, raise_bet, all_in
        # calculate bet_to_follow
        if current_gameboard['board'].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
            raise_amount = current_gameboard['small_bet']
        elif current_gameboard['board'].cur_phase in [Phase.TURN, Phase.RIVER]:
            raise_amount = current_gameboard['big_bet']
        else:
            raise

        already_bet = current_gameboard['board'].player_pot[player.player_name]


        # bet, raise_bet, all_in
        # case 1: no bet happened before
        if current_gameboard['board'].current_bet_count == 0:
            # in this case, the player have no enough cash to bet. But for other players, they should consider this player call bet.
            current_bet_count = 1
            current_raise_count = 0
        # case 2: already bet happened before, consider as raise
        elif current_gameboard['board'].current_bet_count == 1 and current_gameboard['board'].current_raise_count < current_gameboard['max_raise_count']:
            current_bet_count = 1
            current_raise_count = current_gameboard['board'].current_raise_count + 1
        else:
            current_bet_count = 1
            current_raise_count = current_gameboard['max_raise_count']

        
        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(all_in)
        else:
            # 2. bet: 
            if current_gameboard['board'].current_bet_count == 0:
                allowable_actions.add(bet)

            # 3. raise_bet
            # check if bet/raise_bet in players_last_move_list. The following logic should be the same
            elif current_gameboard['board'].current_raise_count < current_gameboard['max_raise_count']:
                allowable_actions.add(raise_bet)

        # call, all_in
        if current_gameboard['board'].current_bet_count != 0:
            bet_to_follow = raise_amount * (1 + current_gameboard['board'].current_raise_count) - already_bet

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)



        return allowable_actions




    def compute_allowable_river_actions(self, current_gameboard):
        """
        first player: bet or check
        
        Args:
        current_gameboard

        Returns:
            bool: True if betting is over

        """
        if current_gameboard['players_dict'][self.player_name].status == 'lost':
            raise

        allowable_actions = set()

        
        # get player_idx
        for player_idx, player in enumerate(current_gameboard['players']):
            if player.player_name == self.player_name:
                break

        # check if it is fold already
        if current_gameboard['board'].players_last_move_list[player_idx] == Action.FOLD:
            raise

        # 1. fold
        allowable_actions.add(fold)  # can fold in any case

        # 2. check
        # if no bet/raise_bet in players_last_move_list
        if Action.RAISE_BET not in current_gameboard['board'].players_last_move_list and \
        Action.BET not in current_gameboard['board'].players_last_move_list and \
        Action.ALL_IN not in current_gameboard['board'].players_last_move_list:
            allowable_actions.add(check)


        # call, bet, raise_bet, all_in
        # calculate bet_to_follow
        if current_gameboard['board'].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
            raise_amount = current_gameboard['small_bet']
        elif current_gameboard['board'].cur_phase in [Phase.TURN, Phase.RIVER]:
            raise_amount = current_gameboard['big_bet']
        else:
            raise

        already_bet = current_gameboard['board'].player_pot[player.player_name]


        # bet, raise_bet, all_in
        # case 1: no bet happened before
        if current_gameboard['board'].current_bet_count == 0:
            # in this case, the player have no enough cash to bet. But for other players, they should consider this player call bet.
            current_bet_count = 1
            current_raise_count = 0
        # case 2: already bet happened before, consider as raise
        elif current_gameboard['board'].current_bet_count == 1 and current_gameboard['board'].current_raise_count < current_gameboard['max_raise_count']:
            current_bet_count = 1
            current_raise_count = current_gameboard['board'].current_raise_count + 1
        else:
            current_bet_count = 1
            current_raise_count = current_gameboard['max_raise_count']

        
        bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet

        if self.current_cash <= bet_to_follow:
            allowable_actions.add(all_in)
        else:
            # 2. bet: 
            if current_gameboard['board'].current_bet_count == 0:
                allowable_actions.add(bet)

            # 3. raise_bet
            # check if bet/raise_bet in players_last_move_list. The following logic should be the same
            elif current_gameboard['board'].current_raise_count < current_gameboard['max_raise_count']:
                allowable_actions.add(raise_bet)



        # call, all_in
        if current_gameboard['board'].current_bet_count != 0:
            bet_to_follow = raise_amount * (1 + current_gameboard['board'].current_raise_count) - already_bet

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)



        return allowable_actions



    def make_pre_flop_moves(self, current_gameboard):
        """
        player takes actions in pre-flop round
        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} currently in pre-flop round')
        allowable_actions = self.compute_allowable_pre_flop_actions(current_gameboard=current_gameboard)


        action_to_execute, parameters = self.agent.make_pre_flop_moves(self, current_gameboard, allowable_actions)
        # current_gameboard['player_last_move'] = Action[action_to_execute.__name__]

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_pre_flop_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append((action_to_execute, parameters))



        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_flop_moves(self, current_gameboard):
        """
        player takes actions in flop round
        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} currently in flop round')
        allowable_actions = self.compute_allowable_flop_actions(current_gameboard=current_gameboard)


        action_to_execute, parameters = self.agent.make_flop_moves(self, current_gameboard, allowable_actions)

        #current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_flop_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append((action_to_execute, parameters))

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_turn_moves(self, current_gameboard):
        """
        player takes actions in turn round
        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} currently in turn round')
        allowable_actions = self.compute_allowable_turn_actions(current_gameboard=current_gameboard)

        action_to_execute, parameters = self.agent.make_turn_moves(self, current_gameboard, allowable_actions)

        #current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_turn_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append((action_to_execute, parameters))

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_river_moves(self, current_gameboard):
        """
        player takes actions in river round
        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} currently in river round')
        allowable_actions = self.compute_allowable_river_actions(current_gameboard=current_gameboard)


        action_to_execute, parameters = self.agent.make_river_moves(self, current_gameboard, allowable_actions)


        #current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_river_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append((action_to_execute, parameters))

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    

    def _execute_action(self, action_to_execute, parameters, current_gameboard):
        """
        executing the action in each round for the player
        :param action_to_execute: action function to run
        :param parameters:
        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} executes its _execute_action function')
        if parameters:
            p = action_to_execute(**parameters)
            # add to game history
            current_gameboard['history']['function'].append(action_to_execute)
            params = parameters.copy()
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(p)
            return p
        else:
            p = action_to_execute()
            # add to game history
            current_gameboard['history']['function'].append(action_to_execute)
            params = dict()
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(p)

            return p
