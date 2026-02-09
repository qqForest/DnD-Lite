import pytest
from app.core.abilities import Ability, ABILITY_NAMES, calculate_modifier


class TestCalculateModifier:
    @pytest.mark.parametrize("score,expected", [
        (1, -5),
        (3, -4),
        (8, -1),
        (9, -1),
        (10, 0),
        (11, 0),
        (14, 2),
        (15, 2),
        (18, 4),
        (20, 5),
    ])
    def test_modifier_values(self, score, expected):
        assert calculate_modifier(score) == expected


class TestAbilityEnum:
    def test_all_six_abilities(self):
        assert len(Ability) == 6

    def test_ability_values(self):
        expected = {"strength", "dexterity", "constitution",
                    "intelligence", "wisdom", "charisma"}
        assert {a.value for a in Ability} == expected


class TestAbilityNames:
    def test_all_abilities_have_short_name(self):
        assert set(ABILITY_NAMES.keys()) == set(Ability)

    def test_short_names(self):
        assert ABILITY_NAMES[Ability.STRENGTH] == "STR"
        assert ABILITY_NAMES[Ability.DEXTERITY] == "DEX"
        assert ABILITY_NAMES[Ability.CONSTITUTION] == "CON"
        assert ABILITY_NAMES[Ability.INTELLIGENCE] == "INT"
        assert ABILITY_NAMES[Ability.WISDOM] == "WIS"
        assert ABILITY_NAMES[Ability.CHARISMA] == "CHA"
