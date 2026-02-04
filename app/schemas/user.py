from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class UserRole(str, Enum):
    player = "player"
    gm = "gm"
    both = "both"


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.player


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str


class UserStatsResponse(BaseModel):
    total_characters: int
    total_npcs: int
    total_sessions: int
    top_characters: List["UserCharacterResponse"] = []

    class Config:
        from_attributes = True


# Deferred import to avoid circular dependency
from app.schemas.user_character import UserCharacterResponse
UserStatsResponse.model_rebuild()
