import gym
import numpy as np
import sys
import logging
from phase import Phase
from flag_config import flag_config_dict
from action import Action
import time
import dealer

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.novelty.rule1")

TIME_LIMIT = 10


class Rule1(gym.Wrapper):
    """
    This novelty, Rule1, restricted the time limit for players to decide in 10 seconds.
    """

    def __init__(self, env):

        super().__init__(env)

        # env = OrderEnforcing(env, disable_render_order_enforcing=True)

        env.reset = _alter_reset.__get__(env)
        # env.reset = getattr(sys.modules[__name__], '_alter_reset')
        # env.reset = types.MethodType(_alter_reset, env)
        # env.alter_reset.__func__.__name__ = 'reset'
        # env.step = _alter_step.__get__(env)
        env.step = getattr(sys.modules[__name__], "_alter_step")
        # env.step = types.MethodType(_alter_step, env)
        # env.step = _alter_step
        # env._alter_step.__func__.__name__ = 'step'
        sys.modules["player"].make_pre_flop_moves = getattr(sys.modules[__name__], "_alter_make_pre_flop_moves")
        sys.modules["player"].make_flop_moves = getattr(sys.modules[__name__], "_alter_make_flop_moves")
        sys.modules["player"].make_turn_moves = getattr(sys.modules[__name__], "_alter_make_turn_moves")
        sys.modules["player"].make_river_moves = getattr(sys.modules[__name__], "_alter_make_river_moves")


def _alter_reset(self, seed=None, options=None):
    # We need the following line to seed self.np_random
    # super().reset(seed=seed)
    np.random.seed(seed)
    self.game_elements = self.set_up_board(random_seed=seed)

    logger.debug("This tournament uses random_seed = " + str(seed))

    if self.render_mode == "human":
        self.render()

    # This is the start of tournament, no need to initialize game
    dealer.initialize_game(self.game_elements)

    #
    dealer.initialize_round(self.game_elements)

    # Deal the hole card
    dealer.check_and_deal_hole_cards(self.game_elements)

    # force_small_big_blind_bet
    blind_stop = dealer.force_small_big_blind_bet(self.game_elements)
    if blind_stop:
        dealer.conclude_tournament(self.game_elements, early_stop=True)
        return [self._get_obs(stopped=True), self._get_reward(), True, False, self._get_info(stopped=True)]

    # check player_1 lost or not
    if dealer.check_player1_lost(self.game_elements):
        dealer.conclude_tournament(self.game_elements, early_stop=True)
        return [self._get_obs(stopped=True), self._get_reward(), True, False, self._get_info(stopped=True)]

    # initialize_betting
    dealer.initialize_betting(self.game_elements)

    # start perform pre-flop betting
    self.step(0, True)
    # if self.game_elements['players'][self.game_elements['board'].current_betting_idx].player_name != 'player_1':
    #     self._betting()

    observation = self._get_obs()
    info = self._get_info()

    if self.render_mode == "human":
        self.render()

    self.game_elements["_timer_time"] = time.time()
    print(self.game_elements["_timer_time"])
    return observation, info


