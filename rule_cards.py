"""
3x starting slot
4x extra slot
5x slot remover
4x stacking
2x dupe jump ins
1x everything else
"""


from rule_slot import RuleSlot
from rule import *
from game import Game


class RuleCard:
    """
    Rule Card object class

    :ivar bool isActive: whether the rule is active
    :ivar str ruleName: name of the rule
    """

    def __init__(self, game: Game, ruleName: str, isActive: bool = False):
        """

        :param game: the game of UNO the rule card is part of
        :param ruleName: name of the rule
        :param isActive: whether the rule is active
        """
        self._game = game
        self.isActive = isActive
        self.ruleName = ruleName

    def __eq__(self, other) -> bool:
        """

        :param other: Other rule card
        :type other: RuleCard
        """
        return self.ruleName == other.ruleName

    def set_active(self, isActive: bool, slot: RuleSlot, **kwargs) -> None:
        """
        Activates or deactivates the rule card
        :param isActive: whether the rule should be active (True) or inactive (False)
        :param slot: the slot the rule is placed in
        """
        '''if slot is self._game.slotDiscard:
            self.isActive = False
        '''
        if isActive != self.isActive:
            self.isActive = isActive
            self._game.rules[self.ruleName].enabled = isActive


class StackingCard(RuleCard):
    """
    Rule cards for stacking
    :ivar str condition: a single condition for the stacking rule. Uses the same entries as the stacking rule
    :ivar str ruleName: name of the rule
    :ivar bool isActive: whether the rule is active
    """

    def __init__(self, game: Game, ruleName: str, condition: str, isActive: bool = False):
        """

        :param game: game of UNO being played
        :param ruleName: name of the rule
        :param condition: a single stacking condition. Conditions include colors (``'wild',
        'red', 'yellow', 'green', 'blue'``), card types (digits 0-9, ``'reverse', 'skip', 'draw 2', 'wild draw 4',
        'wild'``), ``'draw any'`` (+2s on +4s and vise versa, if compatible), and ``'draw same'`` (+2 on +2, +4 on +4,
         but no mixing)
        :param isActive: whether the rule is active
        """
        super().__init__(game, ruleName, isActive)
        self.condition = condition

    def set_active(self, isActive: bool, slot: RuleSlot, **kwargs) -> None:
        self.isActive = isActive
        if isActive:
            self._game.rules['stacking'].conditions.add(self.condition)
        else:
            self._game.rules['stacking'].conditions.discard(self.condition)


class MathCard(RuleCard):
    """
    Rule cards for stacking
    :ivar str operation: either ``'addition'`` or ``'subtraction'``
    :ivar str ruleName: name of the rule card
    :ivar bool isActive: whether the rule is active
    """

    def __init__(self, game: Game, ruleName: str, operation: str, isActive: bool = False):
        super().__init__(game, ruleName, isActive)
        assert operation == 'addition' or operation == 'subtraction'
        self.operation: str = operation

    def set_active(self, isActive: bool, slot: RuleSlot, **kwargs) -> None:
        self.isActive = isActive
        setattr(self._game.rules['math'], self.operation, isActive)


class ReviveRuleCard(RuleCard):
    """Rule card for slot and discard revives"""

    def __init__(self, game: Game, mode: str = 'slot', isActive: bool = False):
        """

        :param game: the game the rule card is in
        :param mode: 'slot' to make this a slot revive, 'discard' to make this a discard revive.
        :param isActive: whether the rule is active
        """
        super().__init__(game, mode+' revive', isActive)
        self.isSlotRevive = mode == 'slot'

    def get_slot(self) -> RuleSlot:
        """
        gets the slot for the rule card
        """
        pass

    def set_active(self, isActive: bool, slot: RuleSlot, **kwargs) -> None:
        super().set_active(isActive, slot)

        if not self.isSlotRevive:
            slot = self._game.ruleDiscard

        # TODO: get choice of rule card
        # TEMPORARY
        ruleIndex = int(input("Enter index of rule in slot: "))
        slot.revive(ruleIndex)


class TotalChaosCard(RuleCard):
    """
    Total Chaos rule card

    :ivar int lives: number of remaining lives. Each time a rule addition card is played, it can either add or remove lives from the total chaos card.
    :ivar str ruleName = 'total chaos': the name of the total chaos rule card is ``'total chaos'``
    :ivar bool isActive: whether total chaos is activated
    """

    def __init__(self, game: Game, isActive: bool = False):
        """

        :param game: game of UNO being played
        :param isActive: whether the total chaos card starts active
        """
        super().__init__(game, 'total chaos', isActive)
        self.lives: int = 3

    def set_active(self, isActive: bool, slot: RuleSlot, **kwargs) -> None:
        if isActive and not self.isActive:
            self.isActive = True
            self.lives = 3
            for name, rule in self._game.rules:
                rule.set_active(True)

            # special rule properties
            self._game.rules['math'].addition = True
            self._game.rules['math'].subtraction = True
            self._game.rules['stacking'].conditions = {'reverse', 'skip', 'draw any'}
            self._game.rules['attack multiplier'].multiplier = 1
            self._game.totalChaos = True

        elif self.isActive:
            self.lives += 1 if isActive else -1
            if self.lives <= 0:
                self.isActive = False
                self._game.reset_rules()

    def add_lives(self, numLives: int) -> None:
        """
        Adds lives to the total chaos card
        :param numLives: number of lives to add.
        """
        self.lives += numLives

    def remove_lives(self, numLives: int) -> None:
        """
        Removes lives from the total chaos card
        :param numLives: number of lives to remove.
        """
        self.lives -= numLives


class SlotRemover(RuleCard):
    """Deletes slot and puts it in discard pile"""

    def __init__(self, game: Game, isActive: bool = False):
        """

        :param game: game of UNO being played
        :param isActive: whether the slot remover starts active
        """
        super().__init__(game, 'slot remover', isActive)

    def set_active(self, isActive: bool, slot: RuleSlot, **kwargs) -> None:
        super().set_active(isActive, slot)
        if self.isActive:
            self._game.ruleDiscard += slot
            self._game.ruleSlots.remove(slot)

        self.isActive = False
