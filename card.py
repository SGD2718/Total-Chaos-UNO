from typing import Iterable


class CardColor:
    """UNO Card Color class"""

    def __init__(self, name: str, color: str | Iterable[int, int, int] | Iterable[int, int, int, int]):
        """
        Color class constructor
        :param name: color name
        :param color: displayed hex, RGB, or RGBA color
        """
        if isinstance(color, str):
            self.hex: str = color
        else:
            self.hex: str = f"#{''.join([hex(i)[:2] for i in color])}"

        self.name: str = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == str(other)

    def __hash__(self):
        return


class CardType:
    """UNO Card Type class"""

    def __init__(self, name: str, drawAmount: int = 0, isWild: bool = False, isSkip: bool = False,
                 isReverse: bool = False, imagePath: str = None):
        """
        UNO Card Type class constructor
        :param name: name of the card type
        :param imagePath: card image file path
        :param drawAmount: number of cards the next player must draw
        :param isWild: if the card is a wildcard
        :param isSkip: if the card will skip the next player
        :param isReverse: if the card will reverse the turn order
        """

        self.name: str = name
        self.imagePath: str = imagePath
        self.isReverse: bool = isReverse
        self.drawAmount: int = drawAmount
        self.isSkip: bool = isSkip
        self.isWild: bool = isWild

    def __hash__(self):
        if self.name.isdigit():
            return int(self.name)
        return 10 + self.isReverse + 2*self.isSkip + 4*self.isWild + 8*self.drawAmount

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == str(other)

    def __and__(self, other):
        return self.isWild or self.name == str(other)

    def __add__(self, other):
        if self.name.isdigit() and other.name.isdigit():
            return int(self.name) + int(other.name)
        else:
            return None

    def __sub__(self, other):
        if self.name.isdigit() and other.name.isdigit():
            return int(self.name) - int(other.name)
        else:
            return None

    def __lt__(self, other):
        if self.name.isdigit() and other.name.isdigit():
            return int(self.name) < int(other.name)
        else:
            return None

    def __gt__(self, other):
        if self.name.isdigit() and other.name.isdigit():
            return int(self.name) > int(other.name)
        else:
            return None

    def __le__(self, other):
        if self.name.isdigit() and other.name.isdigit():
            return int(self.name) <= int(other.name)
        else:
            return None

    def __ge__(self, other):
        if self.name.isdigit() and other.name.isdigit():
            return int(self.name) >= int(other.name)
        else:
            return None


class Card:
    """
    UNO Card Class
    """

    # static class attributes

    # card colors
    COLORS = {
        'wild': CardColor('wild', '#111111'),
        'red': CardColor('red', '#e00000'),
        'yellow': CardColor('yellow', '#ffe000'),
        'green': CardColor('green', '#00e000'),
        'blue': CardColor('blue', '#0060ff')
    }

    ACTION_CARDS = {
        'skip': CardType('skip', isSkip=True),
        'reverse': CardType('reverse', isReverse=True),
        'draw 2': CardType('draw 2', drawAmount=2, isSkip=True),
        'wild draw 4': CardType('wild draw 4', drawAmount=4, isSkip=True, isWild=True),
        'wild': CardType('wild', isWild=True),
    }

    def __init__(self, color: str | CardColor, cardType: int | str,
                 ruleAdditions: int | Iterable[int] = 0):
        """
        Card class constructor
        :param color: the card's color. Can be 'wild', 'red', 'yellow', 'green', or 'blue'
        :param cardType: The type of card. Use 0-9 for a number card. Use 'skip', 'reverse', 'draw 2', 'wild draw 4',
        or 'wild' for the respective action cards
        :param ruleAdditions: the number of rules the player must add. If an
        iterable is provided, it allows for the player to add varying amounts of rules.
        """

        # set card color
        self.color = None
        self.set_color(color)

        # set card type
        self.type = None
        self.set_type(cardType)

        # set card rule additions
        if isinstance(ruleAdditions, int):
            self.ruleAdditions = {ruleAdditions}
        elif isinstance(ruleAdditions, Iterable):
            assert all(map(lambda numRules: isinstance(numRules, int), ruleAdditions))
            self.ruleAdditions = set(ruleAdditions)

    def __eq__(self, other):
        """Determines if 2 cards are identical"""
        if isinstance(other, Card):
            return self.type == other.type and self.color == other.color \
                and self.ruleAdditions == other.ruleAdditions
        elif isinstance(other, str):
            return self.color.name == other or self.type.name == other
        else:
            return False

    def __str__(self):
        return f'{self.color.name} {self.type.name}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.type) + 128 * ['wild', 'red', 'yellow', 'green', 'blue'].index(self.color.name)

    def __and__(self, other):
        """Determines if 2 cards are compatible"""
        return self.color == other.color or (self.type and other.type)

    def __add__(self, other):
        return self.type + other.type

    def __sub__(self, other):
        return self.type - other.type

    def __lt__(self, other):
        return self.type < other.type

    def __gt__(self, other):
        return self.type > other.type

    def __le__(self, other):
        return self.type <= other.type

    def __ge__(self, other):
        return self.type >= other.type

    def set_color(self, color: str | CardColor) -> None:
        """
        Sets the card's color.
        :param color: the card's color. Can be 'wild', 'red', 'yellow', 'green', or 'blue'
        """
        if isinstance(color, CardColor):
            self.color = color
        else:
            assert (isinstance(color, str))  # ensure color is a string
            if self.type.isWild:
                self.color.name = color
            else:
                try:
                    self.color = Card.COLORS[color]
                except KeyError:
                    raise ValueError(f"'{color}' is not a valid card color. Valid card colors include 'wild', 'red', "
                                     f"'yellow', 'green', and 'blue'")

    def set_type(self, cardType: str | CardType) -> None:
        """
        Sets the card's type
        :param cardType: The type of card. Use 0-9 for a number card. Use 'skip', 'reverse', 'draw 2', 'wild draw 4',
        or 'wild' for the respective action cards
        """
        if isinstance(cardType, CardType):
            self.type = cardType
        else:
            cardType = str(cardType)
            if cardType.isdigit():
                self.type = CardType(cardType)
            else:
                try:
                    self.type = Card.ACTION_CARDS[cardType]
                except KeyError:
                    raise ValueError(f"'{cardType}' is not a valid card type. Valid card types include digits 0-9, "
                                     f"'reverse', 'skip', 'draw 2', 'wild draw 4', and 'wild'.")