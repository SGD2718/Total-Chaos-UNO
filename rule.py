from abc import ABC, abstractmethod
from game import Game
from player import Player
from card import CardType, Card

class Rule(ABC):
    """Total Chaos UNO Rule"""

    def __init__(self, name: str, description: str):
        """Rule abstract class constructor"""
        self.name: str = name
        self.description: str = description

    @abstractmethod
    def apply(self, game: Game) -> None:
        """
        Applies the rule, if applicable
        :param game: the game that the rule is used in
        """
        pass


class Stacking:
    """Stacking Rule class"""

    def __init__(self, conditions: list[str]):
        """
        Stacking class constructor
        :param conditions: list of card types that can stack
        """
        self.conditions = conditions
        self.stackCount = 0
        self.enabled = bool(len(conditions))

    def apply(self, game: Game) -> None:
        if self.stackCount == 0:
            if self.game.deck.get_top().type.drawAmount:
                pass


class SlapJacks:
    """Slap Jacks Rule class"""

    def __init__(self):
        self.slapped: list[int] = []
        self.shouldSlap: bool = False
        self.enabled: bool = False

    def slap(self, player: Player):
        """When a player slaps the deck"""
        if self.enabled:
            if self.shouldSlap:
                self.slapped.append(player.index)
            else:
                player.draw(player.game.deck.deal(2))

    def update(self, game: Game):
        """Updates whether slaps should occur and penalizes bad slappers"""
        if len(self.slapped) == game.numPlayers:
            game.players[self.slapped[-1]].draw(game.deck.deal(2))
        elif self.slapped:
            for i, player in enumerate(game.players):
                if player.index not in self.slapped:
                    game.players[i].draw(game.deck.deal(2))

        self.slapped = []
        self.shouldSlap = game.discard.top_sum() == 10
