from card_utility_actions import number_cards_to_draw

# from action_choices import *
import numpy as np
import collections
from action import Action


from phase import Phase
import logging

logger = logging.getLogger("gym_open_poker.envs.poker_util.logging_info.board")


class Board:
    def __init__(
        self,
        buy_in_amount,
        total_cash,
        pot,
        side_pot,
        deck,
        deck_idx,
        num_active_player_on_table,
    ):
        # self.dealer = dealer_name
        # self.total_cash_on_table = total_cash
        # self.pot = pot
        # self.side_pot = side_pot  # only use for all-in situation
        self.deck = deck
        self.deck_idx = deck_idx  # record which card has been used in the deck. e.x deck[deck_idx: deck_idx+2] as hole card
        self.community_cards = list()
        self.burn_cards = list()
        # self.players_made_decisions = list()  # players who have made decision on the table
        # self.current_highest_bet = 0  # previous bet in the current round
        # self.num_active_player_on_table = num_active_player_on_table  # number of player could act in a hand
        self.game_idx = 0
        self.dealer_position = -1

        self.cur_phase = Phase.PRE_FLOP

        # parameters to keep track on the total betting
        self.player_pot = collections.defaultdict(int)  # how much did each player spend in the current round
        self.players_last_move_list = [Action.NONE] * num_active_player_on_table  # keep track on last move of each player
        self.players_last_move_list_hist = [Action.NONE] * num_active_player_on_table  # keep track on last move of each player
        self.pots_amount_list = []
        # the total amount on the table, it will be update in function conclude round.
        # The size might differ if there are side pot.
        self.pots_attendee_list = []

        self.buy_in_amount = buy_in_amount

        self.current_betting_idx = 0
        self.current_bet_count = 0
        self.current_raise_count = 0
        self.small_blind_postiion_idx = 1
        self.big_blind_postiion_idx = 2

        self.previous_showdown = None
        self.history = dict()
        self.history["cash"] = dict()
        self.history["cash"][0] = [buy_in_amount] * num_active_player_on_table
        self.history["rank"] = dict()
        self.history["rank"][0] = [1] * num_active_player_on_table
        self.history["player_status"] = dict()
        self.history["player_status"][0] = ["active"] * num_active_player_on_table

    def assign_deck_idx(self, num):
        """
        increase deck index to choose proper cards from deck
        :param num: number of cards you want to use
        :return:
        """
        if self.deck_idx + num > len(self.deck):
            logger.debug("Error: cannot deal more cards")
            raise Exception

        self.deck_idx += num

    def reset_board_each_game(self, current_gameboard):
        """
        Args:
            current_gameboard

        Returns:
            None

        """
        # deck
        self.deck_idx = 0
        self.community_cards = list()
        np.random.shuffle(self.deck)

        # pots_attendee_list
        """
        attendee = set()
        for p in current_gameboard["players"]:
            if p.status != "lost":
                attendee.add(p.player_name)
        current_gameboard["board"].pots_attendee_list = [attendee]
        """
        current_gameboard["board"].pots_attendee_list = []

        # pots_amount_list
        # current_gameboard["board"].pots_amount_list = [0]
        current_gameboard["board"].pots_amount_list = []

        # reset players_last_move_list
        for move_idx in range(len(current_gameboard["players"])):
            if (
                current_gameboard["board"].players_last_move_list[move_idx] != Action.LOST
                and current_gameboard["players"][move_idx].status != "lost"
            ):
                current_gameboard["board"].players_last_move_list[move_idx] = Action.NONE

        # player_pot
        self.player_pot = collections.defaultdict(int)

        # update dealer_position:
        dealer_position = self.dealer_position
        total_number_of_players = current_gameboard["total_number_of_players"]

        while True:
            dealer_position = (dealer_position + 1) % total_number_of_players
            if current_gameboard["players"][dealer_position].status != "lost":
                self.dealer_position = dealer_position
                break

        # update big and small blind:
        counter = 0
        for idx in range(dealer_position + 1, dealer_position + total_number_of_players + 1):
            player = current_gameboard["players"][idx % total_number_of_players]
            if player.status != "lost":
                counter += 1
                if counter == 1:
                    current_gameboard["board"].small_blind_postiion_idx = idx % total_number_of_players
                elif counter == 2:
                    current_gameboard["board"].big_blind_postiion_idx = idx % total_number_of_players

    def deal_hole_cards(self, player, phase, current_gameboard):
        """
        call this function to deal two cards to each player at the beginning of pre-flop round
        :param player:
        :param phase:
        :return:
        """
        num_cards = number_cards_to_draw(phase)
        if self.deck_idx + num_cards > len(self.deck):
            logger.debug("Error: cannot deal more hold cards, since no more card in the deck")
            raise Exception
        if phase != Phase.PRE_FLOP:
            logger.debug("Error: cannot deal hole cards in the current phase = " + str(phase))
            raise Exception

        hole_cards = self.deck[self.deck_idx : self.deck_idx + num_cards]
        self.assign_deck_idx(num_cards)
        player.assign_hole_cards(hole_cards)
        logger.debug(f"{player.player_name} gets hole cards:")
        for c in hole_cards:
            logger.debug(f"---> {c}")

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
            logger.debug("Error: cannot deal more communities cards")
            raise Exception

        community_cards = self.deck[self.deck_idx : self.deck_idx + num_cards]
        self.assign_deck_idx(num_cards)
        self.community_cards.extend(community_cards)
        logger.debug("Current community cards on the table:")
        for c in self.community_cards:
            logger.debug(f"---> {c}")

    def deal_community_card_by_number(self, num):
        """
        deal community cards by a specific number
        :param num: number of cards to deal
        :return:
        """
        # burn 1 card before deal community cards
        self.burn_card()

        if self.deck_idx + num > len(self.deck):
            logger.debug("Error: cannot deal more communities cards")
            raise Exception

        community_cards = self.deck[self.deck_idx : self.deck_idx + num]
        self.assign_deck_idx(num)
        self.community_cards.extend(community_cards)
        logger.debug("Current community cards on the table:")
        for c in self.community_cards:
            logger.debug(f"---> {c}")

    def burn_card(self, num=1):
        """
        the function is used to burn card at the beginning of flop/turn/river round
        :param num: number of cards to burn, default is 1
        :return:
        """
        if self.deck_idx + num > len(self.deck):
            logger.debug("Error: cannot burn more cards")
            raise Exception

        for card in self.deck[self.deck_idx : self.deck_idx + num]:
            self.burn_cards.append(card)
            logger.debug(f"Burn a card with suit {card.suit} and number {card.number}")

        self.assign_deck_idx(num)
        logger.debug(f"Board: burn {num} cards before dealing community cards")

    def remain_deck_number(self):
        """calculate the remain card number in deck
        =

                Args:


                Returns:
                    int:

        """
        return 52 - self.deck_idx
