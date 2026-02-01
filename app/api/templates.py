"""API endpoints для шаблонов классов."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.player import Player
from app.models.character import Character
from app.models.item import Item
from app.models.spell import Spell
from app.schemas.templates import (
    ClassTemplateResponse,
    ClassTemplateListItem,
    CreateFromTemplateRequest,
    StartingItemSchema,
    StartingSpellSchema,
)
from app.schemas.character import CharacterResponse
from app.core.class_templates import (
    list_templates,
    get_template,
    ClassTemplate,
)
from app.websocket.manager import manager

router = APIRouter()


def get_player_by_token(token: str, db: DBSession) -> Player:
    """Получить игрока по токену."""
    player = db.query(Player).filter(Player.token == token).first()
    if not player:
        raise HTTPException(status_code=401, detail="Invalid token")
    return player


def template_to_response(template: ClassTemplate) -> ClassTemplateResponse:
    """Преобразовать шаблон в Pydantic модель."""
    return ClassTemplateResponse(
        id=template.id,
        name=template.name,
        name_ru=template.name_ru,
        description=template.description,
        description_ru=template.description_ru,
        hit_die=template.hit_die.value,
        primary_abilities=template.primary_abilities,
        strength=template.strength,
        dexterity=template.dexterity,
        constitution=template.constitution,
        intelligence=template.intelligence,
        wisdom=template.wisdom,
        charisma=template.charisma,
        recommended_hp=template.calculate_hp(1),
        starting_items=[
            StartingItemSchema(
                name=item.name,
                description=item.description,
                effects=item.effects,
                is_equipped=item.is_equipped,
            )
            for item in template.starting_items
        ],
        starting_spells=[
            StartingSpellSchema(
                name=spell.name,
                level=spell.level,
                description=spell.description,
                damage_dice=spell.damage_dice,
            )
            for spell in template.starting_spells
        ],
    )


def template_to_list_item(template: ClassTemplate) -> ClassTemplateListItem:
    """Преобразовать шаблон в краткую модель для списка."""
    return ClassTemplateListItem(
        id=template.id,
        name=template.name,
        name_ru=template.name_ru,
        description_ru=template.description_ru,
        hit_die=template.hit_die.value,
        primary_abilities=template.primary_abilities,
    )


@router.get("", response_model=List[ClassTemplateListItem])
def list_class_templates():
    """Получить список всех доступных шаблонов классов."""
    templates = list_templates()
    return [template_to_list_item(t) for t in templates]


@router.get("/{template_id}", response_model=ClassTemplateResponse)
def get_class_template(template_id: str):
    """Получить детальную информацию о шаблоне класса."""
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template_to_response(template)


@router.post("/create", response_model=CharacterResponse)
async def create_character_from_template(
    request: CreateFromTemplateRequest,
    token: str,
    db: DBSession = Depends(get_db),
):
    """Создать персонажа на основе шаблона класса.

    Автоматически устанавливает характеристики, HP,
    и опционально добавляет стартовые предметы и заклинания.
    """
    player = get_player_by_token(token, db)

    template = get_template(request.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Создаём персонажа с характеристиками из шаблона
    hp = template.calculate_hp(request.level)

    character = Character(
        player_id=player.id,
        name=request.name,
        class_name=template.name,
        level=request.level,
        strength=template.strength,
        dexterity=template.dexterity,
        constitution=template.constitution,
        intelligence=template.intelligence,
        wisdom=template.wisdom,
        charisma=template.charisma,
        max_hp=hp,
        current_hp=hp,
    )
    db.add(character)
    db.flush()

    # Добавляем стартовые предметы
    if request.include_items:
        for item_template in template.starting_items:
            item = Item(
                character_id=character.id,
                name=item_template.name,
                description=item_template.description,
                effects=item_template.effects,
                is_equipped=item_template.is_equipped,
            )
            db.add(item)

    # Добавляем стартовые заклинания
    if request.include_spells:
        for spell_template in template.starting_spells:
            spell = Spell(
                character_id=character.id,
                name=spell_template.name,
                level=spell_template.level,
                description=spell_template.description,
                damage_dice=spell_template.damage_dice,
            )
            db.add(spell)

    db.commit()
    db.refresh(character)

    # Broadcast создание персонажа
    await manager.broadcast_event("character_created", {
        "character": CharacterResponse.model_validate(character).model_dump(),
        "from_template": template.id,
    })

    return character
