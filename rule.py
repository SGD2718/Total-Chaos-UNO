import itertools
from abc import ABC, abstractmethod
from game import Game
from deck import Deck
from card import Card
from player import Player

import itertools as itt


class Rule(ABC):
    """Total Chaos UNO Rule"""

    def __init__(self):
        """
        Total Chaos Rule abstract class constructor
        """
        self.enabled: bool = False

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """
        Applies the rule, if applicable
        """
        if not self.enabled:
            return


class Stacking(Rule):
    """
    All Stacking Rules:
    delayed blast: you can pass on an attack with a skip
    no u: you can give an attack back to the previous player with a reverse
    normal stacking: +2 can be added to a +2, +4 can be added to +4
    total chaos stacking: +4 and +2 cards can be added on top of each other.
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

    def can_stack(self, discard: Deck, player: Player) -> bool:
        """Checks whether a player can stack
        :param discard: the discard pile
        :param player: the player in question"""
        # make sure a stack exists
        if self.stackCount and self.enabled:
            for card in player.hand:
                if card in self.conditions and (card and discard.get_top()):
                    return True
        return False

    def update(self, discard: Deck, cardsPlayed: int, player: Player) -> bool:
        """
        update stacking
        :param discard: discard pile
        :param cardsPlayed:
        :param player:
        :return: returns True if the player drew, False otherwise
        """
        self.enabled = bool(len(self.conditions))
        super().update()
        # draw cards

        newCards = discard[-cardsPlayed:]

        # add stuff to the stack
        for card in newCards:
            if card in self.conditions:
                self.stackCount += card.type.drawAmount
            else:
                # the stack was ended because someone did something illegal
                if self.stackCount > 0:
                    print("Someone did something illegal on a stack")

                self.stackCount = 0
                break

        if not self.can_stack(discard, player):
            player.draw(self.stackCount)
            self.stackCount = 0
            return True

        return False


class SlapJacks(Rule):
    """When the top 2 cards add up to 10: everyone must slap the discard pile. The last player to do so draws 2 cards.
    Players who slap incorrectly or fail to slap are also penalized 2 cards."""

    def __init__(self, numPlayers: int):
        super().__init__()
        self.numPlayers = numPlayers
        self.slapped: list[int] = []
        self.shouldSlap: bool = False

    def slap(self, player: Player):
        """When a player slaps the deck"""
        if self.enabled:
            if self.shouldSlap:
                self.slapped.append(player.index)
            else:
                player.draw(2)

    def update(self, discard: Deck, players: list[Player]):
        """
        Updates whether slaps should occur and penalizes bad slappers
        :param discard: the discard pile
        :param players: the list of players in the game
        """
        super().update()
        # everyone slapped
        if len(self.slapped) == self.numPlayers:
            # punish last player to slap
            players[self.slapped[-1]].draw(2)
        elif self.slapped:
            # at least one person slapped
            for i, player in enumerate(players):
                if player.index not in self.slapped:
                    # punish the players who failed to slap
                    players[i].draw(2)

        self.slapped = []
        self.shouldSlap = discard.top_sum() == 10


class SwappyZero(Rule):
    """When someone plays a 0, everyone passes their hand to the next player"""

    def update(self, game: Game) -> None:
        super().update()
        if game.discard.get_top().type == '0':
            game.cycle()


class SwappySeven(Rule):
    """Swappy 7"""

    def update(self, game: Game) -> None:
        if game.discard.get_top().type == '7':
            # TODO: Implement method to choose someone's hand to take
            game.trade(game.toMove, int(input("Who's hand do you want? ")))


class MathRules(Rule):
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

    def update(self, discard: Deck, player: Player, checkColor: bool = False) -> list[tuple[Card, Card] | set[Card, Card]]:
        """
        Checks for the possible dos things
        :param discard:
        :param player: the player whose hand we're checking
        :param checkColor: whether both cards must match the color of the top card
        :return: list of the pairs of cards in the player's hand that add up to the top card
        """

        top = discard.get_top()
        topName = top.type.name

        # make sure that the top card is a number card
        if not topName.isdigit():
            return []

        # filter the player's hand for number cards
        numberCards = list(filter(lambda card: card.type.name.isdigit(), player.hand))

        # filter the player's hand by color if necessary
        if checkColor:
            numberCards = list(filter(lambda card: card.color == top.color, player.hand))

        # cannot do math with <2 cards
        if len(numberCards) < 2:
            return []

        # the value of the top card
        value = int(topName)

        mathPairs = []

        for card1, card2 in itertools.combinations(numberCards, 2):
            if self.addition and card1 + card2 == value:
                mathPairs.append((card1, card2))
                mathPairs.append((card2, card1))
            elif self.subtraction and abs(card1 - card2) == value:
                if value:  # non-zero difference
                    # smaller value below the bigger value for subtraction
                    mathPairs.append((card1, card2) if card1 < card2 else (card2, card1))
                else:  # both cards have equal value
                    mathPairs.append({card1, card2})
        return mathPairs


class Depleters(Rule):
    """When you play 9, you can put all you cards that are the same color as the 9 under the 9"""

