from cards import Card


class Player:
    """UNO Player class"""

    def __init__(self, name: str, hand: list[Card] = None):
        """
        UNO Player class constructor
        :param name: player's name
        :param hand: the player's cards
        """
        self.name = name
        self.hand = [] if hand is None else hand

    def __str__(self):
        return self.name

    def draw(self, cards: list[Card]) -> None:
        """
        draw cards
        :param cards: the cards to be drawn
        """
        self.hand += cards

    def play(self):