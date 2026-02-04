from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.player import Player
from app.models.session import Session
from app.models.user_character import UserCharacter
from app.schemas.user import UserRegister, UserLogin, UserResponse, AuthResponse, UserStatsResponse
from app.core.auth import hash_password, verify_password, create_access_token, create_refresh_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: DBSession = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует"
        )

    user = User(
        username=data.username,
        display_name=data.display_name,
        hashed_password=hash_password(data.password),
        role=data.role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token_data = {"sub": f"user:{user.id}"}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(data: UserLogin, db: DBSession = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный username или пароль"
        )

    token_data = {"sub": f"user:{user.id}"}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get dashboard stats for the current user."""
    total_characters = db.query(func.count(UserCharacter.id)).filter(
        UserCharacter.user_id == current_user.id,
        UserCharacter.is_npc == False
    ).scalar() or 0

    total_npcs = db.query(func.count(UserCharacter.id)).filter(
        UserCharacter.user_id == current_user.id,
        UserCharacter.is_npc == True
    ).scalar() or 0

    total_sessions = db.query(func.count(Player.id)).filter(
        Player.user_id == current_user.id
    ).scalar() or 0

    # Top characters by sessions_played
    top_characters_rows = db.query(UserCharacter).filter(
        UserCharacter.user_id == current_user.id,
        UserCharacter.is_npc == False,
        UserCharacter.sessions_played > 0
    ).order_by(UserCharacter.sessions_played.desc()).limit(5).all()

    from app.schemas.user_character import UserCharacterResponse
    top_characters = [UserCharacterResponse.model_validate(c) for c in top_characters_rows]

    return UserStatsResponse(
        total_characters=total_characters,
        total_npcs=total_npcs,
        total_sessions=total_sessions,
        top_characters=top_characters,
    )
