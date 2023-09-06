import numpy as np
import copy
from action_choices import *
from card_utility_actions import number_cards_to_draw, check_hands
from card import Card
from chip import Chip


def exchange_hands_left_and_find_winner(current_gameboard):
    """
    the function is used to find winner of current game after river round if there are more than
    one players in the game
    :param current_gameboard:
    :return:
    """
    print('Board: comparing hands of those player below...')

    print(f'Board: before exchanging hands')
    before_exchange = copy.deepcopy(current_gameboard['hands_of_players'][-1])
    for k, v in before_exchange.items():
        print(f'{k} hand ---> {", ".join(map(str, v[1]))}')

    print('Board: after exchanging hands')
    original_values = [v for v in before_exchange.values()]
    values = original_values[1:] + [original_values[0]]
    res = {name: val for val, name in zip(values, before_exchange.keys())}
    for k, v in res.items():
        print(f'{k} hand ---> {", ".join(map(str, v[1]))}')

    candidate_list = list()
    max_num = float('-inf')
    for player_name, value in res.items():
        if value[0] < max_num:
            continue
        if value[0] > max_num:
            candidate_list = list()
            max_num = value[0]
        candidate_list.append(player_name)

    if len(candidate_list) == 1:
        return [candidate_list[0]]

    # now have to compare highest value in hand
    candidates_hand = [res[candidate][1] for candidate in candidate_list]
    win_bool_list = [1] * len(candidate_list)
    winners = list()  # in case if there are equal hands

    for values in zip(*candidates_hand):
        max_num = max([values[i] for i in range(len(values)) if win_bool_list[i]])
        for i in range(len(values)):
            if not win_bool_list[i]:
                continue
            if values[i] < max_num:
                win_bool_list[i] = 0
    for i in range(len(win_bool_list)):
        if win_bool_list[i]:
            winners.append(candidate_list[i])

    return winners


def exchange_hands_and_find_winner(current_gameboard):
    """
    the function is used to find winner of current game after river round if there are more than
    one players in the game
    :param current_gameboard:
    :return:
    """
    print('Board: comparing hands of those player below...')

    print(f'Board: before exchanging hands')
    before_exchange = copy.deepcopy(current_gameboard['hands_of_players'][-1])
    for k, v in before_exchange.items():
        print(f'{k} hand ---> {", ".join(map(str, v[1]))}')

    print('Board: after exchanging hands')
    values = [v for v in before_exchange.values()]
    exchange_list = [i for i in range(len(before_exchange))]
    flag = True
    while flag:
        np.random.shuffle(exchange_list)
        flag = False if all([True if i != num else False for i, num in enumerate(exchange_list)]) else True
    res = {name: values[idx] for idx, name in zip(exchange_list, before_exchange.keys())}
    for k, v in res.items():
        print(f'{k} hand ---> {", ".join(map(str, v[1]))}')

    candidate_list = list()
    max_num = float('-inf')
    for player_name, value in res.items():
        if value[0] < max_num:
            continue
        if value[0] > max_num:
            candidate_list = list()
            max_num = value[0]
        candidate_list.append(player_name)

    if len(candidate_list) == 1:
        return [candidate_list[0]]

    # now have to compare highest value in hand
    candidates_hand = [res[candidate][1] for candidate in candidate_list]
    win_bool_list = [1] * len(candidate_list)
    winners = list()  # in case if there are equal hands

    for values in zip(*candidates_hand):
        max_num = max([values[i] for i in range(len(values)) if win_bool_list[i]])
        for i in range(len(values)):
            if not win_bool_list[i]:
                continue
            if values[i] < max_num:
                win_bool_list[i] = 0
    for i in range(len(win_bool_list)):
        if win_bool_list[i]:
            winners.append(candidate_list[i])

    return winners


def alternate_compute_allowable_pre_flop_actions(self, current_gameboard):
    """
    this is alternate function to compute player's allowable actions in pre-flop round
    Only two are allowable: 1. call, 2. fold
    :param current_gameboard:
    :return:
    """
    print(f'{self.player_name} computes allowable pre-flop round actions, only flop/call...')
    allowable_actions = set()
    allowable_actions.add(fold)

    # except fold, only allowable action is call
    allowable_actions.add(call)

    return allowable_actions


