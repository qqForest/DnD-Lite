from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


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

    class Config:
        from_attributes = True
