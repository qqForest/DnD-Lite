"""Импорт сессии из JSON."""

import uuid
from typing import Dict, Any, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import Session as DBSession

from app.models.session import Session
from app.models.player import Player
from app.services.persistence.types import ImportContext, IdMapping
from app.services.persistence.registry import registry
from app.services.persistence.migrations import (
    is_version_supported,
    migrate_data,
    CURRENT_FORMAT_VERSION,
)


@dataclass
class ImportResult:
    """Результат импорта сессии."""
    success: bool
    session_id: int | None
    session_code: str | None
    gm_token: str | None
    player_tokens: Dict[str, str]  # player_name -> token
    entity_counts: Dict[str, int]
    warnings: list[str]
    errors: list[str]


@dataclass
class ValidationResult:
    """Результат валидации данных импорта."""
    is_valid: bool
    format_version: str
    entity_counts: Dict[str, int]
    warnings: list[str]
    errors: list[str]


def validate_import_data(data: Dict[str, Any]) -> ValidationResult:
    """Валидация данных импорта без создания записей.

    Args:
        data: Данные для валидации

    Returns:
        Результат валидации
    """
    errors = []
    warnings = []

    # Проверяем версию формата
    format_version = data.get("format_version", "unknown")
    if not is_version_supported(format_version):
        errors.append(
            f"Неподдерживаемая версия формата: {format_version}. "
            f"Поддерживаются версии до {CURRENT_FORMAT_VERSION}"
        )
        return ValidationResult(
            is_valid=False,
            format_version=format_version,
            entity_counts={},
            warnings=warnings,
            errors=errors,
        )

    # Проверяем наличие обязательных полей
    if "entities" not in data:
        errors.append("Отсутствует секция 'entities'")
        return ValidationResult(
            is_valid=False,
            format_version=format_version,
            entity_counts={},
            warnings=warnings,
            errors=errors,
        )

    # Мигрируем данные если нужно
    if format_version != CURRENT_FORMAT_VERSION:
        try:
            data = migrate_data(data)
            warnings.append(
                f"Данные мигрированы с версии {format_version} до {CURRENT_FORMAT_VERSION}"
            )
        except ValueError as e:
            errors.append(f"Ошибка миграции: {e}")
            return ValidationResult(
                is_valid=False,
                format_version=format_version,
                entity_counts={},
                warnings=warnings,
                errors=errors,
            )

    entities = data.get("entities", {})

    # Создаём фиктивный контекст для валидации
    context = ImportContext(
        db=None,  # type: ignore
        session_id=0,
        validation_only=True,
    )

    # Валидируем каждую сущность
    registry.validate_all(entities, context)

    errors.extend(context.errors)
    warnings.extend(context.warnings)

    # Считаем количество записей
    entity_counts = {}
    for name, entity_info in entities.items():
        entity_counts[name] = len(entity_info.get("data", []))

    return ValidationResult(
        is_valid=len(errors) == 0,
        format_version=format_version,
        entity_counts=entity_counts,
        warnings=warnings,
        errors=errors,
    )


def import_session(
    db: DBSession,
    data: Dict[str, Any],
    new_session_code: str | None = None,
) -> ImportResult:
    """Импортировать сессию из JSON данных.

    Args:
        db: Сессия базы данных
        data: Данные экспорта
        new_session_code: Опциональный код для новой сессии

    Returns:
        Результат импорта
    """
    # Сначала валидируем
    validation = validate_import_data(data)
    if not validation.is_valid:
        return ImportResult(
            success=False,
            session_id=None,
            session_code=None,
            gm_token=None,
            player_tokens={},
            entity_counts={},
            warnings=validation.warnings,
            errors=validation.errors,
        )

    # Мигрируем данные если нужно
    format_version = data.get("format_version", "1.0")
    if format_version != CURRENT_FORMAT_VERSION:
        data = migrate_data(data)

    # Создаём новую сессию
    if new_session_code is None:
        import string
        import random
        chars = string.ascii_uppercase + string.digits
        new_session_code = "".join(random.choices(chars, k=6))

    gm_token = str(uuid.uuid4())

    session = Session(
        code=new_session_code,
        gm_token=gm_token,
        is_active=True,
    )
    db.add(session)
    db.flush()

    # Создаём GM игрока
    gm_player = Player(
        session_id=session.id,
        name="Game Master",
        token=gm_token,
        is_gm=True,
    )
    db.add(gm_player)
    db.flush()

    # Создаём контекст импорта
    context = ImportContext(
        db=db,
        session_id=session.id,
        id_mapping=IdMapping(),
    )

    # Находим старый GM ID и создаём маппинг
    entities = data.get("entities", {})
    players_data = entities.get("players", {}).get("data", [])
    for p in players_data:
        if p.get("is_gm", False):
            context.id_mapping.set("players", p["id"], gm_player.id)
            break

    # Импортируем все сущности
    entity_counts = registry.import_all(entities, context)

    db.commit()

    # Собираем токены игроков
    player_tokens = {}
    players = db.query(Player).filter(Player.session_id == session.id).all()
    for player in players:
        player_tokens[player.name] = player.token

    return ImportResult(
        success=True,
        session_id=session.id,
        session_code=session.code,
        gm_token=gm_token,
        player_tokens=player_tokens,
        entity_counts=entity_counts,
        warnings=context.warnings,
        errors=[],
    )
