"""Типы данных для системы сохранения сессий."""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from sqlalchemy.orm import Session as DBSession


@dataclass
class IdMapping:
    """Маппинг старых ID на новые при импорте."""

    _mappings: Dict[str, Dict[int, int]] = field(default_factory=dict)

    def set(self, entity_type: str, old_id: int, new_id: int) -> None:
        """Записать маппинг ID для сущности."""
        if entity_type not in self._mappings:
            self._mappings[entity_type] = {}
        self._mappings[entity_type][old_id] = new_id

    def get(self, entity_type: str, old_id: int) -> int:
        """Получить новый ID по старому."""
        if entity_type not in self._mappings:
            raise KeyError(f"No mappings for entity type: {entity_type}")
        if old_id not in self._mappings[entity_type]:
            raise KeyError(f"No mapping for {entity_type} ID: {old_id}")
        return self._mappings[entity_type][old_id]

    def has(self, entity_type: str, old_id: int) -> bool:
        """Проверить наличие маппинга."""
        return (
            entity_type in self._mappings
            and old_id in self._mappings[entity_type]
        )


@dataclass
class ExportContext:
    """Контекст для экспорта сессии."""

    db: DBSession
    session_id: int
    include_combat: bool = True
    _exported_data: Dict[str, List[Dict[str, Any]]] = field(
        default_factory=dict, repr=False
    )

    def set_exported(self, entity_type: str, data: List[Dict[str, Any]]) -> None:
        """Сохранить экспортированные данные сущности."""
        self._exported_data[entity_type] = data

    def get_exported(self, entity_type: str) -> List[Dict[str, Any]]:
        """Получить экспортированные данные сущности."""
        return self._exported_data.get(entity_type, [])


@dataclass
class ImportContext:
    """Контекст для импорта сессии."""

    db: DBSession
    session_id: int
    id_mapping: IdMapping = field(default_factory=IdMapping)
    validation_only: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Добавить ошибку валидации."""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Добавить предупреждение."""
        self.warnings.append(message)

    def is_valid(self) -> bool:
        """Проверить отсутствие ошибок."""
        return len(self.errors) == 0
