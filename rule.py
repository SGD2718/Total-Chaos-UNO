from abc import ABC, abstractmethod
from game import Game
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

    def apply(self, game: Game) -> None:
        if self.stackCount == 0:
            if self.game.deck.get_top().type.drawAmount:
                pass



