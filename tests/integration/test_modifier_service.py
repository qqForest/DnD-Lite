import pytest
from app.services.modifiers import ModifierService
from app.core.abilities import Ability


class TestGetAbilityModifier:
    def test_strength(self, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, strength=16)
        assert ModifierService.get_ability_modifier(char, Ability.STRENGTH) == 3

    def test_low_score(self, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, intelligence=8)
        assert ModifierService.get_ability_modifier(char, Ability.INTELLIGENCE) == -1


class TestGetAllModifiers:
    def test_returns_six_keys(self, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player)
        mods = ModifierService.get_all_modifiers(char)
        assert len(mods) == 6
        expected_keys = {"strength", "dexterity", "constitution",
                         "intelligence", "wisdom", "charisma"}
        assert set(mods.keys()) == expected_keys

    def test_values_correct(self, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        # str=16→3, dex=14→2, con=14→2, int=10→0, wis=12→1, cha=8→-1
        char = create_character_fixture(player)
        mods = ModifierService.get_all_modifiers(char)
        assert mods["strength"] == 3
        assert mods["dexterity"] == 2
        assert mods["charisma"] == -1


class TestGetProficiencyBonus:
    @pytest.mark.parametrize("level,expected", [
        (1, 2), (4, 2), (5, 3), (8, 3), (9, 4), (12, 4),
        (13, 5), (16, 5), (17, 6), (20, 6),
    ])
    def test_proficiency_levels(self, level, expected):
        assert ModifierService.get_proficiency_bonus(level) == expected


class TestCalculateInitiativeModifier:
    def test_based_on_dexterity(self, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, dexterity=14)
        assert ModifierService.calculate_initiative_modifier(char) == 2

    def test_negative_dex(self, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, dexterity=8)
        assert ModifierService.calculate_initiative_modifier(char) == -1
