from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class MapTokenBase(BaseModel):
    x: float
    y: float
    scale: float = 1.0
    rotation: float = 0.0
    layer: str = "tokens"
    type: str = "character"
    label: Optional[str] = None
    color: Optional[str] = "#red"
    icon: Optional[str] = None

class MapTokenCreate(MapTokenBase):
    character_id: Optional[int] = None

class MapTokenUpdate(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    scale: Optional[float] = None
    rotation: Optional[float] = None
    layer: Optional[str] = None
    label: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    character_id: Optional[int] = None

class MapTokenResponse(MapTokenBase):
    id: str
    map_id: str
    character_id: Optional[int] = None

    class Config:
        from_attributes = True

class MapBase(BaseModel):
    name: str
    background_url: Optional[str] = None
    width: int = 1920
    height: int = 1080
    grid_scale: int = 50

class MapCreate(MapBase):
    pass

class MapUpdate(BaseModel):
    name: Optional[str] = None
    background_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    grid_scale: Optional[int] = None
    is_active: Optional[bool] = None

class MapResponse(MapBase):
    id: str
    session_id: int
    is_active: bool
    tokens: List[MapTokenResponse] = []

    class Config:
        from_attributes = True
