from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserCharacterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    class_name: Optional[str] = None
    level: int = Field(default=1, ge=1, le=20)
    is_npc: bool = False
    strength: int = Field(default=10, ge=1, le=30)
    dexterity: int = Field(default=10, ge=1, le=30)
    constitution: int = Field(default=10, ge=1, le=30)
    intelligence: int = Field(default=10, ge=1, le=30)
    wisdom: int = Field(default=10, ge=1, le=30)
    charisma: int = Field(default=10, ge=1, le=30)
    max_hp: int = Field(default=10, ge=1)
    current_hp: int = Field(default=10, ge=0)
    appearance: Optional[str] = None


class UserCharacterUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    class_name: Optional[str] = None
    level: Optional[int] = Field(default=None, ge=1, le=20)
    is_npc: Optional[bool] = None
    strength: Optional[int] = Field(default=None, ge=1, le=30)
    dexterity: Optional[int] = Field(default=None, ge=1, le=30)
    constitution: Optional[int] = Field(default=None, ge=1, le=30)
    intelligence: Optional[int] = Field(default=None, ge=1, le=30)
    wisdom: Optional[int] = Field(default=None, ge=1, le=30)
    charisma: Optional[int] = Field(default=None, ge=1, le=30)
    max_hp: Optional[int] = Field(default=None, ge=1)
    current_hp: Optional[int] = Field(default=None, ge=0)
    appearance: Optional[str] = None


class UserCharacterResponse(BaseModel):
    id: int
    user_id: int
    name: str
    class_name: Optional[str] = None
    level: int
    is_npc: bool
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    max_hp: int
    current_hp: int
    appearance: Optional[str] = None
    avatar_url: Optional[str] = None
    sessions_played: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
