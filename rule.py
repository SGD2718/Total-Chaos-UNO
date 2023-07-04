import itertools
from abc import ABC, abstractmethod
from game import Game
from deck import Deck
from card import Card
from player import Player
from move import Move

# for silent sixes to detect talking
import tensorflow as tf
from tensorflow import keras

import itertools as itt


class Rule(ABC):
    """
    Total Chaos UNO Rule

    :ivar bool enabled = False: whether the rule is enabled
    """

    def __init__(self):
        """
        Total Chaos Rule abstract class constructor
        """
        self.enabled: bool = False

    def __bool__(self) -> bool:
        """Rule.__bool__() <==> bool(rule)
        :return Returns True if the rule is enabled, False if not"""
        return self.enabled

    def set_active(self, isActive: bool) -> None:
        """
        Enables or disables the rule
        :param isActive:
        """
        self.enabled = isActive


class MoveRule(Rule, ABC):
    """
    A rule that affects what cards are playable
    """

    @abstractmethod
    def get_moves(self, discard: Deck | Card, hand: list[Card] | Player, duplicate: bool = False) -> list[Move]:
        """
        :param discard: discard pile or the top card
        :param hand: the list of cards to choose from or the player that owns them
        :param duplicate: if the card must be a duplicate of the top card (for jump-ins)
        :return: list of additional moves that this rule allows
        """
        raise NotImplementedError


class ActionRule(Rule, ABC):
    """
    A rule that affects actions in the game
    """

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """
        Applies the rule, if applicable
        """
        raise NotImplementedError


class AttackMultiplier(Rule):
    """
    Multiplies the effect of draw cards.

    :ivar float multiplier: how much to multiply the effect of draw cards
    """

    def __init__(self):
        super().__init__()
        self.multiplier: float = 1
        self.enabled = True


class Stacking(MoveRule, ActionRule):
    """
    All Stacking Rules:
    Delayed blast: you can pass on an attack with a skip
    No U: you can give an attack back to the previous player with a reverse
    Normal stacking: +2 can be added to a +2, +4 can be added to +4
    Total chaos stacking: +4 and +2 cards can be added on top of each other.

    :ivar set[str] conditions: list of conditions that allow a card to stack. Conditions include colors (``'wild',
    'red', 'yellow', 'green', 'blue'``), card types (digits 0-9, ``'reverse', 'skip', 'draw 2', 'wild draw 4',
    'wild'``), ``'draw any'`` (+2s on +4s and vise versa, if compatible), and ``'draw same'`` (+2 on +2, +4 on +4,
     but no mixing)
    :ivar bool enabled: whether stacking is enabled
    :ivar int stackCount: number of cards that will be drawn when the stack ends
    """

    def __init__(self, conditions: set[str]):
        """
        Stacking class constructor
        :param conditions: list of card types that can stack
        """
        super().__init__()
        self.conditions = conditions
        self.stackCount = 0
        self.enabled = bool(len(conditions))

    def get_moves(self, discard: Deck | Card, hand: Player | list[Card], duplicate: bool = False) -> list[Move]:
        """
        Checks whether a player can stack
        :param discard: the discard pile or the top card
        :param hand: the player in question or their hand
        :param duplicate: if the card must be a duplicate (for jump-ins)
        :return: list of moves that could add to the stack
        """
        # make sure a stack exists
        if self.stackCount and self.enabled:
            # get top card
            if isinstance(discard, Deck):
                top = discard.get_top()
            else:
                top = discard

            if isinstance(hand, Player):
                hand = hand.hand

            return list(map(Move, filter(lambda card: self.can_stack(top, card), hand)))

        return []

    def can_stack(self, discard: Deck | Card, card: Card, duplicate: bool = False) -> bool:
        """
        Check if card is valid for stacking :param discard: either the discard pile or the card on top :param card:
        the card in question :param duplicate: whether the card has to be a duplicate of the top card (for jump-ins)
        :return: True if the card can be played on the stack, False otherwise. If the stack is at 0, then it returns
        False.
        """

        if isinstance(discard, Deck):
            top = discard.get_top()
        else:
            top = discard

        if duplicate:
            if card.is_dupe(top):
                return True
        elif card.type.drawAmount > 0:
            if (card and top) and 'draw any' in self.conditions:  # any valid draw card on a draw card
                return True
            elif card.type == top.type and 'draw same' in self.conditions:  # when +2s and +4s cannot mix
                return True
        elif card in self.conditions and (card and top):
            # card is stackable, and it can go on the top card
            return True

        return False

    def update(self, discard: Deck, cardsPlayed: int) -> None:
        """
        update stack and draw buffer
        :param discard: discard pile
        :param cardsPlayed: number of cards played last turn
        """
        self.enabled = bool(len(self.conditions))

        if not self.enabled:
            return

        newCards = discard[-cardsPlayed:]

        # add stuff to the stack
        for card in newCards:
            if self.can_stack(discard, card):
                self.stackCount += card.type.drawAmount
            else:
                # the stack was ended because someone did something illegal
                if self.stackCount > 0:
                    print("Someone did something illegal on a stack")
                self.stackCount = 0
                break

    def flush(self, player: Player, attackMultiplier: float | AttackMultiplier = 1) -> None:
        """
        Empties the stack and makes the player draw.
        If the stack is empty, the player draws 1.
        :param player: the unfortunate player who must draw every card in the stack
        :param attackMultiplier: how much attacks get multiplied
        """
        if self.stackCount:
            if isinstance(attackMultiplier, AttackMultiplier):
                attackMultiplier = attackMultiplier.multiplier
            player.draw(int(round(self.stackCount * attackMultiplier)))
        else:
            player.draw(1)

        self.stackCount = 0


