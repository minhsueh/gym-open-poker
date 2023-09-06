import gameplay
from collections import defaultdict, Counter
import numpy as np
from agent import Agent
from novelty_distributions import *
import csv
import json
from scipy import stats
import pandas as pd
import sys

# import agents
from agents import example_agent_check_fold, example_agent_random, example_agent_call, example_agent_raise_bet
from agents import agent_call_AJ, agent_raise_AJ, agent_call_toppair_AJ, agent_raise_aggressive_AJ
from agents import agent_call_AJ_flop, background_agent_v1, background_agent_v2

# import plot package
import seaborn as sns
import matplotlib.pyplot as plt
# sns.set_theme(style="whitegrid")


def plot_box_graph():
    novelties = {
        'nov': [exchange_hands_novelty, reorder_hand_ranking, reorder_numbers_ranking,
                royal_texas_version, finish_flop_round, cards_invisible_to_players, remove_rank_category,
                add_rank_category, draw_card_with_replacement],
        'undo': [None, None, None, None, undo_finish_flop_round, undo_draw_card, undo_draw_card, None, undo_draw_card],
        'novelty_names': ['exchange_hands_novelty', 'reorder_hand_ranking', 'reorder_numbers_ranking',
                          'royal_texas_version', 'finish_flop_round', 'hole_card_invisible',
                          'remove_one_hand_rank', 'adding_color_flush', 'draw_card_with_replacement']
    }

    # novelties = {
    #     'nov': [cards_invisible_to_players, remove_rank_category,
    #             add_rank_category, draw_card_with_replacement],
    #     'undo': [undo_draw_card, undo_draw_card, None, undo_draw_card],
    #     'novelty_names': ['hole_card_invisible',
    #                       'remove_one_hand_rank', 'adding_color_flush', 'draw_card_with_replacement']
    # }

    agents_collect = defaultdict(list)
    novelties_impact = defaultdict(list)
    output_json = []
    for i in range(len(novelties['nov'])):
        nov = novelties['nov'][i]
        undo = novelties['undo'][i]
        pre_cash, post_cash, pre_reaction, post_reaction, names = \
            build_matrix(max_hand=max_hand,
                         num_game_in_tournament=num_game_in_tournament,
                         inject_at=inject_at,
                         player_list=player_decision_agents,
                         compete_list=players_compete_itself,
                         novelty=nov,
                         undo_novelty=undo)

        for idx, name in enumerate(names):
            n = len(pre_cash[idx])
            # pre_mean = np.average([num for pos, num in enumerate(pre_cash[idx]) if pos != idx])
            # post_mean = np.average([num for pos, num in enumerate(post_cash[idx]) if pos != idx])
            # agents_collect['Cash Ratio'].extend([pre_mean, post_mean])
            agents_collect['Cash Ratio'].extend(pre_cash[idx] + post_cash[idx])
            agents_collect['Novelty Type'].extend(['Pre-Novelty'] * n + ['Post-Novelty'] * n)
            agents_collect['Players'].extend([idx] * 2 * n)

            output_json.append({
                'name': name,
                'name_idx': idx,
                'novelty_type': 'Pre-Novelty',
                'novelty_name': novelties['novelty_names'][i],
                'reaction': pre_reaction[idx],
                'cash_ratio': pre_cash[idx]
            })
            output_json.append({
                'name': name,
                'name_idx': idx,
                'novelty_type': 'Post-Novelty',
                'novelty_name': novelties['novelty_names'][i],
                'reaction': post_reaction[idx],
                'cash_ratio': post_cash[idx]
            })

        curr = []
        for row in range(len(names)):
            for col in range(row):
                curr.append(abs(pre_cash[row][col] - post_cash[row][col]))
                # novelties_impact['Value'].append(abs(pre_cash[row][col] - post_cash[row][col]))
                # novelties_impact['Novelties'].append(i)
        novelties_impact['Mean'].append(np.average(curr))
        novelties_impact['Std'].append(np.std(curr))
        novelties_impact['Novelties'].append(i)

    with open('/Users/hongyuli/Desktop/poker_paper_data/data/heads_up.json', 'w') as f:
        for line in output_json:
            json.dump(line, f)
            f.write('\n')

    # box plot for agents
    # df = pd.DataFrame(agents_collect)
    # ax = sns.boxplot(x="Players", y="Cash Ratio", hue="Novelty Type",
    #                  data=df, palette="Set3")
    # plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)
    # # plt.show()
    # plt.savefig(f'/Users/hongyuli/Desktop/box_plot.png', dpi=500)

    # global impact
    # df = pd.DataFrame(novelties_impact)
    # ax = sns.pointplot(x="Novelties", y="Mean", data=df, palette="Set3")
    # plt.savefig(f'/Users/hongyuli/Desktop/global_impact.png', dpi=500)


