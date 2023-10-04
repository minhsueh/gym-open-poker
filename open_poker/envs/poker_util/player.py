from action_choices import *
from card_utility_actions import *

import logging

logger = logging.getLogger('open_poker.envs.poker_util.logging_info.player')

class Player:
    def __init__(self, player_name, status, current_cash, small_blind, big_blind, is_dealer, hole_cards,
                 current_bet, agent, chips, current_decision):
        """
        Each object is unique player in the game
        :param player_name: name of player
        :param status: win, lost, waiting_for_move
        :param current_cash: int total cash in hand
        :param small_blind: if current is small blind True, otherwise False
        :param big_blind: if current is big blind True, otherwise False
        :param is_dealer: if current is dealer of board True, otherwise False
        :param hole_cards: 2 card in hand for playing game
        :param current_bet: current bet in the round
        :param agent: agent object of this player
        :param chips: dict of chips with amount as key, and chips as value in a set
        """
        self.player_name = player_name
        self.status = status    # win, lost, waiting for move
        self.current_cash = current_cash
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.is_dealer = is_dealer
        self.hole_cards = hole_cards
        self.current_bet = current_bet   # save chips the player has called, bet, raise bet, all-in
        self.agent = agent
        self.chips = chips
        self.current_decision = current_decision  # call/fold/check/all_in/bet/raise_bet in the current round

        self.is_fold = False  # which might skip their turn if is fold
        self.is_all_in = False  # which might skip their turn if is all-in
        self.bet_amount_each_round = 0  # total money the player bet in each round
        self.bet_amount_each_game = 0  # total money the player bet in each game

        self.current_money_in_pot = 0



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
        current_gameboard['board'].num_active_player_on_table -= 1

        current_gameboard['players_last_move_list'][self.position] = 'LOSE'


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

    def add_bet_amount_each_round(self, amount):
        """
        add the total amount of money the player bet in this round
        :param amount:
        :return:
        """
        self.bet_amount_each_round += amount

    def reduce_current_cash(self, amount):
        """
        if bet, current cash amount should be reduced
        :param amount:
        :return:
        """
        self.current_cash -= amount

    def reset_player_each_game_old(self, current_gameboard):
        """
        reset those variables after finish current game, and prepare for the next one
        :return:
        """
        if current_gameboard['cur_phase'] != 'concluding_phase':
            logger.debug(f'{self.player_name} are in wrong phase to reset each game')
            raise Exception

        self.small_blind = False
        self.big_blind = False
        self.hole_cards = list()
        self.current_bet = dict()
        self.is_fold = False
        self.is_all_in = False
        self.bet_amount_each_game = 0

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

    def force_bet_small_blind_old(self, current_gameboard):  # what is number?
        """
        This player is forced to pay the half of small bet limit at the table
        :param current_gameboard:
        :return:
        """
        if not self.small_blind:
            logger.debug(f'{self.player_name} is not small blind, and cannot force to bet...')
            raise Exception

        # small blind from $1 chip
        logger.debug(f'{self.player_name} is forced to bet ${current_gameboard["small_blind_amount"]} as small blind')
            
        chips, remaining = chips_combination_given_amount(self, current_gameboard['small_blind_amount'], current_gameboard)
        if not chips:
            return None, 0
        total_bet = 0
        for amount, chips_list in chips.items():
            total_bet += amount * len(chips_list)
            self.add_current_bet(amount, chips_list)
        self.current_cash -= total_bet 

        self.add_bet_amount_each_round(total_bet)
        self.bet_amount_each_game += total_bet

        current_gameboard['board'].add_total_cash_on_table(total_bet)
        current_gameboard['board'].compare_for_highest_bet(total_bet)
        current_gameboard['board'].add_chips_to_pot(chips)

        return chips, total_bet

    def force_bet_small_blind(self, current_gameboard):  # what is number?
        """
        Already checked if player have enough money for small blind in dealer.check_and_deal_hole_cards
        Args:
            current_gameboard

        Returns:
            None

        """
        if not self.small_blind:
            logger.debug(f'{self.player_name} is not small blind, and cannot force to bet...')
            raise Exception

        small_blind_amount = current_gameboard["small_blind_amount"]
        logger.debug(f'{self.player_name} is forced to bet ${small_blind_amount} as small blind')
        self.current_cash -= small_blind_amount 

        self.add_bet_amount_each_round(small_blind_amount)
        self.bet_amount_each_game += small_blind_amount

        current_gameboard['board'].add_total_cash_on_table(small_blind_amount)

        return 

        

    def force_bet_big_blind_old(self, current_gameboard, time_raise_from_small_blind=2):
        """
        This player is force to pay the small bet limit at the table
        :param current_gameboard:
        :param time_raise_from_small_blind:
        :return:
        """
        if not self.big_blind:
            logger.debug(f'{self.player_name} is not big blind, and cannot force to bet...')

        # big blind from $2 chip, which are two $1 chip not one $5 chip
        amount_for_big_blind = current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']
        logger.debug(f'{self.player_name} is forced to bet ${amount_for_big_blind} as big blind')
        chips, remaining = chips_combination_given_amount(self, amount_for_big_blind, current_gameboard)
        if not chips:
            return None, 0
        total_bet = 0
        for amount, chips_list in chips.items():
            total_bet += amount * len(chips_list)
            self.add_current_bet(amount, chips_list)
        self.current_cash -= total_bet
        self.add_bet_amount_each_round(total_bet)
        self.bet_amount_each_game += total_bet

        current_gameboard['board'].add_total_cash_on_table(total_bet)
        current_gameboard['board'].compare_for_highest_bet(total_bet)
        current_gameboard['board'].add_chips_to_pot(chips)

        return chips, total_bet

    def force_bet_big_blind(self, current_gameboard, time_raise_from_small_blind=2):
        """
        Already checked if player have enough money for small blind in dealer.check_and_deal_hole_cards
        Args:
            current_gameboard

        Returns:
            None

        """

        if not self.big_blind:
            logger.debug(f'{self.player_name} is not big blind, and cannot force to bet...')

        big_blind_amount = current_gameboard["big_blind_amount"]
        logger.debug(f'{self.player_name} is forced to bet ${big_blind_amount} as big blind')

        self.current_cash -= big_blind_amount 

        self.add_bet_amount_each_round(big_blind_amount)
        self.bet_amount_each_game += big_blind_amount

        current_gameboard['board'].add_total_cash_on_table(big_blind_amount)

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
        
        Args:
            current_gameboard

        Returns:
            allowable_actions(set)
            

        Raises:

        """
        logger.debug(f'{self.player_name} computes allowable pre-flop round actions...')
        allowable_actions = set()

        # check if it is fold already
        for player_idx, player in enumerate(current_gameboard['players']):
            if player.player_name == self.player_name and current_gameboard['players_last_move_list'][player_idx] == 'FOLD':
                return(allowable_actions)



        # big blind

        if current_gameboard['current_raise_count'] == 0 and self.position == current_gameboard['big_blind_postiion_idx']:
            allowable_actions.add(check)

        allowable_actions.add(fold)  # can fold in any case

        allowable_actions.add(call)
        allowable_actions.add(raise_bet)

        return allowable_actions

    def compute_allowable_flop_actions_old(self, current_gameboard):
        """
        Players in this phase could call, raise, fold, check, bet, and all-in:
            1. player could check only if he/she is first player or previous players also check in this turn. Special
            condition that everyone checks in this round, then the round finished and dealt a new card for next round.
            2. all-in situations:
                (1)
            3. bet only added if he/she is first player to put chips into the pot
        Finish condition is same as pre-flop phase

        :param current_gameboard:
        :return: allowable actions
        :rtype: set
        """
        # will be (check, bet, fold) and then (raise, call, fold) if everyone does not check
        logger.debug(f'{self.player_name} computes allowable flop round actions...')
        allowable_actions = set()
        allowable_actions.add(fold)

        # can bet only if there are not others bet before
        # can check only if there are not others bet before
        if not current_gameboard['board'].current_highest_bet:
            allowable_actions.add(check)
            allowable_actions.add(bet)

        # can all-in if have cash
        # if self.current_cash > 0:
        #    allowable_actions.add(all_in)

        # can raise bet if there are other bet previously
        # can call if there are other bet previously
        if current_gameboard['board'].current_highest_bet:
            allowable_actions.add(raise_bet)
            allowable_actions.add(call)

        return allowable_actions

    def compute_allowable_flop_actions(self, current_gameboard):
        """
        first player: bet or check
        
        Args:
        current_gameboard

        Returns:
            bool: True if betting is over

        """
        logger.debug(f'{self.player_name} computes allowable flop round actions...')
        allowable_actions = set()

        # check if it is fold already
        for player_idx, player in enumerate(current_gameboard['players']):
            if player.player_name == self.player_name and current_gameboard['players_last_move_list'][player_idx] == 'FOLD':
                return(allowable_actions)

        allowable_actions.add(fold)


        if current_gameboard['current_bet_count'] == 0:
            allowable_actions.add(bet)
            allowable_actions.add(check)
        elif current_gameboard['current_bet_count'] == 1 and current_gameboard['current_raise_count'] < current_gameboard['max_raise_count']:
            allowable_actions.add(raise_bet)
            allowable_actions.add(call)
        elif current_gameboard['current_bet_count'] == 1 and current_gameboard['current_raise_count'] == current_gameboard['max_raise_count']:
            allowable_actions.add(call)
        else:
            raise

        return allowable_actions

    def compute_allowable_turn_actions_old(self, current_gameboard):
        """
        Allowable actions is same as in flop round
        :param current_gameboard:
        :return: allowable actions
        :rtype: set
        """
        # will be (check, bet, fold) and then (raise, call, fold) if everyone does not check
        logger.debug(f'{self.player_name} computes allowable turn round actions...')
        allowable_actions = set()
        allowable_actions.add(fold)

        # can bet only if there are not others bet before
        # can check only if there are not others bet before
        if not current_gameboard['board'].current_highest_bet:
            allowable_actions.add(check)
            allowable_actions.add(bet)

        # can all-in if have cash
        # if self.current_cash > 0:
        #    allowable_actions.add(all_in)

        # can raise bet if there are other bet previously
        # can call if there are other bet previously
        if current_gameboard['board'].current_highest_bet:
            allowable_actions.add(raise_bet)
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
        logger.debug(f'{self.player_name} computes allowable turn round actions...')
        allowable_actions = set()

        # check if it is fold already
        for player_idx, player in enumerate(current_gameboard['players']):
            if player.player_name == self.player_name and current_gameboard['players_last_move_list'][player_idx] == 'FOLD':
                return(allowable_actions)

        allowable_actions.add(fold)


        if current_gameboard['current_bet_count'] == 0:
            allowable_actions.add(bet)
            allowable_actions.add(check)
        elif current_gameboard['current_bet_count'] == 1 and current_gameboard['current_bet_count'] < current_gameboard['max_raise_count']:
            allowable_actions.add(raise_bet)
            allowable_actions.add(call)
        elif current_gameboard['current_raise_count'] == 1 and current_gameboard['current_bet_count'] == current_gameboard['max_raise_count']:
            allowable_actions.add(call)
        else:
            raise

        return allowable_actions

    def compute_allowable_river_actions_old(self, current_gameboard):
        """
        Allowable action is same as in flop and turn round
        :param current_gameboard:
        :return: allowable actions
        :rtype: set
        """
        # will be (check, bet, fold) and then (raise, call, fold) if everyone does not check
        logger.debug(f'{self.player_name} computes allowable river round actions...')
        allowable_actions = set()
        allowable_actions.add(fold)

        # can bet only if there are not others bet before
        # can check only if there are not others bet before
        if not current_gameboard['board'].current_highest_bet:
            allowable_actions.add(check)
            allowable_actions.add(bet)

        # can all-in if have cash
        # if self.current_cash > 0:
        #    allowable_actions.add(all_in)

        # can raise bet if there are other bet previously
        # can call if there are other bet previously
        if current_gameboard['board'].current_highest_bet:
            allowable_actions.add(raise_bet)
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
        logger.debug(f'{self.player_name} computes allowable river round actions...')
        allowable_actions = set()

        # check if it is fold already
        for player_idx, player in enumerate(current_gameboard['players']):
            if player.player_name == self.player_name and current_gameboard['players_last_move_list'][player_idx] == 'FOLD':
                return(allowable_actions)
        
        allowable_actions.add(fold)


        if current_gameboard['current_bet_count'] == 0:
            allowable_actions.add(bet)
            allowable_actions.add(check)
        elif current_gameboard['current_bet_count'] == 1 and current_gameboard['current_bet_count'] < current_gameboard['max_raise_count']:
            allowable_actions.add(raise_bet)
            allowable_actions.add(call)
        elif current_gameboard['current_raise_count'] == 1 and current_gameboard['current_bet_count'] == current_gameboard['max_raise_count']:
            allowable_actions.add(call)
        else:
            raise

        return allowable_actions

    def compute_allowable_computing_best_hand_actions(self, current_gameboard):
        """
        this might change to make by board, not execute by players
        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} computes allowable best hand actions...')
        allowable_actions = set()
        allowable_actions.add(current_gameboard['calculate_best_hand'])

        return allowable_actions

    def compute_allowable_continue_game_actions(self, current_gameboard):
        """
        In continue game phase, each player has completed their decision on pre-flop/flop/turn/river round.
        At this time, agents could only:
            1. call if it checked in this round
            2. fold if it did not want to continue
            3. match if it had bet a certain amount but smaller than the highest bet on the table
        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} computes allowable continue game actions...')
        allowable_actions = set()
        allowable_actions.add(fold)

        if self.current_decision == 'check':
            allowable_actions.add(call)

        if self.bet_amount_each_round < current_gameboard['board'].current_highest_bet:
            allowable_actions.add(match_highest_bet_on_the_table)

        return allowable_actions

    def make_pre_flop_moves(self, current_gameboard):
        """
        player takes actions in pre-flop round
        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} currently in pre-flop round')
        allowable_actions = self.compute_allowable_pre_flop_actions(current_gameboard=current_gameboard)

        code = 0
        action_to_execute, parameters = self.agent.make_pre_flop_moves(self, current_gameboard, allowable_actions, code)
        current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_pre_flop_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
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

        code = 0
        action_to_execute, parameters = self.agent.make_flop_moves(self, current_gameboard, allowable_actions, code)

        current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_flop_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
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

        code = 0
        action_to_execute, parameters = self.agent.make_turn_moves(self, current_gameboard, allowable_actions, code)

        current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_turn_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
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


        code = 0
        action_to_execute, parameters = self.agent.make_river_moves(self, current_gameboard, allowable_actions, code)


        current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_river_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append((action_to_execute, parameters))

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_computing_best_hand_moves(self, current_gameboard):
        """

        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} currently is computing best hand')
        allowable_actions = self.compute_allowable_computing_best_hand_actions(current_gameboard=current_gameboard)

        code = 0
        action_to_execute, parameters = self.agent.make_computing_best_hand_moves(self, current_gameboard, allowable_actions, code)

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_computing_best_hand_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append((action_to_execute, parameters))

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_continue_game_moves(self, current_gameboard):
        """

        :param current_gameboard:
        :return:
        """
        logger.debug(f'{self.player_name} currently is in continue game moves')
        allowable_actions = self.compute_allowable_continue_game_actions(current_gameboard=current_gameboard)

        code = 0
        action_to_execute, parameters = self.agent.make_continue_game_moves(self, current_gameboard, allowable_actions, code)

        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_continue_game_moves)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
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
