"""Импорт всех сериализаторов для автоматической регистрации в registry."""

from app.services.persistence.serializers.player import PlayerSerializer
from app.services.persistence.serializers.character import CharacterSerializer
from app.services.persistence.serializers.item import ItemSerializer
from app.services.persistence.serializers.spell import SpellSerializer
from app.services.persistence.serializers.combat import CombatSerializer

__all__ = [
    "PlayerSerializer",
    "CharacterSerializer",
    "ItemSerializer",
    "SpellSerializer",
    "CombatSerializer",
]


def register_all(registry):
    """Зарегистрировать все сериализаторы в реестре."""
    registry.register(PlayerSerializer)
    registry.register(CharacterSerializer)
    registry.register(ItemSerializer)
    registry.register(SpellSerializer)
    registry.register(CombatSerializer)
