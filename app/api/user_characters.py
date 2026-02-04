from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.user import User
from app.models.user_character import UserCharacter
from app.schemas.user_character import UserCharacterCreate, UserCharacterUpdate, UserCharacterResponse
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[UserCharacterResponse])
def list_user_characters(
    is_npc: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    query = db.query(UserCharacter).filter(UserCharacter.user_id == current_user.id)
    if is_npc is not None:
        query = query.filter(UserCharacter.is_npc == is_npc)
    return query.order_by(UserCharacter.created_at.desc()).all()


@router.post("/", response_model=UserCharacterResponse, status_code=201)
def create_user_character(
    data: UserCharacterCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    character = UserCharacter(
        user_id=current_user.id,
        **data.model_dump()
    )
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.get("/{character_id}", response_model=UserCharacterResponse)
def get_user_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    character = db.query(UserCharacter).filter(
        UserCharacter.id == character_id,
        UserCharacter.user_id == current_user.id
    ).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.patch("/{character_id}", response_model=UserCharacterResponse)
def update_user_character(
    character_id: int,
    data: UserCharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    character = db.query(UserCharacter).filter(
        UserCharacter.id == character_id,
        UserCharacter.user_id == current_user.id
    ).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)

    db.commit()
    db.refresh(character)
    return character


@router.delete("/{character_id}", status_code=204)
def delete_user_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    character = db.query(UserCharacter).filter(
        UserCharacter.id == character_id,
        UserCharacter.user_id == current_user.id
    ).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    db.delete(character)
    db.commit()
