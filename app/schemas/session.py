from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SessionCreate(BaseModel):
    pass


class SessionResponse(BaseModel):
    code: str
    gm_token: str
    access_token: str
    refresh_token: str

    class Config:
        from_attributes = True


class SessionJoin(BaseModel):
    code: str
    name: str
    user_character_id: Optional[int] = None


class SessionJoinResponse(BaseModel):
    player_id: int
    token: str
    session_code: str
    access_token: str
    refresh_token: str
    character_id: Optional[int] = None

    class Config:
        from_attributes = True


class SessionState(BaseModel):
    id: int
    code: str
    is_active: bool
    session_started: bool
    created_at: datetime
    player_count: int
    player_id: Optional[int] = None

    class Config:
        from_attributes = True


class PlayerReadyRequest(BaseModel):
    is_ready: bool
