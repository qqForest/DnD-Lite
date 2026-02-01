"""Экспорт сессии в JSON."""

from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session as DBSession

from app.models.session import Session
from app.services.persistence.types import ExportContext
from app.services.persistence.registry import registry
from app.services.persistence.migrations import CURRENT_FORMAT_VERSION


def export_session(
    db: DBSession,
    session_id: int,
    include_combat: bool = True,
) -> Dict[str, Any]:
    """Экспортировать сессию в словарь для сериализации в JSON.

    Args:
        db: Сессия базы данных
        session_id: ID сессии для экспорта
        include_combat: Включать ли данные о боях

    Returns:
        Словарь с полными данными сессии
    """
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise ValueError(f"Session {session_id} not found")

    context = ExportContext(
        db=db,
        session_id=session_id,
        include_combat=include_combat,
    )

    # Экспортируем все сущности через registry
    entities = registry.export_all(context)

    return {
        "format_version": CURRENT_FORMAT_VERSION,
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "session_info": {
            "code": session.code,
            "created_at": session.created_at.isoformat() + "Z" if session.created_at else None,
        },
        "entities": entities,
    }
