from cards import Card


class Player:
    """UNO Player class"""

    def __init__(self, name: str, hand: list[Card] = None):
        """
        UNO Player class constructor
        :param name: player's name
        :param hand: the player's cards
        """
        self.name: str = name
        self.hand: list[Card] = [] if hand is None else hand
        self.canJumpIn: bool = False

    def __str__(self):
        return self.name

    def __int__(self):
        return len(self.hand)

    def draw(self, cards: list[Card]) -> None:
        """
        draw cards
        :param cards: the cards to be drawn
        """
        self.hand += cards

    def play(self, cards: Card | list[Card]) -> None:
        """
        Plays cards from the player's and
        :param cards: the cards being played
        """
        if isinstance(cards, list):
            for card in cards:
                assert (card in self.hand)
                self.hand.remove(card)
        else:
            assert (cards in self.hand)
            self.hand.remove(cards)


class Hand:
    """UNO Player Hand class"""

    def __init__(self, cards, rules):
        pass