from app.core.abilities import calculate_modifier, Ability
from app.models.character import Character


class ModifierService:
    @staticmethod
    def get_ability_modifier(character: Character, ability: Ability) -> int:
        """Get the modifier for a specific ability."""
        score = getattr(character, ability.value)
        return calculate_modifier(score)

    @staticmethod
    def get_all_modifiers(character: Character) -> dict:
        """Get all ability modifiers for a character."""
        return {
            "strength": calculate_modifier(character.strength),
            "dexterity": calculate_modifier(character.dexterity),
            "constitution": calculate_modifier(character.constitution),
            "intelligence": calculate_modifier(character.intelligence),
            "wisdom": calculate_modifier(character.wisdom),
            "charisma": calculate_modifier(character.charisma),
        }

    @staticmethod
    def get_proficiency_bonus(level: int) -> int:
        """Calculate proficiency bonus based on level (D&D 5e)."""
        return (level - 1) // 4 + 2

    @staticmethod
    def calculate_initiative_modifier(character: Character) -> int:
        """Initiative modifier is based on DEX."""
        return calculate_modifier(character.dexterity)
