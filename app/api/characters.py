from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.player import Player
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse
from app.websocket.manager import manager
from app.core.auth import get_current_player

router = APIRouter()




@router.get("", response_model=List[CharacterResponse])
def list_characters(
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Get all characters in the session."""

    characters = (
        db.query(Character)
        .join(Player)
        .filter(Player.session_id == current_player.session_id)
        .all()
    )
    return characters


@router.post("", response_model=CharacterResponse)
async def create_character(
    data: CharacterCreate,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Create a new character for the player."""

    character = Character(
        player_id=current_player.id,
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
        armor_class=data.armor_class,
        appearance=data.appearance,
        avatar_url=data.avatar_url,
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
def get_character(
    character_id: int,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Get a specific character."""

    character = (
        db.query(Character)
        .join(Player)
        .filter(
            Character.id == character_id,
            Player.session_id == current_player.session_id
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
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Update a character. Only owner or GM can update."""

    character = (
        db.query(Character)
        .join(Player)
        .filter(
            Character.id == character_id,
            Player.session_id == current_player.session_id
        )
        .first()
    )

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check ownership or GM status
    if character.player_id != current_player.id and not current_player.is_gm:
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


@router.post("/{character_id}/generate-avatar", response_model=CharacterResponse)
async def generate_character_avatar(
    character_id: int,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Generate avatar for a session character. Owner or GM only."""
    character = (
        db.query(Character)
        .join(Player)
        .filter(
            Character.id == character_id,
            Player.session_id == current_player.session_id
        )
        .first()
    )
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if character.player_id != current_player.id and not current_player.is_gm:
        raise HTTPException(status_code=403, detail="Not authorized")

    if not character.appearance:
        raise HTTPException(status_code=400, detail="Character has no appearance description")

    from app.services.avatar import generate_avatar
    try:
        avatar_url = await generate_avatar(character.appearance)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Avatar generation failed: {e}")

    character.avatar_url = avatar_url
    db.commit()
    db.refresh(character)

    await manager.broadcast_event("character_updated", {
        "character": CharacterResponse.model_validate(character).model_dump()
    })

    return character


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Delete a character. Only owner or GM can delete."""

    character = (
        db.query(Character)
        .join(Player)
        .filter(
            Character.id == character_id,
            Player.session_id == current_player.session_id
        )
        .first()
    )

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check ownership or GM status
    if character.player_id != current_player.id and not current_player.is_gm:
        raise HTTPException(status_code=403, detail="Not authorized to delete this character")

    db.delete(character)
    db.commit()

    # Broadcast character deletion
    await manager.broadcast_event("character_deleted", {
        "character_id": character_id
    })

    return {"message": "Character deleted"}
