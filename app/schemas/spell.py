from pydantic import BaseModel, Field
from typing import Optional


class SpellCreate(BaseModel):
    name: str
    level: int = Field(default=0, ge=0, le=9)
    description: Optional[str] = None
    damage_dice: Optional[str] = None


class SpellUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = Field(default=None, ge=0, le=9)
    description: Optional[str] = None
    damage_dice: Optional[str] = None


class SpellResponse(BaseModel):
    id: int
    character_id: int
    name: str
    level: int
    description: Optional[str]
    damage_dice: Optional[str]

    class Config:
        from_attributes = True
