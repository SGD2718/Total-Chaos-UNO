from card import *


class Move:
    """
    A move in Total Chaos UNO. Structured like a sandwich

    :ivar list[Card] bottom: one of the cards in this list must go first
    :ivar list[Card] middle: intermediate cards
    :ivar list[Card] top: one of the cards in this list must go last.
    :ivar bool enforceMatch: whether another move must have all the same cards in order to be interchangeable
    """

    def __init__(self,
                 middle: Card | list[Card] | set[Card] | None,
                 bottom: Card | list[Card] | set[Card] | None = None,
                 top: Card | list[Card] | set[Card] | None = None,
                 enforceMatch: bool = False):
        """
        UNO Move class constructor
        :param middle: the cards played in the middle. Use None if None of the cards must go in the middle
        :param bottom: Any one of the cards in this container must be on the bottom, and the rest can go anywhere else.
        Leave as None if any card can go on the bottom.
        :param top: Any one of the cards in this container must be on the top, and the rest can go anywhere else.
        Leave as None if any card can go on top.
        :param enforceMatch: whether another move must have all the same cards in order to be interchangeable
        """
        if isinstance(middle, Card):
            self.middle: list[Card] = [middle]
        elif middle is not None:
            self.middle: list[Card] = middle
        else:
            self.middle: list[Card] = []

        if isinstance(bottom, Iterable):
            self.bottom: list[Card] = list(bottom)
        elif bottom is not None:
            self.bottom: list[Card] = [bottom]
        else:
            self.bottom: list[Card] = []

        if isinstance(top, Iterable):
            self.top: list[Card] = list(top)
        elif top is not None:
            self.top: list[Card] = [top]
        else:
            self.top: list[Card] = []

        self.enforceMatch = enforceMatch

    def __len__(self) -> int:
        return len(self.bottom) + len(self.middle) + len(self.top)

    def __getitem__(self, index) -> Card:
        return self.tolist()[index]

    def __contains__(self, item: Card) -> bool:
        return item in self.tolist()

    def __eq__(self, other) -> bool:
        """
        other is a Move object
        :type other: Move
        :return: Returns True if the two moves are the same set, False if not
        """
        return all([set(getattr(self, layer)) == set(getattr(other, layer)) for layer in ['bottom', 'middle', 'top']]) \
            and len(self) == len(other)

    def without(self, cards: list[Card], emptyOnInvalid: bool = False):
        """
        Copies the move and removes cards from the copy going from bottom to top
        :param cards: the list of cards to exclude from the move
        :param emptyOnInvalid: determines whether to return an empty move if a card is not present in the move
        :return: A version of the move without the cards in cards
        :rtype: Move
        """
        bottom = self.bottom[:]
        middle = self.middle[:]
        top = self.top[:]

        for card in cards:
            if card in bottom:
                bottom.remove(card)
            elif card in middle:
                middle.remove(card)
            elif card in top:
                top.remove(card)
            elif emptyOnInvalid:
                return Move([], enforceMatch=self.enforceMatch)

        return Move(middle, bottom=bottom, top=top, enforceMatch=self.enforceMatch)

    def first_layer(self) -> list[Card]:
        """
        :return: the first non-empty layer in the move
        """
        if self.bottom:
            return self.bottom
        elif self.middle:
            return self.middle
        else:
            return self.top

    def can_replace(self, other) -> bool:
        """
        Determines if this move is a subset of another ``Move`` object
        :type other: Move
        :return: returns ``True`` if the move can replace ``other``, ``False`` if not
        """

        # check if the move is a non-empty subset of the other move
        if self.__len__():
            if (self.enforceMatch or other.enforceMatch) and \
                    not (self.toset() == other.toset() and len(self) == len(other)):
                return False
            elif not self.toset().issubset(other.toset()):
                return False
            # check if top and bottom are subsets or can go in the middle
            bottomMatches: bool = len(other.bottom) == 0 or set(self.bottom).issubset(other.bottom)
            topMatches: bool = len(other.top) == 0 or set(self.top).issubset(other.top)
            return bottomMatches and topMatches

        return False

    def tolist(self) -> list[Card]:
        """Cast to list of cards"""
        return self.bottom + self.middle + self.top

    def toset(self) -> set[Card]:
        """Cast to set of cards"""
        return set(self.tolist())


'''class MoveChain: # depreciated
    """
    Chain of moves played as 1 move due to jump-ins and stuff in Total Chaos UNO

    :ivar list[Move] moves: the moves played in the chain
    """

    def __init__(self, moves: list[Move]):
        self.moves: list[Move] = moves

    def __getitem__(self, index: int) -> Move:
        return self.moves[index]

    def __len__(self):
        """
        MoveChain.__len__() <==> len(MoveChain)
        :return: the number of moves in the chain
        """
        return len(self.moves)

    def __eq__(self, other):
        """Checks if all the moves are equal"""
        if self.__len__() == len(other):
            for move1, move2 in zip(self.moves, other.moves):
                if move1 != move2:
                    return False

        return False

    def num_cards(self) -> int:
        """
        :return: The number of cards in the chain
        """
        return sum(map(len, self.moves))

    def get_cards(self) -> list[Card]:
        """
        Converts the move chain to a list of cards
        :return: a list of cards.
        """
        asList = []
        for move in self.moves:
            asList += move.tolist()
        return asList

'''


