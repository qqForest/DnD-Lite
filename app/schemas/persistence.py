"""Pydantic схемы для системы сохранения сессий."""

from datetime import datetime
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field


class SessionInfo(BaseModel):
    """Информация о сессии в экспорте."""
    code: str
    created_at: Optional[str] = None


class EntityData(BaseModel):
    """Данные сущности в экспорте."""
    version: int
    data: List[Dict[str, Any]]


class SessionExport(BaseModel):
    """Полный формат экспорта сессии."""
    format_version: str
    exported_at: str
    session_info: SessionInfo
    entities: Dict[str, EntityData]


class ExportRequest(BaseModel):
    """Запрос на экспорт сессии."""
    include_combat: bool = Field(default=True, description="Включить данные о боях")


class ExportResponse(BaseModel):
    """Ответ с экспортированными данными."""
    success: bool
    data: Optional[SessionExport] = None
    error: Optional[str] = None


class ImportRequest(BaseModel):
    """Запрос на импорт сессии."""
    data: Dict[str, Any] = Field(..., description="Данные экспорта")
    new_session_code: Optional[str] = Field(
        None,
        description="Опциональный код для новой сессии",
        min_length=4,
        max_length=10,
    )


class ImportResponse(BaseModel):
    """Ответ на запрос импорта."""
    success: bool
    session_id: Optional[int] = None
    session_code: Optional[str] = None
    gm_token: Optional[str] = None
    player_tokens: Dict[str, str] = Field(
        default_factory=dict,
        description="Маппинг имя игрока -> токен"
    )
    entity_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Количество импортированных сущностей по типам"
    )
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ValidationRequest(BaseModel):
    """Запрос на валидацию данных импорта."""
    data: Dict[str, Any] = Field(..., description="Данные для валидации")


class ValidationResponse(BaseModel):
    """Ответ на запрос валидации."""
    is_valid: bool
    format_version: str
    entity_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Количество записей по типам сущностей"
    )
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
