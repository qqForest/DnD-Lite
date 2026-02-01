from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.player import Player
from app.schemas.dice import DiceRoll, DiceResult
from app.services.dice import DiceService
from app.websocket.manager import manager

router = APIRouter()


@router.post("/roll", response_model=DiceResult)
async def roll_dice(
    data: DiceRoll,
    token: str,
    db: DBSession = Depends(get_db)
):
    """Roll dice and broadcast the result."""
    player = db.query(Player).filter(Player.token == token).first()
    if not player:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        rolls, modifier, total = DiceService.roll(data.dice)
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
        player_name=player.name,
    )

    # Broadcast dice result to all players
    await manager.broadcast_event("dice_result", result.model_dump())

    return result
