import re
import random
from typing import Tuple, List


class DiceService:
    DICE_PATTERN = re.compile(r"^(\d+)?d(\d+)([+-]\d+)?$", re.IGNORECASE)

    @classmethod
    def parse_dice(cls, dice_str: str) -> Tuple[int, int, int]:
        """
        Parse dice notation like "2d6+3", "1d20", "d8-1".
        Returns (count, sides, modifier).
        """
        match = cls.DICE_PATTERN.match(dice_str.replace(" ", ""))
        if not match:
            raise ValueError(f"Invalid dice notation: {dice_str}")

        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        if sides not in (4, 6, 8, 10, 12, 20, 100):
            raise ValueError(f"Invalid dice type: d{sides}")

        if count < 1 or count > 100:
            raise ValueError(f"Invalid dice count: {count}")

        return count, sides, modifier

    @classmethod
    def roll(cls, dice_str: str) -> Tuple[List[int], int, int]:
        """
        Roll dice and return (individual_rolls, modifier, total).
        """
        count, sides, modifier = cls.parse_dice(dice_str)
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls) + modifier
        return rolls, modifier, total

    @classmethod
    def roll_initiative(cls) -> int:
        """Roll d20 for initiative."""
        return random.randint(1, 20)

    @classmethod
    def roll_ability_check(cls, modifier: int = 0) -> Tuple[int, int]:
        """Roll d20 for ability check. Returns (roll, total)."""
        roll = random.randint(1, 20)
        return roll, roll + modifier
