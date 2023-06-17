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
        self.discard: Deck = Deck('empty', maxCards=2)
        self.discard.append(self.deck.deal(1))
        self._discardHeight = 1

        # player list
        random.shuffle(players)
        self.players: list[Player] = [Player(name, self, i) for i, name in enumerate(players)]
        self.numPlayers: int = len(players)

        for i in range(self.numPlayers):
            self.players[i].draw(7)

        self.toMove: int = 0
        self.direction: int = 1

        # rules
        self.stack = Stacking(self, [])
        self.slapJacks = SlapJacks(self)
        self.swappyRules = SwappyRules(self)
        self.multiplier = 1

        self.legal: list[str] = []

        self.ruleDeck = None
        self.rules = None


    def next(self):
        """
        Ends the current player's turn and all active rules take effect
        """
        if len(self.discard) > self._discardHeight:
            top = self.discard.get_top()
            topType = top.type

            skip = topType.isSkip

            self.swappyRules.update()

            # slap jacks
            self.slapJacks.update()

            # action cards
            if topType.isReverse:
                self.reverse()
                # reverse becomes skip with 2 players
                if self.numPlayers == 2:
                    skip = True

            self.skip()  # next player

            # draw cards
            if top.type.drawAmount > 0:
                self.stack.stackCount += topType.drawAmount

            # stacking
            if self.stack.stackCount:
                canStack = False
                for card in self.players[self.toMove].hand:
                    if card in self.stack.conditions and (card and top):
                        canStack = True
                        break
                if canStack:
                    # let the player continue the stack
                    skip = False
                else:
                    # draw however many cards the stack requires * the multiplier
                    self.players[self.toMove].draw(self.deck.deal(self.stack.stackCount*self.multiplier))

            # skips
            if skip:
                self.skip()
        else:  # ignore action cards and go to the next player if the last player just drew
            self.skip()

        # update number of cards in the discard pile
        self._discardHeight = len(self.discard)

    def reverse(self):
        """UNO Reverse Card"""
        self.direction = -self.direction

    def skip(self):
        self.toMove = (self.toMove + self.direction) % self.numPlayers

    def cycle(self):
        """Swappy 0"""
        hand0 = self.players[0].hand

        for i in range(0, -self.direction*(self.numPlayers-1), -self.direction):
            self.players[i].hand = self.players[i-self.direction].hand

        self.players[self.direction].hand = hand0

    def trade(self, player1: int, player2: int):
        """Swappy 7"""
        tmp = self.players[player1].hand
        self.players[player1].hand = self.players[player2].hand
        self.players[player2].hand = tmp