class SlapJacks(ActionRule):
    """
    When the top 2 cards add up to 10, everyone must slap the discard pile. The last player to do so draws 2 cards.
    Players who slap incorrectly or fail to slap are also penalized 2 cards.

    :ivar int numPlayers: number of players in the game
    :ivar list[int] slapped: list of the indices of the players who have slapped
    :ivar bool shouldSlap: if the players should slap the deck
    :ivar bool enabled: if the rule is enabled
    """

    def __init__(self, numPlayers: int):
        super().__init__()
        self.numPlayers = numPlayers
        self.slapped: list[int] = []
        self.shouldSlap: bool = False

    def slap(self, player: Player) -> None:
        """
        Call when a player slaps the deck
        :param player: the player who slapped
        """
        if self.enabled:
            if self.shouldSlap:
                self.slapped.append(player.index)
                if len(self.slapped) == self.numPlayers:
                    # this is the last player to slap, so they draw 2
                    player.draw(2)
            else:
                player.draw(2)

    def update(self, discard: Deck, players: list[Player]) -> None:
        """
        Updates whether slaps should occur and penalizes bad slappers
        :param discard: the discard pile
        :param players: the list of players in the game
        """

        if not self.enabled:
            return

        if self.slapped and self.shouldSlap:
            # at least one person slapped
            for i, player in enumerate(players):
                if player.index not in self.slapped:
                    # punish the players who failed to slap
                    players[i].draw(2)

        # reset for next turn
        self.slapped = []
        self.shouldSlap = discard.top_sum() == 10


class SwappyZero(ActionRule):
    """
    When someone plays a 0, everyone passes their hand to the next player

    :ivar bool enabled: if swappy 0 is enabled
    """

    def update(self, game: Game) -> None:
        """
        Checks if a zero was played and cycles everyone's hand if so
        :param game: the game of UNO being played
        """

        if self.enabled and game.discard.get_top().type == '0':
            game.cycle_hands()


class SwappySeven(ActionRule):
    """
    When someone plays a 7, they pick someone to trade hands with.

    :ivar bool enabled: if swappy 7 is enabled
    """

    def update(self, game: Game) -> None:
        """
        Check if the top card is a 7 and have the player pick a player to trade hands with if so
        :param game: UNO Game being played
        """
        if self.enabled and game.discard.get_top().type == '7':
            # TODO: Implement method to choose someone's hand to take
            game.trade_hands(game.toMove, int(input("Who's hand do you want? ")))


class MathRules(MoveRule):
    """Math Rules: you use math to play 2 cards at once"""

    def __init__(self, addition: bool = False, subtraction: bool = False):
        """
        Math Rules class constructor
        :param addition: if we should check addition
        :param subtraction: if we should check subtraction
        """
        super().__init__()
        self.addition = addition
        self.subtraction = subtraction
        self.enabled = addition or subtraction

    def get_moves(self, discard: Deck | Card, hand: list[Card] | Player, duplicate: bool = False) -> list[Move]:
        """
        Checks for the possible math moves
        :param discard: discard pile or top card
        :param hand: the player whose hand we're checking or their hand itself
        :param duplicate: whether both cards must match the color of the top card
        :return: list of the pairs of cards in the player's hand that add up to the top card
        """
        self.enabled = self.addition or self.subtraction
        super().get_moves(discard, hand)

        top = discard.get_top() if isinstance(discard, Deck) else discard
        topName = top.type.name

        # make sure that the top card is a number card
        if not topName.isdigit():
            return []

        # convert hand to a list of cards
        if isinstance(hand, Player):
            hand = hand.hand

        # filter the player's hand for number cards
        numberCards = list(filter(lambda card: card.type.name.isdigit(), hand))

        # filter the player's hand by color if necessary
        if duplicate:
            numberCards = list(filter(lambda card: card.color == top.color, hand))

        # cannot do math with <2 cards
        if len(numberCards) < 2:
            return []

        # the value of the top card
        value = int(topName)

        mathPairs = []

        for card1, card2 in itertools.combinations(numberCards, 2):
            if self.addition and card1 + card2 == value:
                mathPairs.append(Move([card1, card2], enforceMatch=True))
            elif self.subtraction and abs(card1 - card2) == value:
                if value:  # non-zero difference
                    # smaller value below the bigger value for subtraction
                    if card1 < card2:
                        mathPairs.append(Move(None, bottom=card1, top=card2, enforceMatch=True))
                    else:
                        mathPairs.append(Move(None, bottom=card2, top=card1, enforceMatch=True))
                else:  # both cards have equal value
                    mathPairs.append(Move([card1, card2], enforceMatch=True))
        return mathPairs


