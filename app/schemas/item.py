from pydantic import BaseModel
from typing import Optional, Dict, Any


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    effects: Optional[Dict[str, Any]] = None
    is_equipped: bool = False


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    effects: Optional[Dict[str, Any]] = None
    is_equipped: Optional[bool] = None


class ItemResponse(BaseModel):
    id: int
    character_id: int
    name: str
    description: Optional[str]
    effects: Optional[Dict[str, Any]]
    is_equipped: bool

    class Config:
        from_attributes = True
