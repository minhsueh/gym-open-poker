from card_utility_actions import *
from action_choices import *
import numpy as np


class Board:
    def __init__(self, dealer_name, total_cash, pot, side_pot, deck, deck_idx, num_active_player_on_table):
        self.dealer = dealer_name
        self.total_cash_on_table = total_cash
        self.pot = pot
        self.side_pot = side_pot  # only use for all-in situation
        self.deck = deck
        self.deck_idx = deck_idx  # record which card has been used in the deck. e.x deck[deck_idx: deck_idx+2] as hole card
        self.community_cards = list()
        self.players_made_decisions = list()  # players who have made decision on the table
        self.current_highest_bet = 0  # previous bet in the current round
        self.buy_in_amount = 40  # 20 times to 100 times of force bet of big blind
        self.num_active_player_on_table = num_active_player_on_table  # number of player could act in a hand

    def assign_dealer(self, player_name):
        """
        assigns which player is the dealer in the next round after river.
        :param player_name: next player who should be dealer after river turn
        :return:
        """
        self.dealer = player_name

    def assign_deck_idx(self, num):
        """
        increase deck index to choose proper cards from deck
        :param num: number of cards you want to use
        :return:
        """
        if self.deck_idx + num > len(self.deck):
            print('Error: cannot deal more cards')
            raise Exception

        self.deck_idx += num

    def compare_for_highest_bet(self, new_bet):
        """
        keep a record of current highest bet on the table each round
        :param new_bet:
        :return:
        """
        self.current_highest_bet = max(self.current_highest_bet, new_bet)

    def reset_board_each_game(self, current_gameboard):
        """
        run this function after each river round to re-shuffle the deck for next game
        :return:
        """
        if current_gameboard['cur_phase'] != 'concluding_phase':
            print('Board: we are in the wrong phase to reset board each game')
            raise Exception

        self.deck_idx = 0
        self.total_cash_on_table = 0
        self.current_highest_bet = 0
        self.pot = dict()
        self.side_pot = dict()
        self.community_cards = list()
        self.num_active_player_on_table = len(current_gameboard['players'])
        np.random.shuffle(self.deck)

    def reset_board_each_round(self, current_gameboard):
        self.players_made_decisions = list()
        self.current_highest_bet = 0

    def add_total_cash_on_table(self, amount):
        """
        once a player bets, we should add that amount in the middle table
        :param amount:
        :return:
        """
        if amount < 0:
            print('Error: try to add 0 or negative value into the board')
            raise Exception

        self.total_cash_on_table += amount

    def add_chips_to_pot(self, chips):
        """
        once a player bets, we should put these chips into the pot
        :param chips:
        :return:
        """
        if not chips:
            print('Error: cannot add empty chips to the pot')
            raise Exception

        print('Board: adding chips into the pot')
        for amount, chips_list in chips.items():
            if amount not in self.pot:
                self.pot[amount] = set()
            for c in copy.copy(chips_list):
                self.pot[amount].add(c)

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

    def deal_community_card_by_number(self, num):
        """
        deal community cards by a specific number
        :param num: number of cards to deal
        :return:
        """
        # burn 1 card before deal community cards
        self.burn_card()

        if self.deck_idx + num > len(self.deck):
            print('Error: cannot deal more communities cards')
            raise Exception

        community_cards = self.deck[self.deck_idx: self.deck_idx+num]
        self.assign_deck_idx(num)
        self.community_cards.extend(community_cards)
        print(f'Current community cards on the table:')
        for c in self.community_cards:
            print(f'---> {c}')

    def burn_card(self, num=1):
        """
        the function is used to burn card at the beginning of flop/turn/river round
        :param num: number of cards to burn, default is 1
        :return:
        """
        if self.deck_idx + num > len(self.deck):
            print('Error: cannot burn more cards')
            raise Exception

        self.assign_deck_idx(num)
        print(f'Board: burn {num} cards before dealing community cards')


    def charge_buy_in(self, player, current_gameboard):
        """
        if player want to join the table, they have to pay the buy in amount
        :param player: player needed to be charged
        :param current_gameboard:
        :return:
        """
        player.current_cash -= self.buy_in_amount
        chips, remaining = chips_combination_given_amount(player, self.buy_in_amount, current_gameboard)
        if remaining > 0:
            raise Exception


    def calculate_all_in_result(self, winners, has_equal_hand=False):
        """
        If someone all-in during the game, use this function to compute side pot which show how much
        each player could get if they win their hands
        :param winners:
        :param has_equal_hand:
        :return:
        """
        if not winners:
            print('Error: cannot find all-in result since no winner provided')
            raise Exception
        if not self.side_pot or not self.pot:
            print('Error: nothing in the side pot/main pot, something went wrong')
            raise Exception

        print(f'Board: computing side pot since there are players all-in in this game')
        res = dict()
        for name in self.side_pot.keys():
            res[name] = 0

        if not has_equal_hand:  # only one winner
            print(f'Board: {winners} is the only one winner for computing all-in')
            winner_money_in_pot = self.side_pot[winners]
            for name, amount in self.side_pot.items():
                res[winners] += min(winner_money_in_pot, amount)
                self.side_pot[name] -= amount
        else:  # more than one winner
            print(f'Board: there are more than one winners for computing all-in')

        return res
