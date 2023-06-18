"""
Total Chaos UNO Player class implementation

Contains the Player class.
"""

from card import Card
from rule import Rule
from game import Game


class Player:
    """
    UNO Player class

    :ivar name: The player's name
    :ivar game: The UNO game the player belongs to
    :ivar index: The player's index in the turn order
    :ivar hand: The list of card in the player's hand
    """

    def __init__(self, name: str, game: Game, index: int, hand: list[Card] = None):
        """
        UNO Player class constructor
        :param name: player's name
        :param index: the player's turn order number
        :param game: the game of UNO the player is playing
        :param hand: (optional) the player's cards
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
        Draw cards from deck
        :param cards: the list cards to be drawn or the number of cards to be drawn
        """
        if isinstance(cards, list):
            self.hand += cards
        else:
            self.hand += self.game.deck.deal(cards)

    def play(self, cards: Card | list[Card]) -> list[Card]:
        """
        Plays cards from the player's hand
        :param cards: the card(s) being played
        """
        # TODO: change this to work with move chain
        # TODO: make player able to change color when wild card is placed
        # TODO: get legal moves

        # convert cards to list
        if isinstance(cards, Card):
            cards = [cards]

        isJumpIn: bool = self != self.game.toMove

        i: int = 0
        top = self.game.deck.get_top()

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

    def slap(self) -> None:
        """Slap the deck for slap jacks"""
        self.game.slapJacks.slap(self)
















