"""Сериализатор для Item."""

from typing import List, Dict, Any

from app.models.item import Item
from app.models.character import Character
from app.models.player import Player
from app.services.persistence.types import ExportContext, ImportContext


class ItemSerializer:
    """Сериализатор предметов."""

    @classmethod
    def entity_name(cls) -> str:
        return "items"

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

        items = (
            context.db.query(Item)
            .filter(Item.character_id.in_(character_ids))
            .all()
        )

        return [
            {
                "id": item.id,
                "character_id": item.character_id,
                "name": item.name,
                "description": item.description,
                "effects": item.effects,
                "is_equipped": item.is_equipped,
            }
            for item in items
        ]

    @classmethod
    def import_(cls, data: List[Dict[str, Any]], context: ImportContext) -> int:
        count = 0

        for item_data in data:
            old_id = item_data["id"]
            old_char_id = item_data["character_id"]

            new_char_id = context.id_mapping.get("characters", old_char_id)

            item = Item(
                character_id=new_char_id,
                name=item_data["name"],
                description=item_data.get("description"),
                effects=item_data.get("effects"),
                is_equipped=item_data.get("is_equipped", False),
            )
            context.db.add(item)
            context.db.flush()

            context.id_mapping.set("items", old_id, item.id)
            count += 1

        return count

    @classmethod
    def validate(cls, data: List[Dict[str, Any]], context: ImportContext) -> None:
        for i, item_data in enumerate(data):
            if "name" not in item_data:
                context.add_error(f"items[{i}]: отсутствует поле 'name'")

            if "id" not in item_data:
                context.add_error(f"items[{i}]: отсутствует поле 'id'")

            if "character_id" not in item_data:
                context.add_error(f"items[{i}]: отсутствует поле 'character_id'")

            effects = item_data.get("effects")
            if effects is not None and not isinstance(effects, dict):
                context.add_error(
                    f"items[{i}]: effects должен быть объектом или null"
                )
