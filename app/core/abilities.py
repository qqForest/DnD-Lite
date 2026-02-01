from enum import Enum


class Ability(str, Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


ABILITY_NAMES = {
    Ability.STRENGTH: "STR",
    Ability.DEXTERITY: "DEX",
    Ability.CONSTITUTION: "CON",
    Ability.INTELLIGENCE: "INT",
    Ability.WISDOM: "WIS",
    Ability.CHARISMA: "CHA",
}


def calculate_modifier(score: int) -> int:
    """Calculate ability modifier from ability score (D&D 5e formula)."""
    return (score - 10) // 2
