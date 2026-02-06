from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.user import User
from app.models.user_map import UserMap
from app.schemas.user_map import UserMapCreate, UserMapUpdate, UserMapResponse
from app.core.auth import get_current_user

router = APIRouter()


@router.get("", response_model=list[UserMapResponse])
def list_user_maps(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return db.query(UserMap).filter(
        UserMap.user_id == current_user.id
    ).order_by(UserMap.created_at.desc()).all()


@router.post("", response_model=UserMapResponse, status_code=201)
def create_user_map(
    data: UserMapCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    user_map = UserMap(
        user_id=current_user.id,
        **data.model_dump()
    )
    db.add(user_map)
    db.commit()
    db.refresh(user_map)
    return user_map


@router.get("/{map_id}", response_model=UserMapResponse)
def get_user_map(
    map_id: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    user_map = db.query(UserMap).filter(
        UserMap.id == map_id,
        UserMap.user_id == current_user.id
    ).first()
    if not user_map:
        raise HTTPException(status_code=404, detail="Map not found")
    return user_map


@router.patch("/{map_id}", response_model=UserMapResponse)
def update_user_map(
    map_id: str,
    data: UserMapUpdate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    user_map = db.query(UserMap).filter(
        UserMap.id == map_id,
        UserMap.user_id == current_user.id
    ).first()
    if not user_map:
        raise HTTPException(status_code=404, detail="Map not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_map, field, value)

    db.commit()
    db.refresh(user_map)
    return user_map


@router.delete("/{map_id}", status_code=204)
def delete_user_map(
    map_id: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    user_map = db.query(UserMap).filter(
        UserMap.id == map_id,
        UserMap.user_id == current_user.id
    ).first()
    if not user_map:
        raise HTTPException(status_code=404, detail="Map not found")

    db.delete(user_map)
    db.commit()
