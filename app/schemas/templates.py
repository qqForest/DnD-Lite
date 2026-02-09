"""Pydantic схемы для шаблонов классов."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class StartingItemSchema(BaseModel):
    """Стартовый предмет в шаблоне."""
    name: str
    description: Optional[str] = None
    effects: Optional[Dict[str, Any]] = None
    is_equipped: bool = False


class StartingSpellSchema(BaseModel):
    """Стартовое заклинание в шаблоне."""
    name: str
    level: int = 0
    description: Optional[str] = None
    damage_dice: Optional[str] = None


class ClassTemplateResponse(BaseModel):
    """Полная информация о шаблоне класса."""
    id: str
    name: str
    name_ru: str
    description: str
    description_ru: str
    hit_die: str
    primary_abilities: List[str]
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    recommended_hp: int = Field(description="Рекомендуемое HP для 1 уровня")
    recommended_ac: int = Field(description="Рекомендуемый AC для 1 уровня")
    starting_items: List[StartingItemSchema]
    starting_spells: List[StartingSpellSchema]


class ClassTemplateListItem(BaseModel):
    """Краткая информация о шаблоне для списка."""
    id: str
    name: str
    name_ru: str
    description_ru: str
    hit_die: str
    primary_abilities: List[str]


class CreateFromTemplateRequest(BaseModel):
    """Запрос на создание персонажа из шаблона."""
    template_id: str = Field(..., description="ID шаблона класса")
    name: str = Field(..., min_length=1, max_length=100, description="Имя персонажа")
    level: int = Field(default=1, ge=1, le=20, description="Уровень персонажа")
    include_items: bool = Field(default=True, description="Добавить стартовые предметы")
    include_spells: bool = Field(default=True, description="Добавить стартовые заклинания")
