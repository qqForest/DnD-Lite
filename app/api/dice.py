from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.player import Player
from app.schemas.dice import DiceRoll, DiceResult
from app.services.dice import DiceService
from app.websocket.manager import manager
from app.core.auth import get_current_player

router = APIRouter()


@router.post("/roll", response_model=DiceResult)
async def roll_dice(
    data: DiceRoll,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Roll dice and broadcast the result."""

    try:
        rolls, modifier, total, all_rolls, chosen_index = DiceService.roll_with_type(
            data.dice, data.roll_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Формируем formula для отображения
    formula = data.dice
    if modifier != 0:
        formula = f"{data.dice.split('+')[0].split('-')[0]}{'+' if modifier > 0 else ''}{modifier if modifier != 0 else ''}"

    result = DiceResult(
        dice=data.dice,
        rolls=rolls,
        modifier=modifier,
        total=total,
        formula=formula,
        reason=data.reason,
        player_name=current_player.name,
        roll_type=data.roll_type,
        all_rolls=all_rolls,
        chosen_index=chosen_index,
    )

    # Broadcast dice result to all players
    await manager.broadcast_event("dice_result", result.model_dump())

    return result
