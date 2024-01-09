
class Card:

    def __init__(self, suit, number=None, is_num_card=False, is_face_card=False, is_ace_card=False, active=1,
                 color=None):
        """
        Note: only one of the is_***_card will be true.
        :param suit:
        :param number:
        :param is_num_card:
        :param is_face_card:
        :param is_ace_card:
        :param active:
        :param color:
        """
        assert suit in ['club', 'diamond', 'heart', 'spade']
        self.suit = suit                # clubs, diamonds, hearts, spades
        self.number = number            # 1,2,3,4,5,6,7,8,9,10,11,12,13


    def __str__(self):
        """
        For directly print card info
        :return: card info
        """
        if self.number == 1:
            return f'card info: A; {self.suit}'
        elif self.number == 11:
            return f'card info: J; {self.suit}'
        elif self.number == 12:
            return f'card info: Q; {self.suit}'
        elif self.number == 13:
            return f'card info: K; {self.suit}'
        else:
            return f'card info: {self.number}; {self.suit}'

    def get_suit(self):
        return self.suit

    def get_number(self):
        return self.number

