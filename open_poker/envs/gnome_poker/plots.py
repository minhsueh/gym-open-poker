"""
The file is used for reading result from json file and direction output plots or logs result
"""

import gameplay
from collections import defaultdict, Counter
import numpy as np
from agent import Agent
from novelty_distributions import *
import csv
import json
from scipy import stats
import pandas as pd
from scipy.stats import sem

# import agents
from agents import example_agent_check_fold, example_agent_random, example_agent_call, example_agent_raise_bet
from agents import agent_call_AJ, agent_raise_AJ, agent_call_toppair_AJ, agent_raise_aggressive_AJ
from agents import agent_call_AJ_flop, background_agent_v1, background_agent_v2

# import plot package
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme(style="whitegrid")


def box_plot(pre, post):
    agents_collect = defaultdict(list)
    pre_res = defaultdict(list)
    for k, v in pre.items():
        for row in v:
            name, array = row
            agents_collect['Players'].extend([name] * len(array))
            agents_collect['Cash Ratio'].extend(array)
            agents_collect['Novelty Type'].extend(['Pre-Novelty'] * len(array))

    for k, v in post.items():
        for row in v:
            name, array = row
            agents_collect['Players'].extend([name] * len(array))
            agents_collect['Cash Ratio'].extend(array)
            agents_collect['Novelty Type'].extend(['Post-Novelty'] * len(array))

    # for k, v in post.items():
    #     for row in v:
    #         name, array = row
    #         cur_mean = np.mean([val for i, val in enumerate(array) if i != name])
    #         agents_collect['Players'].append(name)
    #         agents_collect['Cash Ratio'].append(cur_mean)
    #         agents_collect['Novelty Type'].append('Post-Novelty')
    #
    # for k, v in pre.items():
    #     for row in v:
    #         name, array = row
    #         cur_mean = np.mean([val for i, val in enumerate(array) if i != name])
    #         pre_res['Players'].append(name)
    #         pre_res['Mean'].append(cur_mean)
    #         pre_res['legend'].append('Pre-Novelty Mean')
    #     break

    df = pd.DataFrame(agents_collect)
    ax = sns.boxplot(x="Players", y="Cash Ratio", hue="Novelty Type", data=df, palette="Set3")
    # ax = sns.lineplot(x="Players", y="Mean", hue="legend", data=pre_res, ax=ax)
    plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)
    labels = ['agent_call_AT',
              'agent_call_flop',
              'agent_call_top_pair',
              'agent_raise_AT',
              'agent_raise_aggressive',
              'background_agent_v1',
              'background_agent_v2',
              'player_call',
              'player_raise',
              'player_random']
    ax.axes.set_xticklabels(labels, rotation=90)
    plt.ylabel('Robustness Number')
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'/Users/hongyuli/Desktop/box_plot.png', dpi=500)


def compute_global_p(pre, post):
    pre_array = []
    post_dict = defaultdict(list)
    for line in pre['exchange_hands_novelty']:
        idx, array = line
        for i in range(idx):
            pre_array.append(array[i])
    for k, v in post.items():
        cur = []
        for line in v:
            idx, array = line
            for i in range(idx):
                cur.append(array[i])
        post_dict[k] = cur

    res = defaultdict(list)
    for k, v in post_dict.items():
        cur = stats.ttest_ind(v, pre_array)
        res[k] = [cur[0], cur[1]]
    print(res)


def global_impact(pre, post):
    novelty2res = defaultdict(list)
    res = defaultdict(list)
    novelty2idx = {k: i for i, k in enumerate(pre.keys())}
    labels = ['Exchange Hand', 'Reorder Hand Ranking', 'Reorder Number Ranking', 'Royal Texas',
              'All-in/Flop at Flop Round', 'Hole Card Invisible', 'Remove One Hand Rank', 'Add Color Flush',
              'Draw card with Replacement']

    for k in pre.keys():
        novelty_pre_res = pre[k]
        novelty_post_res = post[k]
        for i in range(len(novelty_pre_res)):
            pre_name, pre_array = novelty_pre_res[i]
            post_name, post_array = novelty_post_res[i]
            for j in range(i):
                novelty2res[k].append(abs(pre_array[j] - post_array[j]))
                res['Novelty'].append(labels[novelty2idx[k]])
                res['Value'].append(abs(pre_array[j] - post_array[j]))
                res['legend'].append('Mean')


    ax = sns.lineplot(x="Novelty", y="Value", hue="legend", data=res, err_style="bars")
    # ax = sns.lineplot(x="Novelty", y="Value", hue="legend", data=std_res, ax=ax, palette=['orange'])
    plt.legend(bbox_to_anchor=(1, 1), loc='upper right', ncol=1)

    ax.axes.set_xticklabels(labels, rotation=90)
    plt.ylabel('Global Impact')
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'/Users/hongyuli/Desktop/novelty_impact.png', dpi=500)


if __name__ == '__main__':
    path = '/Users/hongyuli/Desktop/poker_paper_data/data/heads_up.json'

    data = []
    with open(path, 'r') as f:
        for line in f:
            data.append(json.loads(line))

    novelties = {
        'nov': [exchange_hands_novelty, reorder_hand_ranking, reorder_numbers_ranking,
                royal_texas_version, finish_flop_round, cards_invisible_to_players, remove_rank_category,
                add_rank_category, draw_card_with_replacement],
        'undo': [None, None, None, None, undo_finish_flop_round, None, None, None, None],
        'novelty_names': ['exchange_hands_novelty', 'reorder_hand_ranking', 'reorder_numbers_ranking',
                          'royal_texas_version', 'finish_flop_round', 'hole_card_invisible',
                          'remove_one_hand_rank', 'adding_color_flush', 'draw_card_with_replacement']
    }

    pre_data = defaultdict(list)
    post_data = defaultdict(list)
    for line in data:
        novelty_name = line['novelty_name']
        if line['novelty_type'] == 'Pre-Novelty':
            pre_data[line['novelty_name']].append((line['name_idx'], line['cash_ratio']))
        if line['novelty_type'] == 'Post-Novelty':
            post_data[line['novelty_name']].append((line['name_idx'], line['cash_ratio']))

    # box_plot(pre_data, post_data)
    # global_impact(pre_data, post_data)
    compute_global_p(pre_data, post_data)





