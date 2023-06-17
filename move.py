from card import *


class Move:
    """
    A move in Total Chaos UNO.
    Structured like a sandwich
    """

    def __init__(self,
                 middle: Card | list[Card] | set[Card] | None,
                 bottom: Card | list[Card] | set[Card] | None = None,
                 top: Card | list[Card] | set[Card] | None = None):
        """
        UNO Move class constructor
        :param middle: the cards played in the middle. Use a set if order does not matter, use a list if order matters.
        Use None if None of the cards must go in the middle
        :param bottom: Any one of the cards in this container must be on the bottom, and the rest can go anywhere else.
        Leave as None if any card can go on the bottom.
        :param top: Any one of the cards in this container must be on the top, and the rest can go anywhere else.
        Leave as None if any card can go on top.
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

    def __len__(self):
        return len(self.bottom) + len(self.middle) + len(self.top)

    def __getitem__(self, item):
        return self.tolist()[item]

    def __eq__(self, other):
        """
        other is a Move object
        :return: Returns True if the two moves are the same set, False if not
        """
        return all([set(getattr(self, layer)) == set(getattr(other, layer)) for layer in ['bottom', 'middle', 'top']])

    def can_replace(self, other) -> bool:
        """
        Determines if this move is a subset of the other move
        :return: returns True if the move can replace the other move, False if not
        """
        issubset: bool = self.toset().issubset(other.toset())
        return issubset and set(self.bottom).issubset(other.bottom) and set(self.top).issubset(other.top)

    def tolist(self) -> list[Card]:
        """Cast to list of cards"""
        return self.bottom + self.middle + self.top

    def toset(self) -> set[Card]:
        """Cast to set of cards"""
        return set(self.tolist())


class MoveChain:
    """Chain of moves played as 1 move due to jump-ins and stuff in Total Chaos UNO"""

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




