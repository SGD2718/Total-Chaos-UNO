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
            'swappy 0': self.swappyZero,
            'swappy 7': self.swappySeven,
            'depleters': self.depleters,
            'attack multiplier': self.attackMultiplier,
            'draw to play': self.drawToPlay,
            'revives': self.revives,
            'jump ins': self.jumpIns,
            'math': self.mathRules,
            'silent 6s': self.silentSixes
        }
        self.ruleDeck: list[RuleCard | RuleSlot] = []
        self.ruleDiscard: RuleSlot = RuleSlot([], False)
        self.ruleSlots: list[RuleSlot] = []
        self.reset_rules()

    def reset_rules(self) -> None:
        """
        Resets the rule deck, slots, and discard:
        3x starting slot
        4x extra slot
        5x slot remover
        4x stacking
        2x dupe jump-ins
        1x everything else
            - delayed blast
            - no u
            - makes a difference
            - dos
            - depleters
            - draw to play
            - slap jacks
            - half attack
            - double attack
            - silent 6s
            - swappy 0
            - swappy 7
            - total chaos
        """
        self.totalChaos = False
        self.ruleDeck = [RuleSlot(None, True) for _ in range(4)] + \
                        [SlotRemover(self, False) for _ in range(5)] + \
                        [ReviveCard(self, 'slot') for _ in range(2)] + \
                        [ReviveCard(self, 'discard') for _ in range(2)] + \
                        [RuleCard(self, 'jump-ins') for _ in range(2)] + \
                        [StackingCard(self, 'stacking (classical)', 'draw same') for _ in range(2)] + \
                        [StackingCard(self, 'stacking (total chaos)', 'draw any') for _ in range(2)] + \
                        [StackingCard(self, 'no u', 'reverse')] + \
                        [StackingCard(self, 'delayed blast', 'skip')] + \
                        [MathCard(self, 'dos', 'addition')] + \
                        [MathCard(self, 'makes a difference', 'subtraction')] + \
                        [MultiplierCard(self, 'half attack', 0.5)] + \
                        [MultiplierCard(self, 'double attack', 2)] + \
                        [RuleCard(self, 'depleters')] + \
                        [RuleCard(self, 'draw to play')] + \
                        [RuleCard(self, 'slap jacks')] + \
                        [RuleCard(self, 'silent 6s')] + \
                        [RuleCard(self, 'swappy 0')] + \
                        [RuleCard(self, 'swappy 7')]

        random.shuffle(self.ruleDeck)
        self.ruleDeck.insert(0, TotalChaosCard(self))
        self.ruleSlots = [RuleSlot(self.ruleDeck.pop()) for _ in range(3)]

    def draw_rule(self, slot: RuleSlot | int | None = None) -> None:
        """
        Draws a rule card and puts it into a slot
        :param slot: the rule slot object to add the rule to or the index of the rule slot.
        Leave as None if no slots are available.
        """

        if isinstance(slot, int):
            self.draw_rule(self.ruleSlots[slot])
        elif slot is None:
            self.draw_rule(self.ruleDiscard)
        else:
            if not self.totalChaos:
                ruleCard = self.ruleDeck.pop()
                if isinstance(ruleCard, RuleCard):
                    slot.append(ruleCard)  # new rule
                else:
                    self.ruleSlots.append(ruleCard)  # extra slot

    def discard_slot(self, slot: RuleSlot | int) -> None:
        """
        Discards a rule slot.
        :param slot: the rule slot object to add the rule to or the index of the rule slot.
        """
        if isinstance(slot, int):
            self.ruleDiscard += self.ruleSlots.pop(slot)
        else:
            self.ruleDiscard += slot
            self.ruleSlots.remove(slot)

    def _apply_rules(self) -> None:
        """
        applies active turn-based rules.
        """
        # stacking
        self.stacking.update(self.drawPile, len(self.discard) - self._discardHeight)

        # swappy rules
        self.swappyZero.update(self)
        self.swappySeven.update(self)

        # slap jacks
        self.slapJacks.update(self.drawPile, self.players)

    def _apply_action_cards(self) -> None:
        """
        Applies action cards after a player moved
        :return:
        """
        top = self.discard.get_top()
        topType = top.type

        skip = topType.isSkip

        if topType.isReverse:
            self.reverse()
            # reverse becomes skip with 2 players
            if self.numPlayers == 2:
                skip = True

        # skip if needed
        if skip and not (bool(self.stacking) and self.stacking.stackCount):
            self.next()

    def update(self) -> None:
        """
        Ends the current player's turn and all active rules take effect
        """
        # check if the player played something (instead of drawing)
        if len(self.discard) > self._discardHeight:
            self._apply_rules()
            self._apply_action_cards()

        self.next()
        self._discardHeight = len(self.discard)

    def draw(self) -> None:
        """Player draws cards from deck after clicking on the deck"""
        wasAttacked = self.stacking.stackCount > 0
        self.stacking.flush(self.players[self.toMove], self.attackMultiplier)

        # end player's turn if they received an attack or
        if wasAttacked or not bool(self.drawToPlay):
            self.next()

    def reverse(self) -> None:
        """Reverse turn order"""
        self.direction = -self.direction

    def next(self) -> None:
        """Next player"""
        self.toMove = (self.toMove + self.direction) % self.numPlayers

    def cycle_hands(self) -> None:
        """Each player passes their hand to the next player"""
        hand0 = self.players[0].hand

        for i in range(0, -self.direction*(self.numPlayers-1), -self.direction):
            self.players[i].hand = self.players[i-self.direction].hand

        self.players[self.direction].hand = hand0

    def trade_hands(self, player1: int, player2: int) -> None:
        """Two players trade hands"""
        tmp = self.players[player1].hand
        self.players[player1].hand = self.players[player2].hand
        self.players[player2].hand = tmp