def _alter_step(self, action, game_start=False):
    """
    Args:

    Returns:

    Raises:


    """
    print(self.game_elements["_timer_time"])
    # get the player object
    if time.time() - self.game_elements["_timer_time"] > TIME_LIMIT:
        logger.debug(
            f"{self.player_name} surpassed the 10-second decision time limit, \
                conflicting with the novelty introduced by Rule 1."
        )
        print("aaaa")
        return [self._get_obs(stopped=True), self._get_reward(), True, False, self._get_info(stopped=True)]

    player = None
    for player_idx, player in enumerate(self.game_elements["players"]):
        if player.player_name == "player_1":
            break
    assert player is not None

    if not game_start:
        execute_res = self._execute_player_1_action(player, action)

        # invalid move -> lost immediately
        if execute_res:
            return execute_res

        if self.render_mode == "human":
            self.render()

    while True:
        # continue betting
        if not dealer.check_betting_over(self.game_elements):

            # continue betting
            is_over = self._betting()

            if not is_over and self.game_elements["board"].players_last_move_list[player_idx] not in [
                Action.FOLD,
                Action.ALL_IN,
                Action.ALL_IN_ALREADY,
            ]:
                if self.render_mode == "human":
                    self.render()
                logger.debug(player.player_name + " start to move with cash " + str(player.current_cash))
                # log bet info
                self._log_board_before_decision(player)

                return self._get_obs(), self._get_reward(), False, False, self._get_info()
            elif not is_over:
                # player_1 fold
                continue
        else:

            early_stop = dealer.conclude_round(self.game_elements)
            if not early_stop:
                # The betting is over, change the phase
                new_phase = dealer.change_phase(self.game_elements)

            #

            if early_stop or new_phase == Phase.PRE_FLOP:
                # conclude this game
                if not early_stop:
                    dealer.log_best_card(self.game_elements)
                    dealer.log_ranking(self.game_elements)
                terminated, truncated = dealer.conclude_game(self.game_elements)

                if terminated or truncated:
                    dealer.conclude_tournament(self.game_elements)
                    if self.render_mode == "human":
                        self.render(stopped=True)

                    return self._get_obs(stopped=True), self._get_reward(), terminated, truncated, self._get_info(stopped=True)

                # showdown:
                if self.render_mode == "human":
                    self.render(stopped=True, showdown=True)
                    time.sleep(3)

                # srart the new game
                #
                dealer.initialize_game(self.game_elements)

                #
                dealer.initialize_round(self.game_elements)

                # Deal the hole card
                dealer.check_and_deal_hole_cards(self.game_elements)

                # force_small_big_blind_bet
                blind_stop = dealer.force_small_big_blind_bet(self.game_elements)
                if blind_stop:
                    dealer.conclude_tournament(self.game_elements, early_stop=True)
                    return [self._get_obs(stopped=True), self._get_reward(), True, False, self._get_info(stopped=True)]

                # check player_1 lost or not
                if dealer.check_player1_lost(self.game_elements):
                    dealer.conclude_tournament(self.game_elements, early_stop=True)
                    return [self._get_obs(stopped=True), self._get_reward(), True, False, self._get_info(stopped=True)]

                # initialize_betting
                dealer.initialize_betting(self.game_elements)
            elif new_phase != Phase.PRE_FLOP:

                dealer.initialize_round(self.game_elements)

                # deal community card
                dealer.check_and_deal_community_card(self.game_elements)

                # initialize_betting
                dealer.initialize_betting(self.game_elements)

                # betting
                is_over = self._betting()
                # if self.render_mode == "human":
                #    self.render()

                if not is_over and self.game_elements["board"].players_last_move_list[player_idx] not in [
                    Action.FOLD,
                    Action.ALL_IN,
                    Action.ALL_IN_ALREADY,
                ]:
                    if self.render_mode == "human":
                        self.render()
                    logger.debug(player.player_name + " start to move with cash " + str(player.current_cash))
                    # log bet info
                    self._log_board_before_decision(player)
                    return self._get_obs(), self._get_reward(), False, False, self._get_info()


def _alter_make_pre_flop_moves(self, current_gameboard):
    """
    player takes actions in pre-flop round
    :param current_gameboard:
    :return:
    """
    logger.debug(f"{self.player_name} currently in pre-flop round")
    allowable_actions = self.compute_allowable_pre_flop_actions(current_gameboard=current_gameboard)

    current_gameboard["_timer_time"] = time.time()
    action_to_execute, parameters = self.agent.make_pre_flop_moves(self, current_gameboard, allowable_actions)

    if time.time() - current_gameboard["_timer_time"] <= TIME_LIMIT:
        # current_gameboard['player_last_move'] = Action[action_to_execute.__name__]

        # add to game history
        current_gameboard["history"]["function"].append(self.agent.make_pre_flop_moves)
        params = dict()
        params["player"] = self
        params["current_gameboard"] = current_gameboard
        params["allowable_moves"] = allowable_actions
        current_gameboard["history"]["param"].append(params)
        current_gameboard["history"]["return"].append((action_to_execute, parameters))

        code = self._execute_action(action_to_execute, parameters, current_gameboard)

    else:
        logger.debug(
            f"{self.player_name} surpassed the 10-second decision time limit, \
                conflicting with the novelty introduced by Rule 1."
        )
        code = flag_config_dict["failure_code"]

    return code


