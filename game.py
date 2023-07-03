import random

from player import Player
from card import Card
from deck import Deck
from rule import *
from rule_slot import *
from rule_cards import *


class Game:
    """Total Chaos UNO Game class"""

    def __init__(self, players: list[str], eternalChaos: bool = False):
        """
        Total Chaos UNO Game class constructor
        :param players: list of players
        :param eternalChaos: determines whether eternal chaos mode is on
        """

        # draw and discard piles
        self.drawPile: Deck = Deck()
        self.discard: Deck = Deck('empty', maxCards=2)
        self.discard.append(self.drawPile.deal(1))
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
        self.totalChaos: bool = eternalChaos

        self.stacking = Stacking(set())
        self.slapJacks = SlapJacks(self.numPlayers)
        self.swappyZero = SwappyZero()
        self.swappySeven = SwappySeven()
        self.depleters = Depleters()
        self.attackMultiplier = AttackMultiplier()
        self.drawToPlay = DrawToPlay()
        self.revives = Revive()
        self.jumpIns = JumpIns()
        self.mathRules = MathRules()
        self.silentSixes = SilentSixes()

        self.rules = {
            'stacking': self.stacking,
            'slap jacks': self.slapJacks,
            'swappy zero': self.swappyZero,
            'swappy seven': self.swappySeven,
            'depleters': self.depleters,
            'attack multiplier': self.attackMultiplier,
            'draw to play': self.drawToPlay,
            'revives': self.revives,
            'jump ins': self.jumpIns,
            'math': self.mathRules,
            'silent sixes': self.silentSixes
        }
        self.ruleDeck: list[RuleCard | RuleSlot] = list(self.rules.values()) + [RuleSlot(), RuleSlot(), RuleSlot()]
        self.ruleDiscard: RuleSlot = RuleSlot([], False)
        self.ruleSlots: list[RuleSlot] = []

    def reset_rules(self):
        pass

    def next(self):
        """
        Ends the current player's turn and all active rules take effect
        """
        if len(self.discard) > self._discardHeight:
            top = self.discard.get_top()
            topType = top.type

            self.stacking.update(self.drawPile, len(self.discard) - self._discardHeight)

            skip = topType.isSkip and not (bool(self.stacking) and self.stacking.stackCount)

            self.swappyZero.update(self)
            self.swappySeven.update(self)

            # slap jacks
            self.slapJacks.update(self.drawPile, self.players)

            # action cards
            if topType.isReverse:
                self.reverse()
                # reverse becomes skip with 2 players
                if self.numPlayers == 2:
                    skip = True

            self.skip()  # next player

            # skips
            if skip:
                self.skip()
        else:  # ignore action cards and go to the next player if the last player just drew
            self.skip()

        # update number of cards in the discard pile
        self._discardHeight = len(self.discard)

    def draw(self):
        """Player draws cards from deck after clicking on the deck"""
        self.stacking.flush(self.players[self.toMove], self.attackMultiplier)

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

