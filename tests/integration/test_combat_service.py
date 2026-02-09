import pytest
from unittest.mock import patch

from app.services.combat import CombatService
from app.models.combat import Combat, CombatParticipant


class TestCreateCombat:
    def test_creates_active_combat(self, db, create_session_fixture):
        session, gm = create_session_fixture()
        combat = CombatService.create_combat(db, session.id)
        assert combat.is_active is True
        assert combat.round_number == 1
        assert combat.session_id == session.id

    def test_deactivates_old_combat(self, db, create_session_fixture):
        session, gm = create_session_fixture()
        old = CombatService.create_combat(db, session.id)
        new = CombatService.create_combat(db, session.id)
        db.refresh(old)
        assert old.is_active is False
        assert new.is_active is True


class TestAddParticipant:
    def test_manual_initiative(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, current_hp=20, max_hp=20)
        combat = CombatService.create_combat(db, session.id)

        p = CombatService.add_participant(db, combat, char, initiative=15)
        assert p.initiative == 15
        assert p.current_hp == 20
        assert p.is_active is True

    @patch("app.services.combat.DiceService.roll_initiative", return_value=12)
    def test_auto_initiative(self, mock_roll, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, dexterity=14)  # mod=2
        combat = CombatService.create_combat(db, session.id)

        p = CombatService.add_participant(db, combat, char)
        assert p.initiative == 14  # 12 + 2


class TestGetTurnOrder:
    def test_sorted_by_initiative_desc(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        p1 = create_player_fixture(session, name="P1")
        p2 = create_player_fixture(session, name="P2")
        c1 = create_character_fixture(p1, name="Slow", current_hp=10)
        c2 = create_character_fixture(p2, name="Fast", current_hp=10)
        combat = CombatService.create_combat(db, session.id)
        CombatService.add_participant(db, combat, c1, initiative=5)
        CombatService.add_participant(db, combat, c2, initiative=20)

        order = CombatService.get_turn_order(combat)
        assert len(order) == 2
        assert order[0].initiative == 20
        assert order[1].initiative == 5

    def test_excludes_inactive(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        p1 = create_player_fixture(session, name="P1")
        p2 = create_player_fixture(session, name="P2")
        c1 = create_character_fixture(p1, name="Active", current_hp=10)
        c2 = create_character_fixture(p2, name="Down", current_hp=10)
        combat = CombatService.create_combat(db, session.id)
        CombatService.add_participant(db, combat, c1, initiative=10)
        part2 = CombatService.add_participant(db, combat, c2, initiative=15)
        part2.is_active = False
        db.flush()

        order = CombatService.get_turn_order(combat)
        assert len(order) == 1


class TestNextTurn:
    def _setup_combat(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        p1 = create_player_fixture(session, name="P1")
        p2 = create_player_fixture(session, name="P2")
        p3 = create_player_fixture(session, name="P3")
        c1 = create_character_fixture(p1, name="A", current_hp=10)
        c2 = create_character_fixture(p2, name="B", current_hp=10)
        c3 = create_character_fixture(p3, name="C", current_hp=10)
        combat = CombatService.create_combat(db, session.id)
        pa = CombatService.add_participant(db, combat, c1, initiative=20)
        pb = CombatService.add_participant(db, combat, c2, initiative=15)
        pc = CombatService.add_participant(db, combat, c3, initiative=10)
        return combat, pa, pb, pc

    def test_first_turn(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        combat, pa, pb, pc = self._setup_combat(
            db, create_session_fixture, create_player_fixture, create_character_fixture)
        result = CombatService.next_turn(db, combat)
        assert result.id == pa.id  # highest initiative

    def test_second_turn(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        combat, pa, pb, pc = self._setup_combat(
            db, create_session_fixture, create_player_fixture, create_character_fixture)
        CombatService.next_turn(db, combat)  # → pa
        result = CombatService.next_turn(db, combat)  # → pb
        assert result.id == pb.id

    def test_new_round(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        combat, pa, pb, pc = self._setup_combat(
            db, create_session_fixture, create_player_fixture, create_character_fixture)
        CombatService.next_turn(db, combat)  # → pa
        CombatService.next_turn(db, combat)  # → pb
        CombatService.next_turn(db, combat)  # → pc
        result = CombatService.next_turn(db, combat)  # → new round, pa
        assert result.id == pa.id
        assert combat.round_number == 2

    def test_empty_combat(self, db, create_session_fixture):
        session, gm = create_session_fixture()
        combat = CombatService.create_combat(db, session.id)
        assert CombatService.next_turn(db, combat) is None


class TestApplyDamage:
    def test_reduces_hp(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, current_hp=20, max_hp=20)
        combat = CombatService.create_combat(db, session.id)
        p = CombatService.add_participant(db, combat, char, initiative=10)

        CombatService.apply_damage(db, p, 5)
        assert p.current_hp == 15
        assert p.is_active is True

    def test_drops_to_zero(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, current_hp=10, max_hp=10)
        combat = CombatService.create_combat(db, session.id)
        p = CombatService.add_participant(db, combat, char, initiative=10)

        CombatService.apply_damage(db, p, 15)
        assert p.current_hp == 0
        assert p.is_active is False

    def test_no_negative_hp(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, current_hp=5, max_hp=10)
        combat = CombatService.create_combat(db, session.id)
        p = CombatService.add_participant(db, combat, char, initiative=10)

        CombatService.apply_damage(db, p, 100)
        assert p.current_hp == 0


class TestApplyHealing:
    def test_heals_up(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, current_hp=5, max_hp=20)
        combat = CombatService.create_combat(db, session.id)
        p = CombatService.add_participant(db, combat, char, initiative=10)

        CombatService.apply_healing(db, p, 10, max_hp=20)
        assert p.current_hp == 15

    def test_caps_at_max_hp(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, current_hp=18, max_hp=20)
        combat = CombatService.create_combat(db, session.id)
        p = CombatService.add_participant(db, combat, char, initiative=10)

        CombatService.apply_healing(db, p, 50, max_hp=20)
        assert p.current_hp == 20

    def test_reactivates_at_zero(self, db, create_session_fixture, create_player_fixture, create_character_fixture):
        session, gm = create_session_fixture()
        player = create_player_fixture(session)
        char = create_character_fixture(player, current_hp=0, max_hp=20)
        combat = CombatService.create_combat(db, session.id)
        p = CombatService.add_participant(db, combat, char, initiative=10)
        p.is_active = False
        db.flush()

        CombatService.apply_healing(db, p, 5, max_hp=20)
        assert p.current_hp == 5
        assert p.is_active is True


class TestEndCombat:
    def test_deactivates(self, db, create_session_fixture):
        session, gm = create_session_fixture()
        combat = CombatService.create_combat(db, session.id)
        assert combat.is_active is True

        CombatService.end_combat(db, combat)
        assert combat.is_active is False
