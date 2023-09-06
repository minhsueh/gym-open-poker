import initialize_game_elements
from agent import Agent
from helper_functions import *
from novelty_distributions import *
import numpy as np
import csv
from collections import defaultdict
from flag_config import flag_config_dict
import json

# import agents
from agents import example_agent_check_fold, example_agent_random, example_agent_call, example_agent_raise_bet
from agents import agent_call_AJ, agent_raise_AJ, agent_call_toppair_AJ, agent_raise_aggressive_AJ
from agents import agent_call_AJ_flop, background_agent_v1, background_agent_v2


def simulate_game_instance(game_elemets, max_hands=50, history_log_file=None, np_seed=2):
    """
    Simulate a game instance
    :param game_elemets:
    :param max_hands:
    :param history_log_file:
    :param np_seed:
    :return:
    """
    print(f'We are now in simulate_game_instance. The seed is {np_seed}')
    np.random.seed(np_seed)
    np.random.shuffle(game_elemets['players'])
    np.random.shuffle(game_elemets['deck'])

    # truncate final cash result csv file
    names = sorted(game_elemets['players_dict'].keys())

    winner = None
    game_elemets['cur_phase'] = 'pre_flop_phase'  # start from pre-flop round
    board = game_elemets['board']  # board object
    hands = 0  # record number of hands in a game instance; break if larger than max_hand
    print_cash_info(game_elemets)  # print cash info before game start

    cash_res = defaultdict(list)

    # players have to pay buy-in amount to join this table
    for p in game_elemets['players']:
        if p.current_cash < board.buy_in_amount:
            print(f'{p.player_name} does not have enough cash to pay buy-in for this table')
            p.assign_status('lost')
        else:
            print(f'{p.player_name} pays ${board.buy_in_amount} buy-in and be ready to player Texas Holdem!')
            board.charge_buy_in(p, game_elemets)
    print_cash_info(game_elemets)

    for p in game_elemets['players']:
        cash_res[p.player_name].append(p.current_cash)

    while True:
        if game_elemets['cur_phase'] == 'pre_flop_phase':
            print(f'Current hand in game: {hands}')
            print('================= Board dealing hole cards and force to bet =================')

            # deal hole cards and small/big blind forced to bet at this time
            active_player = 0
            for player in game_elemets['players']:
                if player.status == 'waiting_for_move':
                    board.deal_hole_cards(player, game_elemets['cur_phase'], game_elemets)
                if active_player == 0:  # position of small blind in queue
                    if player.current_cash < game_elemets['small_blind_amount']:
                        print(f'{player.player_name} does not have chips to pay, assign to lost')
                        # player.assign_to_fold(game_elemets)
                        player.assign_status(game_elemets, 'lost')
                        continue
                    player.assign_small_blind(current_gameboard=game_elemets, assign_to=True)
                    player.force_bet_small_blind(game_elemets)
                elif active_player == 1:  # position of big blind in queue
                    if player.current_cash < game_elemets['small_blind_amount'] * game_elemets['big_blind_pay_from_baseline']:
                        print(f'{player.player_name} does not have chips to pay, assign to lost')
                        # player.assign_to_fold(game_elemets)
                        player.assign_status(game_elemets, 'lost')
                        continue
                    player.assign_big_blind(current_gameboard=game_elemets, assign_to=True)
                    player.force_bet_big_blind(game_elemets)
                active_player += 1
                print(f'{player.player_name} now moves into pre-flop round')

            # first player be small blind, second player be big blind
            print('================= This is pre-flop round =================')
            blind_list = [game_elemets['players'][0], game_elemets['players'][1]]
            for player in list(game_elemets['players'])[2:] + blind_list:
                if player.is_fold or player.status == 'lost' or player.is_all_in:
                    print(f'{player.player_name} already fold/lost/all-in previously, next player...')
                    continue
                if board.num_active_player_on_table <= 1:  # possible all players except one fold
                    print('Board: only 1 player left in the game, concluding the game')
                    end_game_and_begin_next(current_gameboard=game_elemets)
                    break

                if player.status == 'waiting_for_move':
                    code = player.make_pre_flop_moves(current_gameboard=game_elemets)
                    if code == flag_config_dict['failure_code']:  # if action failed, assign player to fold, or lost?
                        print(f'Board: {player.player_name} tries an invalid move, assign to lost')
                        # player.assign_to_fold(game_elemets)
                        player.assign_status(game_elemets, 'lost')
                        continue

                    board.players_made_decisions.append(player)  # add player who has made decision to board
                    print(f'Board: total cash on the table ---> {board.total_cash_on_table}')
                    print(f'{player.player_name} finished its pre-flop round')

            game_elemets['cur_phase'] = 'flop_phase'

        elif game_elemets['cur_phase'] == 'flop_phase':
            print('================= This is flop round =================')
            board.deal_community_card(game_elemets['cur_phase'], game_elemets)

            for player in game_elemets['players']:
                if player.is_fold or player.status == 'lost' or player.is_all_in:
                    print(f'{player.player_name} already fold/lost/all-in previously, next player...')
                    continue
                if board.num_active_player_on_table <= 1:
                    print('Board: only 1 player left in the game, concluding the game')
                    end_game_and_begin_next(current_gameboard=game_elemets)
                    break

                if player.status == 'waiting_for_move':
                    code = player.make_flop_moves(current_gameboard=game_elemets)
                    if code == flag_config_dict['failure_code']:
                        print(f'Board: {player.player_name} tries an invalid move, assign to lost')
                        # player.assign_to_fold(game_elemets)
                        player.assign_status(game_elemets, 'lost')
                        continue

                    board.players_made_decisions.append(player)
                    print(f'Board: total cash on the table ---> {board.total_cash_on_table}')
                    print(f'{player.player_name} finished its flop round')

            game_elemets['cur_phase'] = 'turn_phase'

        elif game_elemets['cur_phase'] == 'turn_phase':
            print('================= This is turn round =================')
            board.deal_community_card(game_elemets['cur_phase'], game_elemets)

            for player in game_elemets['players']:
                if player.is_fold or player.status == 'lost' or player.is_all_in:
                    print(f'{player.player_name} already fold/lost/all-in previously, next player...')
                    continue
                if board.num_active_player_on_table <= 1:
                    print('Board: only 1 player left in the game, concluding the game')
                    end_game_and_begin_next(current_gameboard=game_elemets)
                    break

                if player.status == 'waiting_for_move':
                    code = player.make_turn_moves(current_gameboard=game_elemets)
                    if code == flag_config_dict['failure_code']:
                        print(f'Board: {player.player_name} tries an invalid move, assign to lost')
                        # player.assign_to_fold(game_elemets)
                        player.assign_status(game_elemets, 'lost')
                        continue

                    board.players_made_decisions.append(player)
                    print(f'Board: total cash on the table ---> {board.total_cash_on_table}')
                    print(f'{player.player_name} finished its turn round')

            game_elemets['cur_phase'] = 'river_phase'

        elif game_elemets['cur_phase'] == 'river_phase':
            print('================= This is river round =================')
            board.deal_community_card(game_elemets['cur_phase'], game_elemets)

            for player in game_elemets['players']:
                if player.is_fold or player.status == 'lost' or player.is_all_in:
                    print(f'{player.player_name} already fold/lost/all-in previously, next player...')
                    continue
                if board.num_active_player_on_table <= 1:
                    print('Board: only 1 player left in the game, concluding the game')
                    end_game_and_begin_next(current_gameboard=game_elemets)
                    break

                if player.status == 'waiting_for_move':
                    code = player.make_river_moves(current_gameboard=game_elemets)
                    if code == flag_config_dict['failure_code']:
                        print(f'Board: {player.player_name} tries an invalid move, assign to lost')
                        # player.assign_to_fold(game_elemets)
                        player.assign_status(game_elemets, 'lost')
                        continue

                    board.players_made_decisions.append(player)
                    print(f'Board: total cash on the table ---> {board.total_cash_on_table}')
                    print(f'{player.player_name} finished its river round')

            game_elemets['cur_phase'] = 'concluding_phase'

        elif game_elemets['cur_phase'] == 'concluding_phase':
            print('================= This is shutdown phase =================')

            # show players' hands if there are more than one player left in the game
            if board.num_active_player_on_table > 1:
                for player in game_elemets['players']:
                    if player.is_fold or player.status == 'lost':  # all-in condition should not be there
                        print(f'{player.player_name} already fold/lost previously, next player...')
                        continue
                    # probably need to make this action done by board not by player
                    # maybe need to change later
                    if player.status == 'waiting_for_move':
                        player.make_computing_best_hand_moves(current_gameboard=game_elemets)
                        board.players_made_decisions.append(player)
                        print(f'{player.player_name} finished its concluding phase')

                # calculate winner among players still on the table
                winners = game_elemets['find_winner'](game_elemets)
            else:
                # only player left should be winner, and do not show its hole cards
                winners = find_only_left_winner(game_elemets)

            print(f'Board: winner(s) of this game is ---> {"; ".join(winners)}')
            if len(winners) > 1:
                print(f'Board: there are more than one winner, split pot for them')
                split_pot_for_euqal_hand(game_elemets, winners)
            elif winners:
                game_elemets['assign_pot_to_only_winner'](game_elemets, winners[0])
                # assign_pot_to_only_winner(game_elemets, winners[0])
            else:
                print('Error: there are no winner')
                raise Exception
            # print cash info after assign pot to winners
            print_cash_info(current_gameboard=game_elemets)

            for p in game_elemets['players_dict'].values():
                if p.status == 'lost':
                    cash_res[p.player_name].append(0)
                else:
                    cash_res[p.player_name].append(p.current_cash)

            # change position of players
            first_player = game_elemets['players'].popleft()
            game_elemets['players'].append(first_player)

            # check if any players should leave the table
            for p in game_elemets['players']:
                if p.current_cash <= 0:
                    p.assign_status(game_elemets, 'lost')
            remove_player_from_queue_if_lost(game_elemets)

            # reset the board, players, and shuffle deck
            board.reset_board_each_game(game_elemets)
            for player in game_elemets['players']:
                player.reset_player_each_game(game_elemets)
            print('Board: have reset board, players, and shuffle for next game!')

            game_elemets['cur_phase'] = 'pre_flop_phase'  # for start next game
            game_elemets['hands_of_players'].append(dict())
            hands += 1

        # NOTICE!!! this is like out of turn moves in monopoly
        # after the end of each round, if players checked and decide to continue, they should put enough money to
        # match the highest bet on the table
        if game_elemets['cur_phase'] != 'pre_flop_phase' and board.num_active_player_on_table > 1:
            print('================= This is continue game phase =================')
            cur_bet_on_table = board.total_cash_on_table

            # if is pre-flop round, loop should start from first player on the left of big blind
            if game_elemets['cur_phase'] == 'flop_phase':
                blind_list = [game_elemets['players'][0]] + [game_elemets['players'][1]]
                player_list = list(game_elemets['players'])[2:] + blind_list
            else:
                player_list = game_elemets['players']

            for p in player_list:
                if p.is_fold or p.status == 'lost' or p.is_all_in:
                    print(f'{p.player_name} already fold/lost/all-in previously, next player...')
                    continue
                if board.num_active_player_on_table <= 1:
                    print('Board: only 1 player left in the game, concluding the game')
                    end_game_and_begin_next(current_gameboard=game_elemets)
                    break

                # only allow to make moves if player's current bet is smaller than highest bet on the table
                if p.status == 'waiting_for_move' and p.bet_amount_each_round < board.current_highest_bet:
                    code = p.make_continue_game_moves(current_gameboard=game_elemets)
                    if code == flag_config_dict['failure_code']:
                        print(f'Board: {p.player_name} tries an invalid move, assign to lost')
                        # p.assign_to_fold(game_elemets)
                        p.assign_status(game_elemets, 'lost')
                        continue

            if board.total_cash_on_table > cur_bet_on_table:
                print(f'Board: total cash on the table ---> {board.total_cash_on_table}')
            else:
                print('Board: nothing happened for this phase as no players need to match/call bet')

        # if all players fold except one, we should concluding game immediately
        if board.num_active_player_on_table <= 1:
            print('Board: all players fold except one, concluding game...')
            end_game_and_begin_next(current_gameboard=game_elemets, show_community_cards=False)
        # if there is a player go all-in, then we should concluding the game
        elif board.num_active_player_on_table - len([p for p in game_elemets['players'] if p.is_all_in]) <= 1:
            print('Board: all players go all-in or only one remaining, concluding game...')
            end_game_and_begin_next(current_gameboard=game_elemets, show_community_cards=True)

        # reset game board and players per round
        board.reset_board_each_round(game_elemets)
        for p in game_elemets['players']:
            p.reset_player_each_round(game_elemets)

        # game instance termination condition below
        num_player_left, candidate = num_players_left(current_gameboard=game_elemets)
        if not num_player_left:
            print('No player left in the game instance, something went wrong')
            raise Exception
        if num_player_left == 1:
            print('Only 1 player left, finish the game')
            winner = candidate
            break
        if hands >= max_hands:
            print('Reach the max number of hands, finish the game')
            winner = player_with_most_cash(game_elemets)
            break

    # with open('experiment_res/cash_res.csv', 'w', newline='') as f:
    #     writer = csv.writer(f)
    #     column_name = ['hand'+str(i) for i in range(max_hands + 1)]
    #     column_name = [''] + column_name
    #     writer.writerow(column_name)
    #     for key in sorted(cash_res.keys()):
    #         row = [key] + cash_res[key]
    #         writer.writerow(row)

    # for compute average cash of all tournaments
    # for k, v in cash_res.items():
    #     while len(v) < 100:
    #         v.append(0)
    #     cash_res[k] = v
    all_tournaments_cash_res.append(cash_res)

    with open('experiment_res/final_cash.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        row = [''] + [game_elemets['players_dict'][name].current_cash for name in names]
        writer.writerow(row)

    with open('experiment_res/cash.json', 'a') as f:
        json.dump({name:game_elemets['players_dict'][name].current_cash for name in names}, f)
        f.write('\n')

    return winner.player_name if winner else None


def set_up_board(player_decision_agents):
    """
    The function to set up game elements`
    :param player_decision_agents: dictionary of player name and its corresponding agent
    :return: game elements
    :rtype: dict
    """
    return initialize_game_elements.initialize_board(player_decision_agents)


# def play_game(number_players, player_agent_list):
def play_game(max_hands=50, np_seed=2):
    """
    Use this function if you want to test a single game instance and control lots of things. For experiments, we will directly
    call some of the functions in gameplay from test_harness.py.

    This is where everything begins. Assign decision agents to your players, set up the board and start simulating! You can
    control any number of players you like, and assign the rest to the simple agent.

    :return: String. the name of the player who won the game, if there was a winner, otherwise None.
    """
    player_decision_agents = dict()
    player_decision_agents['player_raise'] = Agent(**example_agent_raise_bet.decision_agent_methods)
    player_decision_agents['player_call'] = Agent(**example_agent_call.decision_agent_methods)
    player_decision_agents['player_random'] = Agent(**example_agent_random.decision_agent_methods)
    player_decision_agents['agent_call_AJ'] = Agent(**agent_call_AJ.decision_agent_methods)
    player_decision_agents['agent_raise_AJ'] = Agent(**agent_raise_AJ.decision_agent_methods)
    player_decision_agents['agent_raise_aggressive_AJ'] = Agent(**agent_raise_aggressive_AJ.decision_agent_methods)
    player_decision_agents['agent_call_top_pair_AJ'] = Agent(**agent_call_toppair_AJ.decision_agent_methods)
    player_decision_agents['agent_call_AJ_flop'] = Agent(**agent_call_AJ_flop.decision_agent_methods)
    player_decision_agents['background_agent_v1'] = Agent(**background_agent_v1.decision_agent_methods)

    # Get game elements to be ready to run
    game_elements = set_up_board(player_decision_agents)
    print('Finished set up game board...')

    for player_name, agent_object in player_decision_agents.items():
        if agent_object.startup() == flag_config_dict['failure_code']:
            print(f'{player_name} is not properly initialized. Cannot play the game')
            return None
    winner = simulate_game_instance(game_elemets=game_elements, max_hands=max_hands, np_seed=np_seed)
    for player_name, agent_object in player_decision_agents.items():
        if agent_object.shutdown() == flag_config_dict['failure_code']:
            print(f'{player_name} is not properly shutdown. ')
            return None

    print(f'All players have benn shutdown. Game over. The winner is: {winner}')
    return winner


def play_game_in_tournament(max_hands=50, np_seed=2, inject_novelty_function=None, player_decision_agents=None):
    """
    Play one game instance with available to inject novelty during the tournament
    :param max_hands: once reach this number, the game instance should be terminated
    :param np_seed: numpy seed
    :param inject_novelty_function: the function you would like to inject
    :return: string winner name
    """
    if not player_decision_agents:
        player_decision_agents = dict()
        player_decision_agents['player_raise'] = Agent(**example_agent_raise_bet.decision_agent_methods)
        player_decision_agents['player_call'] = Agent(**example_agent_call.decision_agent_methods)
        player_decision_agents['player_random'] = Agent(**example_agent_random.decision_agent_methods)
        player_decision_agents['agent_call_AJ'] = Agent(**agent_call_AJ.decision_agent_methods)
        player_decision_agents['agent_raise_AJ'] = Agent(**agent_raise_AJ.decision_agent_methods)
        player_decision_agents['agent_raise_aggressive_AJ'] = Agent(**agent_raise_aggressive_AJ.decision_agent_methods)
        player_decision_agents['agent_call_top_pair_AJ'] = Agent(**agent_call_toppair_AJ.decision_agent_methods)
        player_decision_agents['agent_call_AJ_flop'] = Agent(**agent_call_AJ_flop.decision_agent_methods)
        player_decision_agents['background_agent_v1'] = Agent(**background_agent_v1.decision_agent_methods)
        player_decision_agents['background_agent_v2'] = Agent(**background_agent_v2.decision_agent_methods)

    # Get game elements to be ready to run
    game_elements = set_up_board(player_decision_agents)
    print('Finished set up game board...')

    if inject_novelty_function:
        inject_novelty_function(game_elements)
        print('Successfully injecting novelty...')

    for player_name, agent_object in player_decision_agents.items():
        if agent_object.startup() == flag_config_dict['failure_code']:
            print(f'{player_name} is not properly initialized. Cannot play the game')
            return None
    winner = simulate_game_instance(game_elemets=game_elements, max_hands=max_hands, np_seed=np_seed)
    for player_name, agent_object in player_decision_agents.items():
        if agent_object.shutdown() == flag_config_dict['failure_code']:
            print(f'{player_name} is not properly shutdown. ')
            return None

    print(f'All players have been shutdown. Game over. The winner is: {winner}')
    return winner


def compute_avg_cash_over_tournament(num_hands=100, num_games=1000, inject_novelty_function=None):
    """
    Compute average cash per hand in one tournament. With the given number of hands and number of games, for example 100
    num_hands and 1000 num_games, the output csv file would contain average cash per hand among those 1000 games in the
    tournament.
    :param num_hands: max number of hands in each game
    :param num_games: number of games in one tournament
    :param inject_novelty_function:
    :return: None
    """
    for seed in range(num_games):
        w = play_game_in_tournament(max_hands=num_hands, np_seed=seed, inject_novelty_function=inject_novelty_function)
        # w = play_game_in_tournament(max_hands=num_hands, np_seed=seed)
        # if seed < 50:
        #     w = play_game_in_tournament(max_hands=num_hands, np_seed=seed)
        # else:
        #     w = play_game_in_tournament(max_hands=num_hands, np_seed=seed, inject_novelty_function=exchange_hands_novelty)
    # winners[w] += 1
    # print(winners)

    res = defaultdict(list)
    names = all_tournaments_cash_res[0].keys()
    for cur_dict in all_tournaments_cash_res:
        for name in names:
            res[name].append(cur_dict[name])
    for k, v in res.items():
        temp = [num/num_games for num in list(map(sum, zip(*v)))]
        res[k] = temp

    with open('./experiment_res/cash_sum.csv', 'w') as f:
        writer = csv.writer(f)
        col = [str(i) for i in range(num_hands)]
        writer.writerow([''] + col)
        for name in sorted(names):
            row = [name] + res[name]
            writer.writerow(row)


# for recording cash after each hand in a tournament
all_tournaments_cash_res = list()

# Play one tournament without novelty
play_game(max_hands=100)
# play_game_in_tournament(max_hands=10)

# Play one tournament with novelty injection
# play_game_in_tournament(max_hands=10, inject_novelty_function=pay_insurance_after_hole_card)

# Compute average cash per hand in one tournament
# compute_avg_cash_over_tournament(inject_novelty_function=finish_flop_round)


