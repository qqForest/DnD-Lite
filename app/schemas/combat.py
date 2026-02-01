from pydantic import BaseModel
from typing import List, Optional


class CombatParticipantResponse(BaseModel):
    id: int
    character_id: int
    character_name: str
    initiative: int
    current_hp: int
    is_active: bool

    class Config:
        from_attributes = True


class CombatResponse(BaseModel):
    id: int
    is_active: bool
    round_number: int
    current_turn_id: Optional[int]
    participants: List[CombatParticipantResponse]

    class Config:
        from_attributes = True


class CombatAction(BaseModel):
    action_type: str  # "attack", "spell", "item", "other"
    target_id: Optional[int] = None
    description: Optional[str] = None
    damage: Optional[int] = None
    healing: Optional[int] = None


# Initiative schemas
class InitiativeEntry(BaseModel):
    """Entry in the initiative list."""
    player_id: int
    player_name: str
    character_name: Optional[str] = None
    roll: Optional[int] = None
    is_npc: bool = False


class InitiativeListResponse(BaseModel):
    """Response with sorted initiative list."""
    entries: List[InitiativeEntry]


class InitiativeRollResponse(BaseModel):
    """Response after rolling initiative."""
    roll: int
    player_name: str
