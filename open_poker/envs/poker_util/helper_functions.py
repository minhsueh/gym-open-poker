from collections import deque


def is_first_player_in_this_round(player, current_gameboard):
    """
    if the player is first player to player the game, return True. Otherwise, return False
    :param player: current player
    :param current_gameboard:
    :return: True if is first player, else False
    """
    flag = True
    if current_gameboard['cur_phase'] == 'pre_flop_phase' and len(current_gameboard['players']) > 2:
        if current_gameboard['players'][2].player_name == player.player_name:
            return flag
    else:
        if current_gameboard['players'][0].player_name == player.player_name:
            return flag
    flag = False

    return flag


def find_winner(current_gameboard):
    """
    the function is used to find winner of current game after river round only if there are more than
    one players in the game. If there is only one player left in the game board, there is another function
    used for finding winner
    :param current_gameboard:
    :return: winner
    """
    print('Board: comparing hands of those player below...')
    res = current_gameboard['hands_of_players'][-1]
    for k, v in res.items():
        print(f'{k} hand ---> {", ".join(map(str, v[1]))}')

    # firstly, check rank type of all players
    candidate_list = list()
    max_num = float('-inf')
    for player_name, value in res.items():
        if value[0] < max_num:
            continue
        if value[0] > max_num:
            candidate_list = list()
            max_num = value[0]
        candidate_list.append(player_name)

    # if only one player with the highest rank type, find the winner
    if len(candidate_list) == 1:
        return [candidate_list[0]]

    # otherwise, we need to compare highest numbers of those equal hand of players
    candidates_hand = [res[candidate][1] for candidate in candidate_list]
    win_bool_list = [1] * len(candidate_list)
    winners = list()  # in case if there are equal hands

    # compare numbers from largest to smallest value
    number_order = current_gameboard['numbers_rank_type']
    for values in zip(*candidates_hand):
        if isinstance(values[0], float):
            continue
        max_num = max([number_order[values[i]] for i in range(len(values)) if win_bool_list[i]])
        for i in range(len(values)):
            if not win_bool_list[i]:
                continue
            if number_order[values[i]] < max_num:
                win_bool_list[i] = 0
    for i in range(len(win_bool_list)):
        if win_bool_list[i]:
            winners.append(candidate_list[i])

    return winners


def chips_combination_given_amount_for_pot(pot, amount, current_gameboard):
    """
    remove certain amount of chips from pot, which would be added to player's hand at the end
    :param pot: board's pot
    :param amount: amount want to remove from pot
    :param current_gameboard:
    :return: chips dict
    """
    keys = sorted(pot.keys(), key=lambda x: -x)
    res = dict()

    for key in keys:
        if not pot[key]:
            continue
        while amount and key <= amount and pot[key]:
            cur_chip = pot[key].pop()
            amount -= key
            if key not in res:
                res[key] = {cur_chip}
            else:
                res[key].add(cur_chip)

    return res


def assign_pot_to_only_winner(current_gameboard, winner):
    """
    if there is only one winner, board should assign pot to it with proper cash and chips
    :param current_gameboard:
    :param winner:
    :return:
    """
    if not winner:
        raise Exception

    board = current_gameboard['board']
    print(f'Board: moving total amount ${board.total_cash_on_table} on the table to {winner}')
    if board.side_pot:  # there is at least one player all-in in the game
        for p in current_gameboard['players']:
            board.side_pot[p.player_name] = p.bet_amount_each_game

    for player in current_gameboard['players']:
        if player.player_name == winner:
            if board.side_pot:  # all-in condition
                winner_get_dict = board.calculate_all_in_result(winner, has_equal_hand=False)

                # add current cash for player
                winner_get = winner_get_dict[winner]
                player.current_cash += winner_get

                # move chips into player's hand
                chips = chips_combination_given_amount_for_pot(board.pot, winner_get, current_gameboard)
                for amount, chips_list in chips.items():
                    player.chips[amount] |= chips_list

                # if there are side pot remaining, we should return those chips to original player
                for name, money in board.side_pot.items():
                    if money > 0:
                        print(f'Board: we should give ${money} chips to {name} as side pot remaining')
                        cur_player = current_gameboard['players_dict'][name]
                        cur_player += money
                        chips = chips_combination_given_amount_for_pot(board.pot, money, current_gameboard)
                        for amount, chips_list in chips.items():
                            cur_player.chips[amount] |= chips_list

            else:  # assign winner normally
                for amount, chips_list in board.pot.items():
                    player.current_cash += amount * len(chips_list)
                    player.chips[amount] |= chips_list


