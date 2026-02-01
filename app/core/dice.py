from enum import Enum


class DiceType(int, Enum):
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20
    D100 = 100


DICE_TYPES = {
    "d4": DiceType.D4,
    "d6": DiceType.D6,
    "d8": DiceType.D8,
    "d10": DiceType.D10,
    "d12": DiceType.D12,
    "d20": DiceType.D20,
    "d100": DiceType.D100,
}
