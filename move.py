from card import *


class Move(Iterable):
    """A move in Total Chaos UNO"""

    def __init__(self, bottom: Card | set[Card] | list[Card], top: Card | Iterable[Card | str] | set[Card | str] | None = None):
        """
        UNO Move class constructor
        :param bottom: the cards played in the move on the bottom.
        Use a set if order does not matter, use a list if order matters.
        :param top: Any one of the cards in this container must be on the top, and the rest can go anywhere else.
        Leave as None if any card can go on top. It is assumed that the rest of these cards would
        """
        if isinstance(bottom, Card):
            self.bottom = [bottom]
        else:
            self.bottom = bottom

        if isinstance(top, Card):
            self.top = [top]
        else:
            self.top = top

    def tolist(self):
        if self.top is None:
            return list(self.bottom)
        else:
            return list(self.bottom) + list(self.top)

    def __setitem__(self, key, value):
    def __



class MoveChain:
    """Chain of moves played as 1 move due to jump-ins and stuff in Total Chaos UNO"""

    def __init__(self, moves: list[Move]):
        self.moves: list[Move] = moves

    def __list__(self):
        asList = []
        for move in self.moves:
            asList += move.tolist()
        return asList

    def __getitem__(self, item):
        return self.__list__()[item]