class Depleters(MoveRule):
    """
    When you play 9, you can put all you cards that are the same color as the 9 under the 9

    :cvar class ColorGroup: A group of cards with of same color for a depleter. Assumes the cards are all the same color
    :ivar bool enabled: whether depleters are enabled
    """

    class ColorGroup:
        """
        A group of cards with of same color for a depleter. Assumes the cards are all the same color.

        :ivar list[Card] nines = []: list of nine-cards
        :ivar list[Card] cards = []: list of other cards
        """
        def __init__(self):
            self.nines: list[Card] = []
            self.cards: list[Card] = []

        def to_move(self) -> Move:
            """
            :return: Casts to `Move` object
            """
            return Move(self.cards, top=self.nines)

        def has_nines(self) -> bool:
            """
            :return: ``True`` if the color group has at least 1 nine card, ``False`` otherwise.
            """
            return bool(self.nines)

        def append(self, card: Card) -> None:
            """
            Appends a card to the group
            :param card: the card being added
            """
            if card == '9':
                self.nines.append(card)
            else:
                self.cards.append(card)

    def get_moves(self, discard: Deck | Card, hand: Player | list[Card], duplicate: bool = False) -> list[Move]:
        """
        Gets possible depleter moves
        :param discard: either the discard pile or the top card
        :param hand: the player whose hand we are testing, the list of cards that can be used, or the Move being played
        :param duplicate: whether the nine must be a duplicate of the top card
        :return: the list of possible depleter moves
        """

        if not self.enabled:
            return []

        top = discard.get_top() if isinstance(discard, Deck) else discard

        # set up color groups
        colorCards: dict[str: Depleters.ColorGroup] = dict()

        isNine: bool = top.type != '9'

        if duplicate and not isNine:
            return []
        elif duplicate or not isNine:
            colorCards[top.color.name] = Depleters.ColorGroup()
        else:
            colorCards = {
                'red': Depleters.ColorGroup(),
                'yellow': Depleters.ColorGroup(),
                'green': Depleters.ColorGroup(),
                'blue': Depleters.ColorGroup()
            }

        # convert hand to a list of Cards
        if isinstance(hand, Player):
            hand = hand.hand

        # filter cards by color
        for card in hand:
            if card != 'wild' and card.color in colorCards:
                colorCards[card.color.name].append(card)

        # get valid depleter moves
        depleters: list[Move] = []
        for _, group in colorCards:
            if group.has_nines():
                depleters.append(group.to_move())

        return depleters

    def update(self, *args, **kwargs) -> None:
        pass


class Revive(ActionRule):
    """
    Slot revive: rule cards can be revived from a slot
    Discard revive: rule cards can be revived from the discard pile
    """

    def update(self, *args, **kwargs) -> None:
        super().update()


class DrawToPlay(ActionRule):
    """
    Players must draw until they can play a card.
    """

    def update(self, *args, **kwargs) -> None:
        super().update()


class SilentSixes(ActionRule):
    """
    When a 6 is played, silent mode is toggled. In silent mode, players will face a 2-card penalty each time they
    talk, even if calling uno.

    Will probably use microphone + voice isolation + volume threshold to determine when someone is talking.
    """

    def update(self, *args, **kwargs) -> None:
        pass


class JumpIns(MoveRule, ActionRule):
    """
    Players can jump in out of turn with a card is identical to the top card.
    After jumping in, the play will continue from that player.
    """

    def get_moves(self, discard: Deck | Card, hand: Player | list[Card], duplicate: bool = False) -> list[Move]:
        """
        :param discard: Discard pile or the top card
        :param hand: list of cards to choose from or the player that owns them
        :param duplicate: whether to apply this rule
        :return: list of single-card jump-in moves
        """
        if not (self.enabled and duplicate):
            return []

        # hand becomes list of cards
        if isinstance(hand, Player):
            hand = hand.hand

        # discard becomes top card
        if isinstance(discard, Deck):
            discard = discard.get_top()

        # filter hand for cards that are duplicates of the top card
        return list(map(Move, filter(lambda card: card.is_dupe(discard), hand)))

    def update(self, player: Player | int, game: Game) -> None:
        """
        Call when a player makes a jump-in
        :param player: the player who performed the jump-in or their turn order index
        :param game: The game of UNO being played
        """

        if not self.enabled:
            return

        if isinstance(player, Player):
            player = player.index

        game.toMove = player
        game.next()



