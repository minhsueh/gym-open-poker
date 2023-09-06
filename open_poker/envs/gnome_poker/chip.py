
class Chip:
    def __init__(self, amount, color, weight):
        """
        Chips are used to pay the current player's bet
        :param amount: value of chip
        :param color: color of chip
        :param weight: weight of chip
        """
        self.amount = amount
        self.color = color
        self.weight = weight

    def get_amount(self):
        return self.amount

    def __str__(self):
        return f'chip info: {self.amount};{self.color};{self.weight}'