def alternate_compute_allowable_flop_actions(self, current_gameboard):
    """
    this is alternate function to compute player's allowable actions in flop round
    Only two are allowable: 1. all-in, 2. fold
    :param current_gameboard:
    :return:
    """
    print(f'{self.player_name} computes allowable flop round actions, only fold/all-in')
    allowable_actions = set()
    allowable_actions.add(fold)

    # except fold, only allowable action is all-in
    if self.current_cash > 0:
        allowable_actions.add(all_in)

    return allowable_actions


def compute_allowable_pre_flop_actions(self, current_gameboard):
    """
    Players in this phase could call, raise, or fold (no all-in in this turn?)
    The phase could finish only if all player who would like to continue put the same amount of money
    :param current_gameboard:
    :return: allowable actions
    :rtype: set
    """
    print(f'{self.player_name} computes allowable pre-flop round actions...')
    allowable_actions = set()

    # big blind are able to check if no other raise bet in pre-flop
    big_blind_force_bet = current_gameboard['small_blind_amount'] * current_gameboard['big_blind_pay_from_baseline']
    if self.big_blind and big_blind_force_bet == current_gameboard['board'].current_highest_bet:
        allowable_actions.add(check)

    allowable_actions.add(fold)  # can fold in any case

    allowable_actions.add(call)
    allowable_actions.add(raise_bet)

    return allowable_actions


def compute_allowable_flop_actions(self, current_gameboard):
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
    print(f'{self.player_name} computes allowable flop round actions...')
    allowable_actions = set()
    allowable_actions.add(fold)

    # can bet only if there are not others bet before
    # can check only if there are not others bet before
    if not current_gameboard['board'].current_highest_bet:
        allowable_actions.add(check)
        allowable_actions.add(bet)

    # can all-in if have cash
    if self.current_cash > 0:
        allowable_actions.add(all_in)

    # can raise bet if there are other bet previously
    # can call if there are other bet previously
    if current_gameboard['board'].current_highest_bet:
        allowable_actions.add(raise_bet)
        allowable_actions.add(call)

    return allowable_actions


def alternate_deal_hole_cards(self, player, phase, current_gameboard):
    """
    call this function to deal two cards to each player at the beginning of pre-flop round
    :param player:
    :param phase:
    :return:
    """
    num_cards = number_cards_to_draw(phase)
    if self.deck_idx + num_cards > len(self.deck):
        print('Error: cannot deal more hold cards, since no more card in the deck')
        raise Exception
    if phase != 'pre_flop_phase':
        print('Error: cannot deal hole cards in the current phase')
        raise Exception

    hole_cards = self.deck[self.deck_idx: self.deck_idx+num_cards]
    self.assign_deck_idx(num_cards)
    current_gameboard['invisible_card']['players'][player.player_name] = hole_cards

    if 'invisible_card' in current_gameboard and 'hole_card' in current_gameboard['invisible_card']:
        type2num = current_gameboard['invisible_card']
    else:
        raise Exception

    if type2num['hole_card'] > num_cards:
        raise Exception

    actual_hole_card = []
    for _ in range(type2num['hole_card']):
        dummy_card = Card(suit='*', number=float('-inf'), is_num_card=False, is_face_card=False, is_ace_card=False, active=1)
        actual_hole_card.append(dummy_card)

    for i in range(num_cards - type2num['hole_card']):
        actual_hole_card.append(hole_cards[i])

    print('Current card is invisible to player')
    player.assign_hole_cards(actual_hole_card)
    print(f'{player.player_name} gets hole cards:')
    for c in hole_cards:
        print(f'---> {c}')
    print(f'But {player.player_name} could only see:')
    for c in actual_hole_card:
        print(f'---> {c}')


