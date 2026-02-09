import pytest
from app.core.class_templates import (
    get_template, list_templates, ClassTemplate, DiceType,
    FIGHTER, WIZARD, BARBARIAN,
)


class TestGetTemplate:
    def test_existing(self):
        t = get_template("fighter")
        assert isinstance(t, ClassTemplate)
        assert t.id == "fighter"

    def test_nonexistent(self):
        assert get_template("nonexistent") is None

    def test_case_insensitive(self):
        assert get_template("FIGHTER") is not None
        assert get_template("Fighter") is not None
        assert get_template("fIgHtEr") is not None


class TestListTemplates:
    def test_returns_12(self):
        templates = list_templates()
        assert len(templates) == 12

    def test_all_class_template_instances(self):
        for t in list_templates():
            assert isinstance(t, ClassTemplate)

    def test_unique_ids(self):
        ids = [t.id for t in list_templates()]
        assert len(ids) == len(set(ids))


class TestCalculateHP:
    def test_wizard_level1(self):
        # d6, con=14 → mod=2, hp = 6 + 2 = 8
        hp = WIZARD.calculate_hp(level=1)
        assert hp == 8

    def test_fighter_level1(self):
        # d10, con=14 → mod=2, hp = 10 + 2 = 12
        hp = FIGHTER.calculate_hp(level=1)
        assert hp == 12

    def test_barbarian_level1(self):
        # d12, con=16 → mod=3, hp = 12 + 3 = 15
        hp = BARBARIAN.calculate_hp(level=1)
        assert hp == 15

    def test_fighter_level5(self):
        # d10, con=14 → mod=2
        # level 5: 10 + 2 + 4*(6+2) = 12 + 32 = 44
        hp = FIGHTER.calculate_hp(level=5)
        assert hp == 44

    def test_wizard_level5(self):
        # d6, con=14 → mod=2
        # level 5: 6 + 2 + 4*(4+2) = 8 + 24 = 32
        hp = WIZARD.calculate_hp(level=5)
        assert hp == 32


class TestArmorClass:
    def test_all_templates_have_ac(self):
        for t in list_templates():
            assert hasattr(t, 'armor_class')
            assert isinstance(t.armor_class, int)
            assert 10 <= t.armor_class <= 20, f"{t.id} AC={t.armor_class} вне диапазона"

    def test_expected_ac_values(self):
        expected = {
            "fighter": 16,
            "paladin": 16,
            "cleric": 16,
            "ranger": 16,
            "monk": 16,
            "barbarian": 15,
            "rogue": 14,
            "bard": 13,
            "warlock": 13,
            "wizard": 12,
            "druid": 12,
            "sorcerer": 12,
        }
        for template_id, ac in expected.items():
            t = get_template(template_id)
            assert t.armor_class == ac, f"{template_id}: expected AC={ac}, got {t.armor_class}"


class TestStartingEquipment:
    def test_caster_has_spells(self):
        wizard = get_template("wizard")
        assert len(wizard.starting_spells) > 0

    def test_fighter_has_no_spells(self):
        fighter = get_template("fighter")
        assert len(fighter.starting_spells) == 0

    def test_fighter_has_items(self):
        fighter = get_template("fighter")
        assert len(fighter.starting_items) >= 2

    def test_cleric_has_spells(self):
        cleric = get_template("cleric")
        assert len(cleric.starting_spells) > 0
