"""
Total Chaos UNO Player class implementation

Contains the Player class.
"""

from card import Card
from rule import *
from game import Game
from deck import Deck
from move import Move, MoveChain


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

        self._moveBuffer: list[Card] = []
        self._topCard: Card = game.discard.get_top()
        self._legalMoves: list[Move] = []

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
            self.hand += self.game.drawPile.deal(cards)

    def play_buffered_cards(self) -> bool:
        """
        Plays cards in the move buffer from the player's hand
        :return: ``True`` if the play was successful, ``False`` if not
        """
        if self.is_move_complete():
            self.game.discard.append(self._moveBuffer)
            self._moveBuffer.clear()
            return True
        return False

    def get_legal_continuations(self, top: Card = None) -> list[bool]:
        """
        Determines which cards can go next in a move
        :param top: the top card. Leave as ``None`` to get the top card automatically
        :return: a boolean-encoded list indicating if each card is legal or not
        """

        myTurn = self.game.toMove == self.index
        continuations: list[bool] = []

        if top is None:
            top = self._topCard

        # check if we are allowed to play moves right now
        if not (myTurn or bool(self.game.jumpIns)):
            return [False] * len(self.hand)

        # check if this is the first card
        if (not self._moveBuffer) or (bool(self.game.jumpIns) and top == self._moveBuffer[-1]):
            for card in self.hand:
                for move in self._legalMoves:
                    if card in move.first_layer():
                        continuations.append(True)
                        break
                else:
                    continuations.append(False)
        else:
            # filter moves
            moves = []
            for move in self._legalMoves:
                # get the other cards that can/must be in the move
                reduced = move.without(self._moveBuffer, True)
                # ensure that cards can still be added to the move
                # and ensure that a top card to complete the move is still present
                if len(reduced) and bool(move.top) == bool(reduced.top):
                    moves.append(reduced)

            # determine which cards can continue the move
            for card in self.hand:
                for move in moves:
                    if card in move:
                        continuations.append(True)
                        break
                else:
                    continuations.append(False)

        return continuations

    def is_move_complete(self, start: int = 0, end: int = -1) -> bool:
        """
        Check if the buffered move is complete/valid.
        WARNING: Assumes that legal moves have been updated
        :param start: starting index in move buffer
        :param end: ending index in move buffer
        :return: whether the buffered move is complete as is
        """
        move = Move(self._moveBuffer[start:end], bottom=self._moveBuffer[start], top=self._moveBuffer[end])
        return any(map(move.can_replace, self._legalMoves))

    def update_legal_moves(self, top: Card = None) -> None:
        """
        Updates stored list of legal moves
        :param top: top card on discard pile
        """
        myTurn = self.index == self.game.toMove
        if top is None:
            top = self._topCard

        self._legalMoves.clear()

        # normal moves
        if myTurn:
            for card in self.hand:
                if card and top:
                    self._legalMoves.append(Move(card))
        elif not bool(self.game.jumpIns):
            # no legal moves if we aren't allowed to play right now, so terminate here
            return

        # special moves from rules
        rules = list(filter(lambda r: isinstance(r, MoveRule) and bool(r), self.game.rules.values()))

        for rule in rules:
            self._legalMoves.extend(rule.get_moves(top, self.hand, not myTurn))

    def interrupt_move(self) -> None:
        """
        interrupts the player's move because another player went
        Updates _topCard private attribute
        """
        newTop = self.game.discard.get_top()

        # TODO: improve legality inference
        if self._topCard != newTop and not (self.game.toMove == self.index and (self._moveBuffer[0] and newTop)):
            self.hand += self._moveBuffer
            self._moveBuffer = []

        self._topCard = newTop

    def move_card_to_buffer(self, card: Card | int) -> bool:
        """
        Moves a card from the player's hand to the move buffer
        :param card: the card being added or the index in the player's hand
        :return: True if successful, False if not
        """
        if isinstance(card, int):
            if -len(self.hand) <= card < len(self.hand):
                card = self.hand[card]
            else:
                return False
        else:
            if card not in self.hand:
                return False

        self._moveBuffer.append(card)
        self.hand.remove(card)
        return True

    def pop_buffer(self, numCards: int = 1) -> bool:
        """
        Moves a card from the move buffer back to the player's hand
        :param numCards: number of cards to bring back. Use -1 to add everything back.
        :return: True if successful, False if not
        """
        if numCards == -1:
            self.hand.extend(self._moveBuffer)
            self._moveBuffer.clear()
            return True
        elif numCards <= len(self._moveBuffer):
            for _ in range(numCards):
                self.hand.append(self._moveBuffer.pop())
            return True
        return False

    def slap(self) -> None:
        """Slap the deck for slap jacks"""
        self.game.slapJacks.slap(self)
