def _alter_make_flop_moves(self, current_gameboard):
    """
    player takes actions in flop round
    :param current_gameboard:
    :return:
    """
    logger.debug(f"{self.player_name} currently in flop round")
    allowable_actions = self.compute_allowable_flop_actions(current_gameboard=current_gameboard)

    current_gameboard["_timer_time"] = time.time()
    action_to_execute, parameters = self.agent.make_flop_moves(self, current_gameboard, allowable_actions)

    if time.time() - current_gameboard["_timer_time"] <= TIME_LIMIT:
        # current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard["history"]["function"].append(self.agent.make_flop_moves)
        params = dict()
        params["player"] = self
        params["current_gameboard"] = current_gameboard
        params["allowable_moves"] = allowable_actions
        current_gameboard["history"]["param"].append(params)
        current_gameboard["history"]["return"].append((action_to_execute, parameters))

        code = self._execute_action(action_to_execute, parameters, current_gameboard)

    else:
        logger.debug(
            f"{self.player_name} surpassed the 10-second decision time limit, \
            conflicting with the novelty introduced by Rule 1."
        )
        code = flag_config_dict["failure_code"]

    return code


def _alter_make_turn_moves(self, current_gameboard):
    """
    player takes actions in turn round
    :param current_gameboard:
    :return:
    """
    logger.debug(f"{self.player_name} currently in turn round")
    allowable_actions = self.compute_allowable_turn_actions(current_gameboard=current_gameboard)

    current_gameboard["_timer_time"] = time.time()
    action_to_execute, parameters = self.agent.make_turn_moves(self, current_gameboard, allowable_actions)

    if time.time() - current_gameboard["_timer_time"] <= TIME_LIMIT:
        # current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard["history"]["function"].append(self.agent.make_turn_moves)
        params = dict()
        params["player"] = self
        params["current_gameboard"] = current_gameboard
        params["allowable_moves"] = allowable_actions
        current_gameboard["history"]["param"].append(params)
        current_gameboard["history"]["return"].append((action_to_execute, parameters))

        code = self._execute_action(action_to_execute, parameters, current_gameboard)

    else:
        logger.debug(
            f"{self.player_name} surpassed the 10-second decision time limit, \
                conflicting with the novelty introduced by Rule 1."
        )
        code = flag_config_dict["failure_code"]

    return code


def _alter_make_river_moves(self, current_gameboard):
    """
    player takes actions in river round
    :param current_gameboard:
    :return:
    """
    logger.debug(f"{self.player_name} currently in river round")
    allowable_actions = self.compute_allowable_river_actions(current_gameboard=current_gameboard)

    current_gameboard["_timer_time"] = time.time()
    action_to_execute, parameters = self.agent.make_river_moves(self, current_gameboard, allowable_actions)

    if time.time() - current_gameboard["_timer_time"] <= TIME_LIMIT:
        # current_gameboard['player_last_move'] = action_to_execute.__name__

        # add to game history
        current_gameboard["history"]["function"].append(self.agent.make_river_moves)
        params = dict()
        params["player"] = self
        params["current_gameboard"] = current_gameboard
        params["allowable_moves"] = allowable_actions
        current_gameboard["history"]["param"].append(params)
        current_gameboard["history"]["return"].append((action_to_execute, parameters))

        code = self._execute_action(action_to_execute, parameters, current_gameboard)

    else:
        logger.debug(
            f"{self.player_name} surpassed the 10-second decision time limit, \
                conflicting with the novelty introduced by Rule 1."
        )
        code = flag_config_dict["failure_code"]

    return code
