import random

from player import Player
from card import Card
from deck import Deck
from rule import *


class Game:
    """Total Chaos UNO Game class"""

    def __init__(self, players: list[str], eternalChaos: bool = False):
        """
        Total Chaos UNO Game class constructor
        :param players: list of players
        :param eternalChaos: determines whether eternal chaos mode is on
        """

        # draw and discard piles
        self.deck: Deck = Deck()
        self.discard: Deck = Deck('empty')

        # player list
        random.shuffle(players)
        self.players: list[Player] = [Player(name, self) for name in players]
        self.numPlayers: int = len(players)

        for i in range(self.numPlayers):
            self.players[i].draw(self.deck.deal(7))

        self.toMove: int = 0
        self.direction: int = 1

        # stacking
        self.drawStack: int = 0

        self.stackConditions = []

        self.legal: list[str] = []


        self.ruleDeck = None
        self.rules = None


