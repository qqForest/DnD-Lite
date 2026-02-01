"""Сериализатор для Character."""

from typing import List, Dict, Any

from app.models.character import Character
from app.models.player import Player
from app.services.persistence.types import ExportContext, ImportContext


class CharacterSerializer:
    """Сериализатор персонажей."""

    @classmethod
    def entity_name(cls) -> str:
        return "characters"

    @classmethod
    def version(cls) -> int:
        return 1

    @classmethod
    def dependencies(cls) -> List[str]:
        return ["players"]

    @classmethod
    def export(cls, context: ExportContext) -> List[Dict[str, Any]]:
        # Получаем всех персонажей через players сессии
        player_ids = (
            context.db.query(Player.id)
            .filter(Player.session_id == context.session_id)
            .all()
        )
        player_ids = [p[0] for p in player_ids]

        characters = (
            context.db.query(Character)
            .filter(Character.player_id.in_(player_ids))
            .all()
        )

        return [
            {
                "id": c.id,
                "player_id": c.player_id,
                "name": c.name,
                "class_name": c.class_name,
                "level": c.level,
                "strength": c.strength,
                "dexterity": c.dexterity,
                "constitution": c.constitution,
                "intelligence": c.intelligence,
                "wisdom": c.wisdom,
                "charisma": c.charisma,
                "max_hp": c.max_hp,
                "current_hp": c.current_hp,
            }
            for c in characters
        ]

    @classmethod
    def import_(cls, data: List[Dict[str, Any]], context: ImportContext) -> int:
        count = 0

        for char_data in data:
            old_id = char_data["id"]
            old_player_id = char_data["player_id"]

            # Маппим player_id на новый
            new_player_id = context.id_mapping.get("players", old_player_id)

            character = Character(
                player_id=new_player_id,
                name=char_data["name"],
                class_name=char_data.get("class_name"),
                level=char_data.get("level", 1),
                strength=char_data.get("strength", 10),
                dexterity=char_data.get("dexterity", 10),
                constitution=char_data.get("constitution", 10),
                intelligence=char_data.get("intelligence", 10),
                wisdom=char_data.get("wisdom", 10),
                charisma=char_data.get("charisma", 10),
                max_hp=char_data.get("max_hp", 10),
                current_hp=char_data.get("current_hp", 10),
            )
            context.db.add(character)
            context.db.flush()

            context.id_mapping.set("characters", old_id, character.id)
            count += 1

        return count

    @classmethod
    def validate(cls, data: List[Dict[str, Any]], context: ImportContext) -> None:
        for i, char_data in enumerate(data):
            if "name" not in char_data:
                context.add_error(f"characters[{i}]: отсутствует поле 'name'")

            if "id" not in char_data:
                context.add_error(f"characters[{i}]: отсутствует поле 'id'")

            if "player_id" not in char_data:
                context.add_error(f"characters[{i}]: отсутствует поле 'player_id'")

            level = char_data.get("level", 1)
            if not isinstance(level, int) or level < 1 or level > 20:
                context.add_warning(
                    f"characters[{i}]: level={level} вне диапазона 1-20"
                )

            for stat in ["strength", "dexterity", "constitution",
                         "intelligence", "wisdom", "charisma"]:
                val = char_data.get(stat, 10)
                if not isinstance(val, int) or val < 1 or val > 30:
                    context.add_warning(
                        f"characters[{i}]: {stat}={val} вне диапазона 1-30"
                    )