def print_win_ratio_std(arr):
    if arr:
        for k in sorted(arr.keys()):
            print(f'{k} --> std: {np.std(arr[k])}; win ratio: {sum(arr[k])/len(arr[k])}; count win: {sum(arr[k])}')
        print('avg of std:', sum([np.std(v) for v in arr.values()])/len(arr))
    else:
        print('computing win ratio and std with empty array')


def get_std_mean(title, matrix, n):
    under_matrix = [matrix[i][j] for i in range(n) for j in range(i)]
    mean = np.mean(under_matrix)
    std = np.std(under_matrix)
    print(f'{title} --> Mean: {mean}; Std: {std}')


def plot_heat_map(matrix, names, title):
    """

    :param matrix:
    :param names:
    :param title:
    :return:
    """
    # output matrix
    with open(f'/Users/hongyuli/Desktop/{title}.csv', 'w') as f:
        writer = csv.writer(f)
        header = [''] + names
        writer.writerow(header)
        for line, name in zip(matrix, names):
            writer.writerow([name] + line)

    # plot fig
    np_matrix = np.array(matrix)

    fig, ax = plt.subplots()
    im = ax.imshow(np_matrix)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(names)))
    ax.set_yticks(np.arange(len(names)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(names)
    ax.set_yticklabels(names)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(names)):
        for j in range(len(names)):
            text = ax.text(j, i, round(np_matrix[i, j], 2), ha="center", va="center", color="w", fontsize=8)

    ax.set_title(title)
    fig.tight_layout()
    # plt.show()
    plt.savefig(f'/Users/hongyuli/Desktop/{title}.png', dpi=500)


def run_tournament_with_novelty(max_hand, num_game_in_tournament, inject_at, player_decision_agents, novelty):
    pre_novelty = defaultdict(list)
    post_novelty = defaultdict(list)

    names = sorted(player_decision_agents.keys())
    with open('experiment_res/final_cash.csv', 'w+') as f:
        writer = csv.writer(f)
        column_name = [''] + [name for name in names]
        writer.writerow(column_name)

    seeds = [seed for seed in range(num_game_in_tournament)]
    for i in range(num_game_in_tournament):
        if i < inject_at:  # pre-novelty
            winner = gameplay.play_game_in_tournament(max_hands=max_hand,
                                                      np_seed=seeds[i],
                                                      player_decision_agents=player_decision_agents)
            if winner not in pre_novelty:
                pre_novelty[winner] = [0] * inject_at
            pre_novelty[winner][i] = 1
        else:  # post-novelty begin here
            if i == inject_at and novelty:
                with open('experiment_res/final_cash.csv', 'a') as f:
                    writer = csv.writer(f)
                    column_name = [''] + [name for name in names]
                    writer.writerow(column_name)
            winner = gameplay.play_game_in_tournament(max_hands=max_hand,
                                                      np_seed=seeds[i],
                                                      player_decision_agents=player_decision_agents,
                                                      inject_novelty_function=getattr(sys.modules[__name__], novelty))
            if winner not in post_novelty:
                post_novelty[winner] = [0] * (num_game_in_tournament - inject_at)
            post_novelty[winner][i-inject_at] = 1

    print_win_ratio_std(pre_novelty)
    print_win_ratio_std(post_novelty)


def build_matrix(max_hand, num_game_in_tournament, inject_at, player_list, compete_list, novelty, undo_novelty=None):
    n = len(player_list)  # length of matrix which should be a sqaure
    names = sorted(player_list.keys())
    name2idx = {name:i for i, name in enumerate(names)}

    with open('experiment_res/cash.json', 'w+') as f:
        print('Clearing previous cash json file')

    # rows and columns should be same order as string in names above
    pre_novelty_matrix_reaction = [[0] * n for _ in range(n)]
    post_novelty_matrix_reaction = [[0] * n for _ in range(n)]

    # rows and columns for final cash results
    pre_novelty_matrix_cash = [[0] * n for _ in range(n)]
    post_novelty_matrix_cash = [[0] * n for _ in range(n)]

    seeds = [seed for seed in range(num_game_in_tournament)]
    for i in range(len(names)):
        for j in range(i, len(names)):
            with open('experiment_res/cash.json', 'w+') as f:
                print('Clearing previous cash json file')

            player1 = names[i]
            player2 = names[j]

            if player1 == player2:
                cur_combination = {
                    player1 + '_1': player_list[player1],
                    player2 + '_2': compete_list[player2]
                }
            else:
                cur_combination = {
                    player1: player_list[player1],
                    player2: player_list[player2]
                }
            pre2cnt = {name:0 for name in cur_combination.keys()}
            post2cnt = {name:0 for name in cur_combination.keys()}

            # run tournament
            for seed in range(num_game_in_tournament):
                if seed < inject_at:
                    if undo_novelty:
                        winner = gameplay.play_game_in_tournament(max_hands=max_hand,
                                                                  np_seed=seeds[seed],
                                                                  player_decision_agents=cur_combination,
                                                                  inject_novelty_function=undo_novelty)
                    else:
                        winner = gameplay.play_game_in_tournament(max_hands=max_hand,
                                                                  np_seed=seeds[seed],
                                                                  player_decision_agents=cur_combination)
                    pre2cnt[winner] += 1
                else:
                    if seed == inject_at and novelty:
                        with open('experiment_res/cash.json', 'a') as f:
                            f.write('post-novelty\n')
                    winner = gameplay.play_game_in_tournament(max_hands=max_hand,
                                                              np_seed=seeds[seed],
                                                              player_decision_agents=cur_combination,
                                                              inject_novelty_function=novelty)
                    post2cnt[winner] += 1


            # record results into matrix
            if player1 == player2:  # diagonal
                pre_novelty_matrix_reaction[name2idx[player1]][name2idx[player2]] = \
                    sum(pre2cnt.values()) / 2 / inject_at
                post_novelty_matrix_reaction[name2idx[player1]][name2idx[player2]] = \
                    sum(post2cnt.values()) / 2 / (num_game_in_tournament - inject_at)
            else:
                pre_novelty_matrix_reaction[name2idx[player1]][name2idx[player2]] = pre2cnt[player1] / inject_at
                pre_novelty_matrix_reaction[name2idx[player2]][name2idx[player1]] = pre2cnt[player2] / inject_at
                post_novelty_matrix_reaction[name2idx[player1]][name2idx[player2]] = post2cnt[player1] / (num_game_in_tournament - inject_at)
                post_novelty_matrix_reaction[name2idx[player2]][name2idx[player1]] = post2cnt[player2] / (num_game_in_tournament - inject_at)

            # read cash file and compute results into matrix
            post_novelty_flag = False
            total_cash = 2000
            pre_novelty_player2cash = {name:0 for name in cur_combination.keys()}
            post_novelty_player2cash = {name:0 for name in cur_combination.keys()}
            with open('experiment_res/cash.json', 'r') as f:
                for line in f:
                    if line.strip() == 'post-novelty':
                        post_novelty_flag = True
                        continue

                    data = json.loads(line)
                    if not post_novelty_flag:  # pre-novelty
                        for player_name, cash in data.items():
                            pre_novelty_player2cash[player_name] += cash
                    else:  # post-novelty
                        for player_name, cash in data.items():
                            post_novelty_player2cash[player_name] += cash
            if player1 == player2:
                pre_novelty_matrix_cash[name2idx[player1]][name2idx[player2]] = 0.5
                post_novelty_matrix_cash[name2idx[player1]][name2idx[player2]] = 0.5
            else:
                pre_novelty_matrix_cash[name2idx[player1]][name2idx[player2]] = \
                    pre_novelty_player2cash[player1] / inject_at / total_cash
                pre_novelty_matrix_cash[name2idx[player2]][name2idx[player1]] = \
                    pre_novelty_player2cash[player2] / inject_at / total_cash
                post_novelty_matrix_cash[name2idx[player1]][name2idx[player2]] = \
                    post_novelty_player2cash[player1] / (num_game_in_tournament - inject_at) / total_cash
                post_novelty_matrix_cash[name2idx[player2]][name2idx[player1]] = \
                    post_novelty_player2cash[player2] / (num_game_in_tournament - inject_at) / total_cash


    # print std and mean under diagonal
    # get_std_mean('pre-reaction', pre_novelty_matrix_reaction, n)
    # get_std_mean('post-reaction', post_novelty_matrix_reaction, n)
    # get_std_mean('pre-cash', pre_novelty_matrix_cash, n)
    # get_std_mean('post-cash', post_novelty_matrix_cash, n)

    # save fig of reaction heat map and output matrix
    # plot_heat_map(pre_novelty_matrix_reaction, names, 'Pre-Novelty Reaction')
    # plot_heat_map(post_novelty_matrix_reaction, names, 'Post-Novelty Reaction')
    # plot_heat_map(pre_novelty_matrix_cash, names, 'Pre-Novelty Cash Ratio')
    # plot_heat_map(post_novelty_matrix_cash, names, 'Post-Novelty Cash Ratio')

    # student t-test
    # reaction_t_test_list = []
    # cash_t_test_list = []
    # for pre, post in zip(pre_novelty_matrix_reaction, post_novelty_matrix_reaction):
    #     t_stats, p_value = stats.ttest_rel(post, pre)
    #     reaction_t_test_list.append([t_stats, p_value])
    # for pre, post in zip(pre_novelty_matrix_cash, post_novelty_matrix_cash):
    #     t_stats, p_value = stats.ttest_rel(post, pre)
    #     cash_t_test_list.append([t_stats, p_value])

    # row_titles = ['t-stats', 'p-value']
    # with open('experiment_res/t-test-res.csv', 'w') as f:
    #     writer = csv.writer(f)
    #
    #     writer.writerow(['Reaction'] + names)
    #     for i, col in enumerate(zip(*reaction_t_test_list)):
    #         row = [row_titles[i]] + list(col)
    #         writer.writerow(row)
    #
    #     writer.writerow('')
    #     writer.writerow(['Cash'] + names)
    #     for i, col in enumerate(zip(*cash_t_test_list)):
    #         row = [row_titles[i]] + list(col)
    #         writer.writerow(row)
    return pre_novelty_matrix_cash, post_novelty_matrix_cash, pre_novelty_matrix_reaction, post_novelty_matrix_reaction, names


if __name__ == '__main__':
    max_hand = 100
    num_game_in_tournament = 20
    inject_at = 10

    player_decision_agents = dict()
    player_decision_agents['player_raise'] = Agent(**example_agent_raise_bet.decision_agent_methods)
    player_decision_agents['player_call'] = Agent(**example_agent_call.decision_agent_methods)
    player_decision_agents['player_random'] = Agent(**example_agent_random.decision_agent_methods)
    player_decision_agents['agent_call_AT'] = Agent(**agent_call_AJ.decision_agent_methods)
    player_decision_agents['agent_raise_AT'] = Agent(**agent_raise_AJ.decision_agent_methods)
    player_decision_agents['agent_raise_aggressive'] = Agent(**agent_raise_aggressive_AJ.decision_agent_methods)
    player_decision_agents['agent_call_top_pair'] = Agent(**agent_call_toppair_AJ.decision_agent_methods)
    player_decision_agents['agent_call_flop'] = Agent(**agent_call_AJ_flop.decision_agent_methods)
    player_decision_agents['background_agent_v1'] = Agent(**background_agent_v1.decision_agent_methods)
    player_decision_agents['background_agent_v2'] = Agent(**background_agent_v2.decision_agent_methods)

    players_compete_itself = dict()
    players_compete_itself['player_raise'] = Agent(**example_agent_raise_bet.decision_agent_methods)
    players_compete_itself['player_call'] = Agent(**example_agent_call.decision_agent_methods)
    players_compete_itself['player_random'] = Agent(**example_agent_random.decision_agent_methods)
    players_compete_itself['agent_call_AT'] = Agent(**agent_call_AJ.decision_agent_methods)
    players_compete_itself['agent_raise_AT'] = Agent(**agent_raise_AJ.decision_agent_methods)
    players_compete_itself['agent_raise_aggressive'] = Agent(**agent_raise_aggressive_AJ.decision_agent_methods)
    players_compete_itself['agent_call_top_pair'] = Agent(**agent_call_toppair_AJ.decision_agent_methods)
    players_compete_itself['agent_call_flop'] = Agent(**agent_call_AJ_flop.decision_agent_methods)
    players_compete_itself['background_agent_v1'] = Agent(**background_agent_v1.decision_agent_methods)
    players_compete_itself['background_agent_v2'] = Agent(**background_agent_v2.decision_agent_methods)

    """
    Current Novelty List
    1. exchange_hands_novelty
    2. reorder_hand_ranking
    3. reorder_numbers_ranking
    4. royal_texas_version
    5. finish_flop_round/undo_finish_flop_round
    """
    run_tournament_with_novelty(max_hand=max_hand,
                                num_game_in_tournament=num_game_in_tournament,
                                inject_at=inject_at,
                                player_decision_agents=player_decision_agents,
                                novelty='exchange_hands_novelty')

    # build_matrix(max_hand=max_hand,
    #              num_game_in_tournament=num_game_in_tournament,
    #              inject_at=inject_at,
    #              player_list=player_decision_agents,
    #              compete_list=players_compete_itself,
    #              novelty=finish_flop_round,
    #              undo_novelty=undo_finish_flop_round)

    # plot_box_graph()