def alternate_deal_community_card(self, phase, current_gameboard):
    """
    deal community cards according to the corresponding phase
    :param phase: pre-flop (private 2), flop(table 3), turn(table 1), river(table 1)
    :return:
    """
    # burn 1 card before dealing community cards
    self.burn_card()

    num_cards = number_cards_to_draw(phase)
    if self.deck_idx + num_cards > len(self.deck):
        print('Error: cannot deal more communities cards')
        raise Exception

    community_cards = self.deck[self.deck_idx: self.deck_idx+num_cards]
    self.assign_deck_idx(num_cards)

    if 'invisible_card' in current_gameboard and 'community_card' in current_gameboard['invisible_card']:
        type2num = current_gameboard['invisible_card']
    else:
        raise Exception

    if type2num['community_card'] - len(self.community_cards) <= 0:
        self.community_cards.extend(community_cards)
    else:
        cur_num_cards = num_cards
        cur_community_card = type2num['community_card']
        print('testing', cur_num_cards, cur_community_card)
        for i in range(min(cur_num_cards, cur_community_card)):
            self.community_cards.append(Card(suit='*', number=float('-inf'), is_num_card=False, is_face_card=False, is_ace_card=False, active=1))
            num_cards -= 1

        idx = 0
        while num_cards > 0:
            self.community_cards.append(community_cards[idx])
            idx += 1
            num_cards -= 1

    print(f'Current community cards on the table with invisible:')
    for c in self.community_cards:
        print(f'---> {c}')


def alternate_calculate_best_hand_invisible(current_gameboard, player):
    """
    computing the best hand of this player
    :param current_gameboard:
    :param player:
    :return:
    """
    print('testing calculate')
    if current_gameboard['cur_phase'] != 'concluding_phase':
        raise Exception

    print(f'{player.player_name} is now calculating its best hand with community cards')
    board = current_gameboard['board']

    if current_gameboard['invisible_card']['community']:
        community_cards = copy.copy(current_gameboard['invisible_card']['community'])
    else:
        community_cards = copy.copy(board.community_cards)
    if current_gameboard['invisible_card']['players'][player.player_name]:
        hole_cards = copy.copy(current_gameboard['invisible_card']['players'][player.player_name])
    else:
        hole_cards = copy.copy(player.hole_cards)

    total_hand = community_cards + hole_cards
    if len(total_hand) != 7:
        raise Exception

    suits = [card.get_suit() for card in total_hand]
    values = [card.get_number() for card in total_hand]
    for c in total_hand:
        print(c)

    rank_type, hand = check_hands(current_gameboard, total_hand, suits, values, player)

    # recording best hand with corresponding player name
    current_gameboard['hands_of_players'][-1][player.player_name] = (rank_type, hand)

    return flag_config_dict['successful_action']


def deal_hole_cards(self, player, phase, current_gameboard):
    """
    call this function to deal two cards to each player at the beginning of pre-flop round
    :param player:
    :param phase:
    :return:
    """
    num_cards = number_cards_to_draw(phase)
    if self.deck_idx + num_cards > len(self.deck):
        print('Error: cannot deal more hold cards, since no more card in the deck')
        raise Exception
    if phase != 'pre_flop_phase':
        print('Error: cannot deal hole cards in the current phase')
        raise Exception

    hole_cards = self.deck[self.deck_idx: self.deck_idx+num_cards]
    self.assign_deck_idx(num_cards)
    player.assign_hole_cards(hole_cards)
    print(f'{player.player_name} gets hole cards:')
    for c in hole_cards:
        print(f'---> {c}')


def deal_community_card(self, phase, current_gameboard):
    """
    deal community cards according to the corresponding phase
    :param phase: pre-flop (private 2), flop(table 3), turn(table 1), river(table 1)
    :return:
    """
    # burn 1 card before dealing community cards
    self.burn_card()

    num_cards = number_cards_to_draw(phase)
    if self.deck_idx + num_cards > len(self.deck):
        print('Error: cannot deal more communities cards')
        raise Exception

    community_cards = self.deck[self.deck_idx: self.deck_idx+num_cards]
    self.assign_deck_idx(num_cards)
    self.community_cards.extend(community_cards)
    print(f'Current community cards on the table:')
    for c in self.community_cards:
        print(f'---> {c}')


