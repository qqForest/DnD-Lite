"""Сериализатор для Spell."""

from typing import List, Dict, Any

from app.models.spell import Spell
from app.models.character import Character
from app.models.player import Player
from app.services.persistence.types import ExportContext, ImportContext


class SpellSerializer:
    """Сериализатор заклинаний."""

    @classmethod
    def entity_name(cls) -> str:
        return "spells"

    @classmethod
    def version(cls) -> int:
        return 1

    @classmethod
    def dependencies(cls) -> List[str]:
        return ["characters"]

    @classmethod
    def export(cls, context: ExportContext) -> List[Dict[str, Any]]:
        # Получаем character_ids через players сессии
        player_ids = (
            context.db.query(Player.id)
            .filter(Player.session_id == context.session_id)
            .all()
        )
        player_ids = [p[0] for p in player_ids]

        character_ids = (
            context.db.query(Character.id)
            .filter(Character.player_id.in_(player_ids))
            .all()
        )
        character_ids = [c[0] for c in character_ids]

        spells = (
            context.db.query(Spell)
            .filter(Spell.character_id.in_(character_ids))
            .all()
        )

        return [
            {
                "id": spell.id,
                "character_id": spell.character_id,
                "name": spell.name,
                "level": spell.level,
                "description": spell.description,
                "damage_dice": spell.damage_dice,
            }
            for spell in spells
        ]

    @classmethod
    def import_(cls, data: List[Dict[str, Any]], context: ImportContext) -> int:
        count = 0

        for spell_data in data:
            old_id = spell_data["id"]
            old_char_id = spell_data["character_id"]

            new_char_id = context.id_mapping.get("characters", old_char_id)

            spell = Spell(
                character_id=new_char_id,
                name=spell_data["name"],
                level=spell_data.get("level", 0),
                description=spell_data.get("description"),
                damage_dice=spell_data.get("damage_dice"),
            )
            context.db.add(spell)
            context.db.flush()

            context.id_mapping.set("spells", old_id, spell.id)
            count += 1

        return count

    @classmethod
    def validate(cls, data: List[Dict[str, Any]], context: ImportContext) -> None:
        for i, spell_data in enumerate(data):
            if "name" not in spell_data:
                context.add_error(f"spells[{i}]: отсутствует поле 'name'")

            if "id" not in spell_data:
                context.add_error(f"spells[{i}]: отсутствует поле 'id'")

            if "character_id" not in spell_data:
                context.add_error(f"spells[{i}]: отсутствует поле 'character_id'")

            level = spell_data.get("level", 0)
            if not isinstance(level, int) or level < 0 or level > 9:
                context.add_warning(
                    f"spells[{i}]: level={level} вне диапазона 0-9"
                )
