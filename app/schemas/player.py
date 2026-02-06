from pydantic import BaseModel


class PlayerBase(BaseModel):
    name: str
    is_gm: bool = False


class PlayerResponse(BaseModel):
    id: int
    name: str
    is_gm: bool
    is_ready: bool = False
    can_move: bool = False

    class Config:
        from_attributes = True
