"""Сериализатор для Combat и CombatParticipant."""

from typing import List, Dict, Any

from app.models.combat import Combat, CombatParticipant
from app.services.persistence.types import ExportContext, ImportContext


class CombatSerializer:
    """Сериализатор боёв."""

    @classmethod
    def entity_name(cls) -> str:
        return "combats"

    @classmethod
    def version(cls) -> int:
        return 1

    @classmethod
    def dependencies(cls) -> List[str]:
        return ["characters"]

    @classmethod
    def export(cls, context: ExportContext) -> List[Dict[str, Any]]:
        if not context.include_combat:
            return []

        combats = (
            context.db.query(Combat)
            .filter(Combat.session_id == context.session_id)
            .all()
        )

        result = []
        for combat in combats:
            participants_data = []
            current_turn_order = None

            for p in combat.participants:
                participant_data = {
                    "id": p.id,
                    "character_id": p.character_id,
                    "initiative": p.initiative,
                    "current_hp": p.current_hp,
                    "is_active": p.is_active,
                }
                participants_data.append(participant_data)

                if combat.current_turn_id == p.id:
                    current_turn_order = len(participants_data) - 1

            result.append({
                "id": combat.id,
                "is_active": combat.is_active,
                "round_number": combat.round_number,
                "current_turn_order": current_turn_order,
                "participants": participants_data,
            })

        return result

    @classmethod
    def import_(cls, data: List[Dict[str, Any]], context: ImportContext) -> int:
        count = 0

        for combat_data in data:
            old_id = combat_data["id"]

            combat = Combat(
                session_id=context.session_id,
                is_active=combat_data.get("is_active", False),
                round_number=combat_data.get("round_number", 1),
                current_turn_id=None,  # Установим после создания участников
            )
            context.db.add(combat)
            context.db.flush()

            context.id_mapping.set("combats", old_id, combat.id)

            # Импортируем участников
            participants = combat_data.get("participants", [])
            current_turn_order = combat_data.get("current_turn_order")
            current_turn_participant_id = None

            for i, p_data in enumerate(participants):
                old_char_id = p_data["character_id"]

                if not context.id_mapping.has("characters", old_char_id):
                    context.add_warning(
                        f"Combat participant references unknown character {old_char_id}"
                    )
                    continue

                new_char_id = context.id_mapping.get("characters", old_char_id)

                participant = CombatParticipant(
                    combat_id=combat.id,
                    character_id=new_char_id,
                    initiative=p_data.get("initiative", 0),
                    current_hp=p_data["current_hp"],
                    is_active=p_data.get("is_active", True),
                )
                context.db.add(participant)
                context.db.flush()

                if current_turn_order is not None and i == current_turn_order:
                    current_turn_participant_id = participant.id

            # Устанавливаем текущий ход
            if current_turn_participant_id:
                combat.current_turn_id = current_turn_participant_id
                context.db.flush()

            count += 1

        return count

    @classmethod
    def validate(cls, data: List[Dict[str, Any]], context: ImportContext) -> None:
        for i, combat_data in enumerate(data):
            if "id" not in combat_data:
                context.add_error(f"combats[{i}]: отсутствует поле 'id'")

            participants = combat_data.get("participants", [])
            for j, p_data in enumerate(participants):
                if "character_id" not in p_data:
                    context.add_error(
                        f"combats[{i}].participants[{j}]: отсутствует character_id"
                    )

                if "current_hp" not in p_data:
                    context.add_error(
                        f"combats[{i}].participants[{j}]: отсутствует current_hp"
                    )