def split_pot_for_euqal_hand(current_gameboard, winners):
    """
    if there are more than one winner, we should split pot for them
    :param current_gameboard:
    :param winners:
    :return:
    """
    if len(winners) < 2:
        raise Exception

    board = current_gameboard['board']
    total_per_winner = board.total_cash_on_table / len(winners)
    print(f'Board: amount each winner could get is {total_per_winner}')

    for amount, chips_list in board.pot.items():
        chips_list = set(chips_list)
        length = len(chips_list) // len(winners)
        for name in winners:
            cur_player = current_gameboard['players_dict'][name]
            cur_player.current_cash += amount * length
            for _ in range(length):
                cur_player.chips[amount].add(chips_list.pop())

            # for player in current_gameboard['players']:
                # if player.player_name == name:
                #     player.current_cash += amount * length
                #     for _ in range(length):
                #         player.get_chips()[amount].add(chips_list.pop())


def remove_player_from_queue_if_lost(current_gamebaord):
    """
    if player status is lost, we remove it from game board
    :param current_gamebaord:
    :return:
    """
    updated_queue = deque()
    lost_players = list()
    for player in current_gamebaord['players']:
        if player.status == 'lost':
            lost_players.append(player.player_name)
            continue
        updated_queue.append(player)
    current_gamebaord['players'] = updated_queue
    if lost_players:
        print(f'Board: those player(s) are out of game {"; ".join(lost_players)}')
    print(f'Board: there are {len(updated_queue)} players remaining on the table')


def print_cash_info(current_gameboard):
    print('*********************************************************')
    print('                       Cash Info              ')
    for p in current_gameboard['players']:
        total = 0
        for amount, chips_list in p.chips.items():
            total += amount * len(chips_list)
        print(f'{p.player_name} cash info (current_cash/chips): {p.current_cash}/{total}')
    print('*********************************************************')


def print_chips_info(chips):
    total = 0
    print('*************************************')
    print('             Chips Info              ')
    for amount, chips_list in chips.items():
        total += amount * len(chips_list)
        print(f'chip amount: {amount}; number of chips: {len(chips_list)}')
    print(f'Total amount of those chips: {total}')
    print('*************************************')


def print_winner_count_in_one_game_instance(winner_of_hands):
    print('During this tournament, players\' hands of winning count below:')
    for key, value in winner_of_hands.items():
        print(f'{key} wins {value} times')


def end_game_and_begin_next(current_gameboard, show_community_cards=True):
    """
    if all players except one fold, we should conclude game right now
    :param current_gameboard:
    :return:
    """
    if show_community_cards:
        num = len(current_gameboard['board'].community_cards)
        current_gameboard['board'].deal_community_card_by_number(max(0, 5 - num))  # 5 is max number for community cards

    current_gameboard['cur_phase'] = 'concluding_phase'


def num_players_left(current_gameboard):
    """
    compute how many player is still in the game and available to play next game
    :param current_gameboard:
    :return: number of player left, last player who left if num of player is 1
    """
    num_player_left = 0
    candidate = None
    for player in current_gameboard['players']:
        if player.status == 'waiting_for_move':
            num_player_left += 1
            candidate = player
    return num_player_left, candidate


def player_with_most_cash(current_gameboard):
    """
    find which player has the most amount of money
    :param current_gameboard:
    :return:
    """
    winner = current_gameboard['players'][0]
    for p in current_gameboard['players']:
        if p.current_cash > winner.current_cash:
            winner = p

    return winner


def find_only_left_winner(current_gameboard):
    """
    if all players fold except one, we should return that player
    :param current_gameboard:
    :return:
    """
    winners = list()
    for p in current_gameboard['players']:
        if p.is_fold or p.status == 'lost':
            continue
        winners.append(p)

    if len(winners) > 1:
        print('Error: more than one player without fold')
        raise Exception

    return [w.player_name for w in winners]