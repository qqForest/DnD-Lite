from pydantic import BaseModel, Field
from typing import Optional


class CharacterCreate(BaseModel):
    name: str
    class_name: Optional[str] = None
    level: int = Field(default=1, ge=1, le=20)
    strength: int = Field(default=10, ge=1, le=30)
    dexterity: int = Field(default=10, ge=1, le=30)
    constitution: int = Field(default=10, ge=1, le=30)
    intelligence: int = Field(default=10, ge=1, le=30)
    wisdom: int = Field(default=10, ge=1, le=30)
    charisma: int = Field(default=10, ge=1, le=30)
    max_hp: int = Field(default=10, ge=1)
    current_hp: Optional[int] = None


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    class_name: Optional[str] = None
    level: Optional[int] = Field(default=None, ge=1, le=20)
    strength: Optional[int] = Field(default=None, ge=1, le=30)
    dexterity: Optional[int] = Field(default=None, ge=1, le=30)
    constitution: Optional[int] = Field(default=None, ge=1, le=30)
    intelligence: Optional[int] = Field(default=None, ge=1, le=30)
    wisdom: Optional[int] = Field(default=None, ge=1, le=30)
    charisma: Optional[int] = Field(default=None, ge=1, le=30)
    max_hp: Optional[int] = Field(default=None, ge=1)
    current_hp: Optional[int] = None


class CharacterResponse(BaseModel):
    id: int
    player_id: int
    name: str
    class_name: Optional[str]
    level: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    max_hp: int
    current_hp: int

    class Config:
        from_attributes = True
