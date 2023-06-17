from card import Card
from rule import Rule
from game import Game


class Player:
    """UNO Player class"""

    def __init__(self, name: str, game: Game, index: int, hand: list[Card] = None):
        """
        UNO Player class constructor
        :param name: player's name
        :param index: the player's turn order number
        :param game: the game of UNO the player is playing
        :param hand: the player's cards
        """
        self.game: Game = game
        self.name: str = name
        self.index: int = index
        self.hand: list[Card] = [] if hand is None else hand
        self.canJumpIn: bool = False

        self.slapped = False

    def __str__(self):
        return self.name

    def __int__(self):
        return len(self.hand)

    def draw(self, cards: list[Card] | int) -> None:
        """
        Draw cards
        :param cards: the list cards to be drawn or the number of cards to be drawn
        """
        if isinstance(cards, list):
            self.hand += cards
        else:
            self.hand += self.game.deck.deal(cards)

    def play(self, cards: Card | list[Card]) -> list[Card]:
        """
        Plays cards from the player's and
        :param cards: the cards being played
        """

        # convert cards to list
        if isinstance(cards, Card):
            cards = [cards]

        isJumpIn: bool = self != self.game.toMove

        i: int = 0
        top = self.game.deck.get_top()

        if self.game.discard:
            return False

        while i < len(cards):
            if cards[0] == self.game.discard.get_top():
                pass

        if isinstance(cards, list):
            for card in cards:
                assert (card in self.hand)
                self.hand.remove(card)
        else:
            assert (cards in self.hand)
            self.hand.remove(cards)

        return cards

    def get_legal(self, deck, rules: list[Rule]) -> list[list[Card]]:
        pass

    def slap(self):
        """Slapping for slap jacks"""
        self.game.slapJacks.slap(self)
