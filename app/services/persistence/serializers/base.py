"""Базовый протокол для сериализаторов сущностей."""

from typing import Protocol, List, Dict, Any, runtime_checkable

from app.services.persistence.types import ExportContext, ImportContext


@runtime_checkable
class Saveable(Protocol):
    """Протокол для сериализаторов сущностей.

    Каждый сериализатор должен реализовать этот протокол
    для регистрации в реестре.
    """

    @classmethod
    def entity_name(cls) -> str:
        """Уникальное имя сущности (используется как ключ в JSON)."""
        ...

    @classmethod
    def version(cls) -> int:
        """Версия формата сериализации."""
        ...

    @classmethod
    def dependencies(cls) -> List[str]:
        """Список имён сущностей, от которых зависит эта.

        Зависимости импортируются первыми для корректного маппинга FK.
        """
        ...

    @classmethod
    def export(cls, context: ExportContext) -> List[Dict[str, Any]]:
        """Экспортировать все записи сущности из БД."""
        ...

    @classmethod
    def import_(cls, data: List[Dict[str, Any]], context: ImportContext) -> int:
        """Импортировать записи сущности в БД.

        Возвращает количество созданных записей.
        """
        ...

    @classmethod
    def validate(cls, data: List[Dict[str, Any]], context: ImportContext) -> None:
        """Валидация данных без импорта.

        Ошибки добавляются в context.errors.
        """
        ...
