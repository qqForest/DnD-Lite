"""Сериализатор для Player."""

from typing import List, Dict, Any

from app.models.player import Player
from app.services.persistence.types import ExportContext, ImportContext


class PlayerSerializer:
    """Сериализатор игроков."""

    @classmethod
    def entity_name(cls) -> str:
        return "players"

    @classmethod
    def version(cls) -> int:
        return 1

    @classmethod
    def dependencies(cls) -> List[str]:
        return []  # Players зависят только от Session, которая создаётся отдельно

    @classmethod
    def export(cls, context: ExportContext) -> List[Dict[str, Any]]:
        players = (
            context.db.query(Player)
            .filter(Player.session_id == context.session_id)
            .all()
        )

        return [
            {
                "id": p.id,
                "name": p.name,
                "is_gm": p.is_gm,
            }
            for p in players
        ]

    @classmethod
    def import_(cls, data: List[Dict[str, Any]], context: ImportContext) -> int:
        count = 0

        for player_data in data:
            old_id = player_data["id"]

            # Пропускаем GM - он создаётся вместе с сессией
            if player_data.get("is_gm", False):
                # Находим GM созданного с сессией и записываем маппинг
                gm = (
                    context.db.query(Player)
                    .filter(
                        Player.session_id == context.session_id,
                        Player.is_gm == True
                    )
                    .first()
                )
                if gm:
                    context.id_mapping.set("players", old_id, gm.id)
                continue

            import uuid
            player = Player(
                session_id=context.session_id,
                name=player_data["name"],
                token=str(uuid.uuid4()),
                is_gm=False,
            )
            context.db.add(player)
            context.db.flush()

            context.id_mapping.set("players", old_id, player.id)
            count += 1

        return count

    @classmethod
    def validate(cls, data: List[Dict[str, Any]], context: ImportContext) -> None:
        names_seen: set = set()

        for i, player_data in enumerate(data):
            if "name" not in player_data:
                context.add_error(f"players[{i}]: отсутствует поле 'name'")
                continue

            if "id" not in player_data:
                context.add_error(f"players[{i}]: отсутствует поле 'id'")

            name = player_data["name"]
            if name in names_seen:
                context.add_error(f"players[{i}]: дублирующееся имя '{name}'")
            names_seen.add(name)
