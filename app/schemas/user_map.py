from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class UserMapTokenCreate(BaseModel):
    type: str = "monster"
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0
    rotation: float = 0.0
    label: Optional[str] = None
    color: str = "#D94A4A"
    icon: Optional[str] = None
    layer: str = "tokens"


class UserMapTokenUpdate(BaseModel):
    type: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    scale: Optional[float] = None
    rotation: Optional[float] = None
    label: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    layer: Optional[str] = None


class UserMapTokenResponse(BaseModel):
    id: str
    user_map_id: str
    type: str
    x: float
    y: float
    scale: float
    rotation: float
    label: Optional[str] = None
    color: str
    icon: Optional[str] = None
    layer: str

    class Config:
        from_attributes = True


class UserMapCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    background_url: Optional[str] = None
    width: int = Field(default=1920, ge=100)
    height: int = Field(default=1080, ge=100)
    grid_scale: int = Field(default=50, ge=10)


class UserMapUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    background_url: Optional[str] = None
    width: Optional[int] = Field(default=None, ge=100)
    height: Optional[int] = Field(default=None, ge=100)
    grid_scale: Optional[int] = Field(default=None, ge=10)


class UserMapResponse(BaseModel):
    id: str
    user_id: int
    name: str
    background_url: Optional[str] = None
    width: int
    height: int
    grid_scale: int
    created_at: datetime
    tokens: List[UserMapTokenResponse] = []

    class Config:
        from_attributes = True
