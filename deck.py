from cards import Card
import random


class Deck:
    """UNO Deck class"""

    def __init__(self, cards: list[Card] | str = 'default'):
        """UNO Deck class constructor
        :param cards: the cards currently in the deck. Use 'default' for a full deck, 'empty' for an empty deck
        """
        if cards == 'default':
            self.fill()
        elif cards == 'empty':
            self.cards = []
        else:
            self.cards = cards

    def fill(self) -> None:
        """Resets the UNO deck to a full deck:
        19 Blue cards - 0 to 9 (5 rule cards)
        19 Green cards - 0 to 9 (5 rule cards)
        19 Red cards - 0 to 9 (5 rule cards)
        19 Yellow cards - 0 to 9 (5 rule cards)
        8 Draw 2 cards - 2 each in blue, green, red and yellow
        8 Reverse cards - 2 each in blue, green, red and yellow
        8 Skip cards - 2 each in blue, green, red and yellow
        4 Wild cards
        4 Wild Draw 4 cards
        4 Wild rule cards
        """
        self.cards: list[Card] = [wild for wild in [Card('wild', 'wild', 0),
                                                    Card('wild', 'wild', range(1, 4)),
                                                    Card('wild', 'wild draw 4', 0)] for _ in range(3)]

        colors = ['red', 'yellow', 'green', 'blue']
        actionCards = ['reverse', 'skip', 'draw 2'] * 2

        for color in colors:
            for cardType in actionCards:
                self.cards.append(Card(color, cardType, 0))

            self.cards.append(Card(color, 0, 2))

            ruleIndices = random.sample(range(1, 10), 4)
            for i in range(1, 10):
                self.cards.append(Card(color, i, 0))
                self.cards.append(Card(color, i, int(i in ruleIndices)))

        random.shuffle(self.cards)

    def draw(self, n: int) -> list[Card]:
        """
        draw n cards from the top of the deck
        :param n: number of cards to draw
        :return: a list of the cards drawn
        """
        drawn = []

        for _ in range(n):
            drawn.append(self.cards.pop())
            if not self.cards:
                self.fill()

        return drawn

    def append(self, cards: Card | list[Card]) -> None:
        """
        Appends cards to the deck
        :param cards: the card(s) to append.
        """
        if isinstance(cards, list):
            self.cards += cards
        else:
            self.cards.append(cards)

    def get_top(self) -> Card | None:
        """
        Gets the top card.
        :return: returns the top card on the deck
        """
        return self.cards[-1] if self.cards else None

    def top_sum(self) -> int | None:
        """
        Gets the sum of the top two cards if they are both number cards
        :return: the sum of the top two cards if they are both number cards, None otherwise.
        """
        type1 = self.cards[-1].type.name
        type2 = self.cards[-2].type.name

        if type1.isdigit() and type2.isdigit():
            return int(type1) + int(type2)
        else:
            return None



