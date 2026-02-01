from typing import List, Optional
from sqlalchemy.orm import Session as DBSession

from app.models.combat import Combat, CombatParticipant
from app.models.character import Character
from app.services.dice import DiceService
from app.services.modifiers import ModifierService


class CombatService:
    @staticmethod
    def create_combat(db: DBSession, session_id: int) -> Combat:
        """Create a new combat for the session."""
        # Deactivate any existing active combat
        db.query(Combat).filter(
            Combat.session_id == session_id,
            Combat.is_active == True
        ).update({"is_active": False})

        combat = Combat(session_id=session_id, is_active=True, round_number=1)
        db.add(combat)
        db.commit()
        db.refresh(combat)
        return combat

    @staticmethod
    def add_participant(
        db: DBSession,
        combat: Combat,
        character: Character,
        initiative: Optional[int] = None
    ) -> CombatParticipant:
        """Add a character to combat with initiative roll."""
        if initiative is None:
            dex_mod = ModifierService.calculate_initiative_modifier(character)
            initiative = DiceService.roll_initiative() + dex_mod

        participant = CombatParticipant(
            combat_id=combat.id,
            character_id=character.id,
            initiative=initiative,
            current_hp=character.current_hp,
            is_active=True
        )
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def get_turn_order(combat: Combat) -> List[CombatParticipant]:
        """Get participants sorted by initiative (highest first)."""
        return sorted(
            [p for p in combat.participants if p.is_active],
            key=lambda p: p.initiative,
            reverse=True
        )

    @staticmethod
    def next_turn(db: DBSession, combat: Combat) -> Optional[CombatParticipant]:
        """Move to the next turn in combat."""
        turn_order = CombatService.get_turn_order(combat)
        if not turn_order:
            return None

        if combat.current_turn_id is None:
            # Start of combat
            next_participant = turn_order[0]
        else:
            # Find current position and move to next
            current_idx = None
            for i, p in enumerate(turn_order):
                if p.id == combat.current_turn_id:
                    current_idx = i
                    break

            if current_idx is None or current_idx >= len(turn_order) - 1:
                # End of round, start new round
                combat.round_number += 1
                next_participant = turn_order[0]
            else:
                next_participant = turn_order[current_idx + 1]

        combat.current_turn_id = next_participant.id
        db.commit()
        db.refresh(combat)
        return next_participant

    @staticmethod
    def apply_damage(
        db: DBSession,
        participant: CombatParticipant,
        damage: int
    ) -> CombatParticipant:
        """Apply damage to a combat participant."""
        participant.current_hp = max(0, participant.current_hp - damage)
        if participant.current_hp == 0:
            participant.is_active = False
        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def apply_healing(
        db: DBSession,
        participant: CombatParticipant,
        healing: int,
        max_hp: int
    ) -> CombatParticipant:
        """Apply healing to a combat participant."""
        participant.current_hp = min(max_hp, participant.current_hp + healing)
        if participant.current_hp > 0:
            participant.is_active = True
        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def end_combat(db: DBSession, combat: Combat) -> Combat:
        """End the combat."""
        combat.is_active = False
        db.commit()
        db.refresh(combat)
        return combat