def is_color_flush(total_hand, suits, values):
    """
    color flush is a hand rank that if there are more than 6 cards with same color return true
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    colors = [card.color for card in total_hand]
    for c in set(colors):
        if colors.count(c) >= 6:
            print('find more than 6 cards with same color')
            return True
    return False


def get_color_flush(total_hand, suits, values):
    """
    get highest card for color flush hand rank
    :param total_hand:
    :param suits:
    :param values:
    :return:
    """
    colors = [card.color for card in total_hand]
    target = None
    for c in set(colors):
        if colors.count(c) >= 6:
            target = c
            break
    array = [card.get_number() for card in total_hand if card.color == target]
    return sorted(array, key=lambda x: -x)[:5]


def alternate_deal_hole_card_replacement(self, player, phase, current_gameboard):
    """

    :param self:
    :param player:
    :param phase:
    :param current_gameboard:
    :return:
    """
    print('draw hole card with replacement')
    if phase != 'pre_flop_phase':
        print('Error: cannot deal hole cards in the current phase')
        raise Exception

    num_cards = number_cards_to_draw(phase)
    all_idx = [i for i in range(len(self.deck))]
    candidate_nums = []
    for i in range(num_cards):
        candidate_nums.append(np.random.choice(all_idx))

    hole_cards = [self.deck[num] for num in candidate_nums]
    player.assign_hole_cards(hole_cards)
    print(f'{player.player_name} gets hole cards:')
    for c in hole_cards:
        print(f'---> {c}')


def alternate_community_hole_card_replacement(self, phase, current_gameboard):
    """

    :param self:
    :param phase:
    :param current_gameboard:
    :return:
    """

    print('draw community card with replacement')
    num_cards = number_cards_to_draw(phase)
    all_idx = [i for i in range(len(self.deck))]
    candidate_nums = []
    for i in range(num_cards):
        candidate_nums.append(np.random.choice(all_idx))

    community_cards = [self.deck[num] for num in candidate_nums]
    self.community_cards.extend(community_cards)
    print(f'Current community cards on the table:')
    for c in self.community_cards:
        print(f'---> {c}')


def pay_insurance(current_gameboard, player, num):
    """
    According to the player's hole card, there is an insurance the player could pay to avoid a loss in the future.

    :param current_gameboard:
    :param player:
    :param num:
    :return:
    """
    print('How much insurance you want to pay?')
    current_gameboard['insurance_pot'][player.player_name] = num

    print(f'{player.player_name} pay {num} insurance')
    player.current_cash -= num
    chips, remaining = chips_combination_given_amount(player, num, current_gameboard)
    if remaining > 0:
        raise Exception


def alternate_assign_pot(current_gameboard, winner):
    """
    insurance should be considered in this function
    :param current_gameboard:
    :param winner:
    :return:
    """
    print('Testing')
    if not winner:
        raise Exception

    # bank give back proper amount to player who purchase insurances before
    insurance_pot = current_gameboard['insurance_pot']
    for k, v in insurance_pot.items():
        insurance_pot[k] = current_gameboard['insurance_rate'] * v

    for player in current_gameboard['players']:
        # only player who are not winner and also purchased insurance in the current game could be pay back
        # and player must bet something
        if player.player_name != winner and player.player_name in insurance_pot and player.bet_amount_each_game > 0:
            # total bet smaller than max amount insurance could cover, give all back
            if player.bet_amount_each_game < insurance_pot[player.player_name]:
                player.current_cash += player.bet_amount_each_game
                new_chips_list = {Chip(amount=1, color=current_gameboard['num2color'][1],
                                       weight=current_gameboard['num2weight'][1])
                                  for _ in range(int(player.bet_amount_each_game))}
                player.chips[1] |= new_chips_list

            # total bet larger than max amount insurance could cover, give back covered amount
            elif player.bet_amount_each_game > insurance_pot[player.player_name]:
                player.current_cash += insurance_pot[player.player_name]
                new_chips_list = {Chip(amount=1, color=current_gameboard['num2color'][1],
                                       weight=current_gameboard['num2weight'][1])
                                  for _ in range(int(insurance_pot[player.player_name]))}
                player.chips[1] |= new_chips_list

            # total bet equal to max amount insurance could cover, nothing need to be done
            else:
                pass

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

    # reset insurance pot after each game since some players may not want to buy insurance in next according to
    # their current hand
    current_gameboard['insurance_pot'] = {}


