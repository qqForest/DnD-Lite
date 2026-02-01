from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.player import Player
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse
from app.websocket.manager import manager

router = APIRouter()


def get_player_by_token(token: str, db: DBSession) -> Player:
    """Helper to get player from token."""
    player = db.query(Player).filter(Player.token == token).first()
    if not player:
        raise HTTPException(status_code=401, detail="Invalid token")
    return player


@router.get("", response_model=List[CharacterResponse])
def list_characters(token: str, db: DBSession = Depends(get_db)):
    """Get all characters in the session."""
    player = get_player_by_token(token, db)

    characters = (
        db.query(Character)
        .join(Player)
        .filter(Player.session_id == player.session_id)
        .all()
    )
    return characters


@router.post("", response_model=CharacterResponse)
async def create_character(
    data: CharacterCreate,
    token: str,
    db: DBSession = Depends(get_db)
):
    """Create a new character for the player."""
    player = get_player_by_token(token, db)

    character = Character(
        player_id=player.id,
        name=data.name,
        class_name=data.class_name,
        level=data.level,
        strength=data.strength,
        dexterity=data.dexterity,
        constitution=data.constitution,
        intelligence=data.intelligence,
        wisdom=data.wisdom,
        charisma=data.charisma,
        max_hp=data.max_hp,
        current_hp=data.current_hp if data.current_hp is not None else data.max_hp,
    )
    db.add(character)
    db.commit()
    db.refresh(character)

    # Broadcast character creation
    await manager.broadcast_event("character_created", {
        "character": CharacterResponse.model_validate(character).model_dump()
    })

    return character


@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(character_id: int, token: str, db: DBSession = Depends(get_db)):
    """Get a specific character."""
    player = get_player_by_token(token, db)

    character = (
        db.query(Character)
        .join(Player)
        .filter(
            Character.id == character_id,
            Player.session_id == player.session_id
        )
        .first()
    )

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return character


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    data: CharacterUpdate,
    token: str,
    db: DBSession = Depends(get_db)
):
    """Update a character. Only owner or GM can update."""
    player = get_player_by_token(token, db)

    character = (
        db.query(Character)
        .join(Player)
        .filter(
            Character.id == character_id,
            Player.session_id == player.session_id
        )
        .first()
    )

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check ownership or GM status
    if character.player_id != player.id and not player.is_gm:
        raise HTTPException(status_code=403, detail="Not authorized to update this character")

    # Track HP changes for broadcast
    old_hp = character.current_hp

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)

    db.commit()
    db.refresh(character)

    # Broadcast character update
    await manager.broadcast_event("character_updated", {
        "character": CharacterResponse.model_validate(character).model_dump()
    })

    # Broadcast HP change if applicable
    if "current_hp" in update_data and old_hp != character.current_hp:
        diff = character.current_hp - old_hp
        await manager.broadcast_event("hp_changed", {
            "character_id": character.id,
            "hp": character.current_hp,
            "damage" if diff < 0 else "heal": abs(diff)
        })

    return character


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    token: str,
    db: DBSession = Depends(get_db)
):
    """Delete a character. Only owner or GM can delete."""
    player = get_player_by_token(token, db)

    character = (
        db.query(Character)
        .join(Player)
        .filter(
            Character.id == character_id,
            Player.session_id == player.session_id
        )
        .first()
    )

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check ownership or GM status
    if character.player_id != player.id and not player.is_gm:
        raise HTTPException(status_code=403, detail="Not authorized to delete this character")

    db.delete(character)
    db.commit()

    # Broadcast character deletion
    await manager.broadcast_event("character_deleted", {
        "character_id": character_id
    })

    return {"message": "Character deleted"}
