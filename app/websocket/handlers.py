import logging
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.websocket.manager import manager
from app.services.dice import DiceService
from app.models.player import Player

logger = logging.getLogger(__name__)


async def handle_message(
    db: DBSession,
    token: str,
    player: Player,
    message: dict
):
    """Route incoming WebSocket messages to appropriate handlers."""
    msg_type = message.get("type")

    # Ignore pong responses from client (heartbeat reply)
    if msg_type == "pong":
        return

    handlers = {
        "roll_dice": handle_roll_dice,
        "chat": handle_chat,
    }

    handler = handlers.get(msg_type)
    if handler:
        try:
            await handler(db, token, player, message.get("payload", {}))
        except Exception as e:
            logger.error(f"Error handling '{msg_type}' from player {player.name}: {e}")
            await manager.send_personal(token, {
                "type": "error",
                "payload": {"message": f"Error processing {msg_type}"}
            })
    elif msg_type:
        logger.warning(f"Unknown message type '{msg_type}' from player {player.name}")


async def handle_roll_dice(
    db: DBSession,
    token: str,
    player: Player,
    payload: dict
):
    """Handle dice roll request."""
    dice = payload.get("dice", "1d20")
    reason = payload.get("reason")

    try:
        rolls, modifier, total = DiceService.roll(dice)
        result = {
            "player_id": player.id,
            "player_name": player.name,
            "dice": dice,
            "rolls": rolls,
            "modifier": modifier,
            "total": total,
            "reason": reason,
        }
        await manager.broadcast_event("dice_result", result)
    except ValueError as e:
        await manager.send_personal(token, {
            "type": "error",
            "payload": {"message": str(e)}
        })


async def handle_chat(
    db: DBSession,
    token: str,
    player: Player,
    payload: dict
):
    """Handle chat message."""
    message = payload.get("message", "")
    if not message.strip():
        return

    await manager.broadcast_event("chat", {
        "player_id": player.id,
        "player_name": player.name,
        "message": message,
    })
