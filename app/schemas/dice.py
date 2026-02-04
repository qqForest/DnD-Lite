from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class DiceRoll(BaseModel):
    dice: str  # "2d6+3", "1d20", "4d6"
    reason: Optional[str] = None
    roll_type: Literal["normal", "advantage", "disadvantage"] = "normal"


class DiceResult(BaseModel):
    dice: str
    rolls: List[int]
    modifier: int
    total: int
    formula: str  # Полная формула броска (например "2d6+3")
    reason: Optional[str]
    player_name: str
    roll_type: str = "normal"  # "normal" | "advantage" | "disadvantage"
    all_rolls: Optional[List[List[int]]] = None  # Все броски при advantage/disadvantage
    chosen_index: Optional[int] = None  # Индекс выбранного броска (0 или 1)
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
