import pytest
from unittest.mock import patch

from app.services.dice import DiceService


class TestParseDice:
    @pytest.mark.parametrize("notation,expected", [
        ("2d6+3", (2, 6, 3)),
        ("d20", (1, 20, 0)),
        ("1d20", (1, 20, 0)),
        ("d8-1", (1, 8, -1)),
        ("3d10", (3, 10, 0)),
        ("1d100", (1, 100, 0)),
        ("4d4+2", (4, 4, 2)),
    ])
    def test_valid_notation(self, notation, expected):
        assert DiceService.parse_dice(notation) == expected

    def test_spaces_ignored(self):
        assert DiceService.parse_dice(" 2d6 + 3 ") == (2, 6, 3)

    @pytest.mark.parametrize("notation", [
        "d7",       # invalid die type
        "d3",       # invalid die type
        "0d20",     # zero count
        "101d6",    # too many dice
        "abc",      # garbage
        "",         # empty
        "d",        # incomplete
        "2d",       # no sides
    ])
    def test_invalid_notation(self, notation):
        with pytest.raises(ValueError):
            DiceService.parse_dice(notation)


class TestRoll:
    @patch("app.services.dice.random.randint")
    def test_roll_basic(self, mock_randint):
        mock_randint.side_effect = [3, 5]  # 2d6
        rolls, modifier, total = DiceService.roll("2d6+3")
        assert rolls == [3, 5]
        assert modifier == 3
        assert total == 11  # 3 + 5 + 3

    @patch("app.services.dice.random.randint")
    def test_roll_single(self, mock_randint):
        mock_randint.return_value = 15
        rolls, modifier, total = DiceService.roll("1d20")
        assert rolls == [15]
        assert modifier == 0
        assert total == 15

    @patch("app.services.dice.random.randint")
    def test_roll_negative_modifier(self, mock_randint):
        mock_randint.return_value = 6
        rolls, modifier, total = DiceService.roll("1d8-1")
        assert rolls == [6]
        assert modifier == -1
        assert total == 5


class TestRollWithType:
    @patch("app.services.dice.random.randint")
    def test_normal(self, mock_randint):
        mock_randint.return_value = 10
        rolls, modifier, total, all_rolls, chosen = DiceService.roll_with_type("1d20", "normal")
        assert rolls == [10]
        assert all_rolls is None
        assert chosen is None

    @patch("app.services.dice.random.randint")
    def test_advantage_picks_higher(self, mock_randint):
        mock_randint.side_effect = [8, 15]  # two d20 rolls
        rolls, modifier, total, all_rolls, chosen = DiceService.roll_with_type("1d20", "advantage")
        assert all_rolls == [[8], [15]]
        assert chosen == 1  # second is higher
        assert total == 15

    @patch("app.services.dice.random.randint")
    def test_advantage_picks_first_on_tie(self, mock_randint):
        mock_randint.side_effect = [12, 12]
        rolls, modifier, total, all_rolls, chosen = DiceService.roll_with_type("1d20", "advantage")
        assert chosen == 0  # >= picks first

    @patch("app.services.dice.random.randint")
    def test_disadvantage_picks_lower(self, mock_randint):
        mock_randint.side_effect = [18, 5]
        rolls, modifier, total, all_rolls, chosen = DiceService.roll_with_type("1d20", "disadvantage")
        assert all_rolls == [[18], [5]]
        assert chosen == 1  # second is lower
        assert total == 5

    @patch("app.services.dice.random.randint")
    def test_disadvantage_picks_first_on_tie(self, mock_randint):
        mock_randint.side_effect = [7, 7]
        rolls, modifier, total, all_rolls, chosen = DiceService.roll_with_type("1d20", "disadvantage")
        assert chosen == 0  # <= picks first


class TestRollInitiative:
    @patch("app.services.dice.random.randint")
    def test_returns_d20(self, mock_randint):
        mock_randint.return_value = 17
        assert DiceService.roll_initiative() == 17
        mock_randint.assert_called_with(1, 20)


class TestRollAbilityCheck:
    @patch("app.services.dice.random.randint")
    def test_with_modifier(self, mock_randint):
        mock_randint.return_value = 14
        roll, total = DiceService.roll_ability_check(modifier=3)
        assert roll == 14
        assert total == 17

    @patch("app.services.dice.random.randint")
    def test_no_modifier(self, mock_randint):
        mock_randint.return_value = 9
        roll, total = DiceService.roll_ability_check()
        assert roll == 9
        assert total == 9
