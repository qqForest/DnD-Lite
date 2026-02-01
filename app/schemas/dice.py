from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DiceRoll(BaseModel):
    dice: str  # "2d6+3", "1d20", "4d6"
    reason: Optional[str] = None


class DiceResult(BaseModel):
    dice: str
    rolls: List[int]
    modifier: int
    total: int
    formula: str  # Полная формула броска (например "2d6+3")
    reason: Optional[str]
    player_name: str
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
