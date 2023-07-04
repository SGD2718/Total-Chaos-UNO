from rule_cards import *


class RuleSlot:
    """
    A slot for rule cards, and the rule cards it holds.

    :ivar list[RuleCard] ruleCards: list of rule cards in the slot
    :ivar bool topActive: whether to activate the top rule.
    """

    def __init__(self, ruleCards: list[RuleCard] | None = None, topActive: bool = True):
        """

        :param ruleCards: list of rule cards on the slot. None by default.
        :param topActive: whether to activate the top rule. True by default.
        """
        self.ruleCards = [] if ruleCards is None else ruleCards
        self.topActive = topActive

        for i in range(len(ruleCards)):
            self.ruleCards[i].set_active(False)

        self.ruleCards[-1].set_active(topActive)

    def __eq__(self, other) -> bool:
        """
        :type other: RuleSlot
        """
        return len(self) == len(other) and all(map(RuleCard.__eq__, self.ruleCards, other.ruleCards))

    def __len__(self):
        return len(self.ruleCards)

    def __contains__(self, item: RuleCard) -> bool:
        return item in self.ruleCards

    def __getitem__(self, i: int) -> RuleCard:
        """Get rule card at index i"""
        return self.ruleCards[i]

    def __setitem__(self, i: int, v: RuleCard):
        """Set rule card at index i to v"""
        self.ruleCards[i] = v

    def __add__(self, other):
        """

        :type other: RuleSlot | RuleCard
        :rtype: RuleSlot
        """
        self.ruleCards[-1].set_active(False, self)
        if isinstance(other, RuleCard):
            slot2 = RuleSlot(self.ruleCards[:])
            slot2.append(other)
            return slot2

        return RuleSlot(self.ruleCards + other.ruleCards)

    def append(self, ruleCard: RuleCard) -> None:
        """
        Appends a new rule card to the top of the slot and activates it if needed.
        Deactivates the previous top rule card.
        :param ruleCard: new rule card to add
        """

        # deactivate top rule
        if self.ruleCards:
            self.ruleCards[-1].set_active(False)

        # activate new rule
        self.ruleCards.append(ruleCard)

        self.ruleCards[-1].set_active(self.topActive)

    def pop(self, ruleCard: int | RuleCard = -1) -> None:
        """
        Removes rule card from slot
        :param ruleCard: rule card being removed or its index in the slot
        """
        if isinstance(ruleCard, int):
            self.ruleCards.pop(ruleCard)
        else:
            self.ruleCards.remove(ruleCard)

    def revive(self, ruleCard: RuleCard | int, targetSlot='self') -> None:
        """
        Sets top rule card to something from the middle of the deck.
        :param ruleCard: either the index of the rule card in the slot or the rule card itself to be revived
        :param targetSlot: slot receiving the revived card. leave as ``'self'`` to make this slot receive the card.
        :type targetSlot: RuleSlot | str
        """

        # get the rule card itself
        if isinstance(ruleCard, int):
            ruleCard = self.ruleCards[ruleCard]

        # rearrange
        self.ruleCards.remove(ruleCard)

        if targetSlot == 'self':
            self.append(ruleCard)
        else:
            targetSlot.append(ruleCard)

