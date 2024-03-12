from action_choices import call, all_in, fold, raise_bet, bet, check
import action_choices
from action import Action
from phase import Phase


import logging

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.player")


class Player:
    def __init__(self, player_name, status, current_cash, hole_cards, agent):
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
        self.status = status  # lost, active
        self.current_cash = current_cash
        self.hole_cards = hole_cards
        self.agent = agent

        # place to store reward
        self.last_game_cash = current_cash
        self.last_reward = 0

    def assign_hole_cards(self, cards):
        """
        assign hole cards to player from board
        :param cards:
        :return:
        """
        if not cards:
            logger.debug("Error: cannot assign empty cards list to player")
            raise Exception

        self.hole_cards = cards

    def assign_status(self, current_gameboard, assign_to="waiting_for_move"):
        """
        assign player's status, which might skip its turn if lost/win
        :param assign_to:
        :return:
        """
        self.status = assign_to
        if assign_to == "lost":
            self.current_cash = 0

    def add_bet_amount_each_round(self, current_gameboard, amount):
        """
        add the total amount of money the player bet in this round
        :param amount:
        :return:
        """
        current_gameboard["board"].player_pot[self.player_name] += amount

    def reduce_current_cash(self, amount):
        """
        if bet, current cash amount should be reduced
        :param amount:
        :return:
        """
        if amount <= 0:
            raise
        self.current_cash -= amount

    def add_current_cash(self, amount):
        """
        if bet/raise_bet and all other players fold, then the betting will be returned in conclude_round
        :param amount:
        :return:
        """
        if amount <= 0:
            raise
        self.current_cash += amount

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

    def force_bet_small_blind(self, current_gameboard):  # what is number?
        """
        Already checked if player have enough money for small blind in dealer.check_and_deal_hole_cards
        Args:
            current_gameboard

        Returns:
            None

        """

        small_blind_amount = current_gameboard["small_blind_amount"]
        logger.debug(f"{self.player_name} is forced to bet ${small_blind_amount} as small blind")
        self.current_cash -= small_blind_amount

        self.add_bet_amount_each_round(current_gameboard, small_blind_amount)

        if self.current_cash == 0:
            # modify players_last_move_list_hist to ALL_IN
            for player_idx, player in enumerate(current_gameboard["players"]):
                if player.player_name == self.player_name:
                    current_gameboard["board"].players_last_move_list[player_idx] = Action.ALL_IN

    def force_bet_big_blind(self, current_gameboard, time_raise_from_small_blind=2):
        """
        Already checked if player have enough money for small blind in dealer.check_and_deal_hole_cards
        Args:
            current_gameboard

        Returns:
            None

        """
        big_blind_amount = current_gameboard["big_blind_amount"]
        logger.debug(f"{self.player_name} is forced to bet ${big_blind_amount} as big blind")

        self.current_cash -= big_blind_amount

        self.add_bet_amount_each_round(current_gameboard, big_blind_amount)

        if self.current_cash == 0:
            # modify players_last_move_list_hist to ALL_IN
            for player_idx, player in enumerate(current_gameboard["players"]):
                if player.player_name == self.player_name:
                    current_gameboard["board"].players_last_move_list[player_idx] = Action.ALL_IN

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
        if current_gameboard["players_dict"][self.player_name].status == "lost":
            raise

        allowable_actions = set()

        # get player_idx
        for player_idx, player in enumerate(current_gameboard["players"]):
            if player.player_name == self.player_name:
                break

        # check if it is fold already
        if current_gameboard["board"].players_last_move_list[player_idx] == Action.FOLD:
            raise

        # 1. fold
        allowable_actions.add(fold)  # can fold at any time

        # bet, raise_bet, call, chcek, all_in

        if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
            raise_amount = current_gameboard["small_bet"]
        elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
            raise_amount = current_gameboard["big_bet"]
        else:
            raise

        already_bet = current_gameboard["board"].player_pot[player.player_name]
        current_bet_count = current_gameboard["board"].current_bet_count
        current_raise_count = current_gameboard["board"].current_raise_count

        if current_bet_count == 0:
            # bet(all_in)
            if self.current_cash <= raise_amount:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(bet)
            # check
            allowable_actions.add(check)

        elif current_bet_count == 1 and current_raise_count < current_gameboard["max_raise_count"]:

            is_big_blind = False
            # exception: BB in pre-flop
            if current_gameboard["board"].players_last_move_list[player_idx] == Action.BIG_BLIND:
                is_big_blind = True

            # call, all_in
            bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
            if (
                current_gameboard["board"].cur_phase == Phase.PRE_FLOP
                and bet_to_follow == 0
                and current_gameboard["board"].players_last_move_list[player_idx] != Action.BIG_BLIND
            ):
                raise
            if is_big_blind and current_raise_count == 0:
                allowable_actions.add(check)
            else:
                if self.current_cash <= bet_to_follow:
                    allowable_actions.add(all_in)
                else:
                    allowable_actions.add(call)

            # raise_bet, all_in
            required_raise_amount = raise_amount * (current_bet_count + current_raise_count + 1) - already_bet
            if self.current_cash <= required_raise_amount:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(raise_bet)

        elif current_bet_count == 1 and current_raise_count == current_gameboard["max_raise_count"]:
            # call, all_in

            bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
            if bet_to_follow == 0:
                raise

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)

        else:
            raise

        logger.debug("allowable_actions = " + ", ".join([action.__name__ for action in allowable_actions]))

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
        if current_gameboard["players_dict"][self.player_name].status == "lost":
            raise

        allowable_actions = set()

        # get player_idx
        for player_idx, player in enumerate(current_gameboard["players"]):
            if player.player_name == self.player_name:
                break

        # check if it is fold already
        if current_gameboard["board"].players_last_move_list[player_idx] == Action.FOLD:
            raise

        # 1. fold
        allowable_actions.add(fold)  # can fold at any time

        # bet, raise_bet, call, chcek, all_in

        if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
            raise_amount = current_gameboard["small_bet"]
        elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
            raise_amount = current_gameboard["big_bet"]
        else:
            raise

        already_bet = current_gameboard["board"].player_pot[player.player_name]
        current_bet_count = current_gameboard["board"].current_bet_count
        current_raise_count = current_gameboard["board"].current_raise_count

        if current_bet_count == 0:
            # bet(all_in)
            if self.current_cash <= raise_amount:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(bet)
            # check
            allowable_actions.add(check)

        elif current_bet_count == 1 and current_raise_count < current_gameboard["max_raise_count"]:
            # exception: BB in pre-flop
            if (
                current_gameboard["board"].cur_phase == Phase.PRE_FLOP
                and current_raise_count == 0
                and current_gameboard["board"].players_last_move_list[player_idx] == Action.BIG_BLIND
            ):
                allowable_actions.add(check)

            # call, all_in
            bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
            if bet_to_follow == 0:
                raise

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)

            # raise_bet, all_in
            required_raise_amount = raise_amount * (current_bet_count + current_raise_count + 1) - already_bet
            if self.current_cash <= required_raise_amount:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(raise_bet)

        elif current_bet_count == 1 and current_raise_count == current_gameboard["max_raise_count"]:
            # call, all_in

            bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
            if bet_to_follow == 0:
                raise

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)

        else:
            raise

        logger.debug("allowable_actions = " + ", ".join([action.__name__ for action in allowable_actions]))

        return allowable_actions

        logger.debug("allowable_actions = " + ", ".join([action.__name__ for action in allowable_actions]))

        return allowable_actions

    def compute_allowable_turn_actions(self, current_gameboard):
        """
        first player: bet or check

        Args:
        current_gameboard

        Returns:
            bool: True if betting is over

        """
        if current_gameboard["players_dict"][self.player_name].status == "lost":
            raise

        allowable_actions = set()

        # get player_idx
        for player_idx, player in enumerate(current_gameboard["players"]):
            if player.player_name == self.player_name:
                break

        # check if it is fold already
        if current_gameboard["board"].players_last_move_list[player_idx] == Action.FOLD:
            raise

        # 1. fold
        allowable_actions.add(fold)  # can fold at any time

        # bet, raise_bet, call, chcek, all_in

        if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
            raise_amount = current_gameboard["small_bet"]
        elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
            raise_amount = current_gameboard["big_bet"]
        else:
            raise

        already_bet = current_gameboard["board"].player_pot[player.player_name]
        current_bet_count = current_gameboard["board"].current_bet_count
        current_raise_count = current_gameboard["board"].current_raise_count

        if current_bet_count == 0:
            # bet(all_in)
            if self.current_cash <= raise_amount:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(bet)
            # check
            allowable_actions.add(check)

        elif current_bet_count == 1 and current_raise_count < current_gameboard["max_raise_count"]:

            # exception: BB in pre-flop
            if (
                current_gameboard["board"].cur_phase == Phase.PRE_FLOP
                and current_raise_count == 0
                and current_gameboard["board"].players_last_move_list[player_idx] == Action.BIG_BLIND
            ):
                allowable_actions.add(check)

            # call, all_in
            bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
            if bet_to_follow == 0:
                raise

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)

            # raise_bet, all_in
            required_raise_amount = raise_amount * (current_bet_count + current_raise_count + 1) - already_bet
            if self.current_cash <= required_raise_amount:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(raise_bet)

        elif current_bet_count == 1 and current_raise_count == current_gameboard["max_raise_count"]:
            # call, all_in

            bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
            if bet_to_follow == 0:
                raise

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)

        else:
            raise

        logger.debug("allowable_actions = " + ", ".join([action.__name__ for action in allowable_actions]))

        return allowable_actions

    def compute_allowable_river_actions(self, current_gameboard):
        """
        first player: bet or check

        Args:
        current_gameboard

        Returns:
            bool: True if betting is over

        """
        if current_gameboard["players_dict"][self.player_name].status == "lost":
            raise

        allowable_actions = set()

        # get player_idx
        for player_idx, player in enumerate(current_gameboard["players"]):
            if player.player_name == self.player_name:
                break

        # check if it is fold already
        if current_gameboard["board"].players_last_move_list[player_idx] == Action.FOLD:
            raise

        # 1. fold
        allowable_actions.add(fold)  # can fold at any time

        # bet, raise_bet, call, chcek, all_in

        if current_gameboard["board"].cur_phase in [Phase.PRE_FLOP, Phase.FLOP]:
            raise_amount = current_gameboard["small_bet"]
        elif current_gameboard["board"].cur_phase in [Phase.TURN, Phase.RIVER]:
            raise_amount = current_gameboard["big_bet"]
        else:
            raise

        already_bet = current_gameboard["board"].player_pot[player.player_name]
        current_bet_count = current_gameboard["board"].current_bet_count
        current_raise_count = current_gameboard["board"].current_raise_count

        if current_bet_count == 0:
            # bet(all_in)
            if self.current_cash <= raise_amount:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(bet)
            # check
            allowable_actions.add(check)

        elif current_bet_count == 1 and current_raise_count < current_gameboard["max_raise_count"]:

            # exception: BB in pre-flop
            if (
                current_gameboard["board"].cur_phase == Phase.PRE_FLOP
                and current_raise_count == 0
                and current_gameboard["board"].players_last_move_list[player_idx] == Action.BIG_BLIND
            ):
                allowable_actions.add(check)

            # call, all_in
            bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
            if bet_to_follow == 0:
                raise

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)

            # raise_bet, all_in
            required_raise_amount = raise_amount * (current_bet_count + current_raise_count + 1) - already_bet
            if self.current_cash <= required_raise_amount:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(raise_bet)

        elif current_bet_count == 1 and current_raise_count == current_gameboard["max_raise_count"]:
            # call, all_in

            bet_to_follow = raise_amount * (current_bet_count + current_raise_count) - already_bet
            if bet_to_follow == 0:
                raise

            if self.current_cash <= bet_to_follow:
                allowable_actions.add(all_in)
            else:
                allowable_actions.add(call)

        else:
            raise

        logger.debug("allowable_actions = " + ", ".join([action.__name__ for action in allowable_actions]))

        return allowable_actions

        logger.debug("allowable_actions = " + ", ".join([action.__name__ for action in allowable_actions]))

        return allowable_actions

    def make_pre_flop_moves(self, current_gameboard):
        """
        player takes actions in pre-flop round
        :param current_gameboard:
        :return:
        """
        logger.debug(f"{self.player_name} currently in pre-flop round")
        allowable_actions = self.compute_allowable_pre_flop_actions(current_gameboard=current_gameboard)

        action_to_execute, parameters = self.agent.make_pre_flop_moves(self, current_gameboard, allowable_actions)
        # current_gameboard['player_last_move'] = Action[action_to_execute.__name__]

        # add to game history
        current_gameboard["history"]["function"].append(self.agent.make_pre_flop_moves)
        params = dict()
        params["player"] = self
        params["current_gameboard"] = current_gameboard
        params["allowable_moves"] = allowable_actions
        current_gameboard["history"]["param"].append(params)
        current_gameboard["history"]["return"].append((action_to_execute, parameters))

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_flop_moves(self, current_gameboard):
        """
        player takes actions in flop round
        :param current_gameboard:
        :return:
        """
        logger.debug(f"{self.player_name} currently in flop round")
        allowable_actions = self.compute_allowable_flop_actions(current_gameboard=current_gameboard)

        action_to_execute, parameters = self.agent.make_flop_moves(self, current_gameboard, allowable_actions)

        # current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard["history"]["function"].append(self.agent.make_flop_moves)
        params = dict()
        params["player"] = self
        params["current_gameboard"] = current_gameboard
        params["allowable_moves"] = allowable_actions
        current_gameboard["history"]["param"].append(params)
        current_gameboard["history"]["return"].append((action_to_execute, parameters))

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_turn_moves(self, current_gameboard):
        """
        player takes actions in turn round
        :param current_gameboard:
        :return:
        """
        logger.debug(f"{self.player_name} currently in turn round")
        allowable_actions = self.compute_allowable_turn_actions(current_gameboard=current_gameboard)

        action_to_execute, parameters = self.agent.make_turn_moves(self, current_gameboard, allowable_actions)

        # current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard["history"]["function"].append(self.agent.make_turn_moves)
        params = dict()
        params["player"] = self
        params["current_gameboard"] = current_gameboard
        params["allowable_moves"] = allowable_actions
        current_gameboard["history"]["param"].append(params)
        current_gameboard["history"]["return"].append((action_to_execute, parameters))

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_river_moves(self, current_gameboard):
        """
        player takes actions in river round
        :param current_gameboard:
        :return:
        """
        logger.debug(f"{self.player_name} currently in river round")
        allowable_actions = self.compute_allowable_river_actions(current_gameboard=current_gameboard)

        action_to_execute, parameters = self.agent.make_river_moves(self, current_gameboard, allowable_actions)

        # current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard["history"]["function"].append(self.agent.make_river_moves)
        params = dict()
        params["player"] = self
        params["current_gameboard"] = current_gameboard
        params["allowable_moves"] = allowable_actions
        current_gameboard["history"]["param"].append(params)
        current_gameboard["history"]["return"].append((action_to_execute, parameters))

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def _execute_action(self, action_to_execute, parameters, current_gameboard):
        """
        executing the action in each round for the player
        :param action_to_execute: action function to run
        :param parameters:
        :param current_gameboard:
        :return:
        """

        action_to_execute_funciton = self._action_decoder(action_to_execute)
        logger.debug(f"{self.player_name} executes its _execute_action function")
        if parameters:
            p = action_to_execute_funciton(**parameters)
            # add to game history
            current_gameboard["history"]["function"].append(action_to_execute)
            params = parameters.copy()
            current_gameboard["history"]["param"].append(params)
            current_gameboard["history"]["return"].append(p)
            return p
        else:
            p = action_to_execute_funciton()
            # add to game history
            current_gameboard["history"]["function"].append(action_to_execute)
            params = dict()
            current_gameboard["history"]["param"].append(params)
            current_gameboard["history"]["return"].append(p)

            return p

    def _action_decoder(self, action):
        """
        Decode integer action into function and the correspongind parameters
        Args:
            action(int): the action got from gym user
        Returns:
            action_function
        """

        if action.__name__ == "call":
            action_function = action_choices.call
        elif action.__name__ == "bet":
            action_function = action_choices.bet
        elif action.__name__ == "raise_bet":
            action_function = action_choices.raise_bet
        elif action.__name__ == "check":
            action_function = action_choices.check
        elif action.__name__ == "fold":
            action_function = action_choices.fold
        elif action.__name__ == "all_in":
            action_function = action_choices.all_in
        else:
            raise
        return action_function
