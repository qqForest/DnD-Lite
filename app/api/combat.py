from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.player import Player
from app.models.character import Character
from app.models.combat import Combat, CombatParticipant, InitiativeRoll
from app.schemas.combat import (
    CombatResponse, CombatParticipantResponse, CombatAction,
    InitiativeEntry, InitiativeListResponse, InitiativeRollResponse
)
from app.services.combat import CombatService
from app.services.dice import DiceService
from app.websocket.manager import manager

router = APIRouter()


def get_player_by_token(token: str, db: DBSession) -> Player:
    """Helper to get player from token."""
    player = db.query(Player).filter(Player.token == token).first()
    if not player:
        raise HTTPException(status_code=401, detail="Invalid token")
    return player


def require_gm(player: Player):
    """Check if player is GM."""
    if not player.is_gm:
        raise HTTPException(status_code=403, detail="Only GM can perform this action")


def get_active_combat(db: DBSession, session_id: int) -> Combat:
    """Get active combat for session."""
    combat = db.query(Combat).filter(
        Combat.session_id == session_id,
        Combat.is_active == True
    ).first()
    if not combat:
        raise HTTPException(status_code=404, detail="No active combat")
    return combat


def get_gm_token(db: DBSession, session_id: int) -> Optional[str]:
    """Get GM token for a session."""
    gm = db.query(Player).filter(
        Player.session_id == session_id,
        Player.is_gm == True
    ).first()
    return gm.token if gm else None


def build_combat_response(combat: Combat) -> dict:
    """Build combat response with participants."""
    participants = []
    for p in sorted(combat.participants, key=lambda x: x.initiative, reverse=True):
        participants.append({
            "id": p.id,
            "character_id": p.character_id,
            "character_name": p.character.name,
            "initiative": p.initiative,
            "current_hp": p.current_hp,
            "is_active": p.is_active,
        })

    return {
        "id": combat.id,
        "is_active": combat.is_active,
        "round_number": combat.round_number,
        "current_turn_id": combat.current_turn_id,
        "participants": participants,
    }


def build_initiative_list(db: DBSession, combat: Combat) -> List[InitiativeEntry]:
    """Build sorted initiative list for combat."""
    # Get all players in session
    players = db.query(Player).filter(
        Player.session_id == combat.session_id,
        Player.is_gm == False
    ).all()

    # Get existing initiative rolls
    rolls = {r.player_id: r.roll for r in combat.initiative_rolls}

    entries = []
    for player in players:
        # Try to get character name
        character = db.query(Character).filter(
            Character.player_id == player.id
        ).first()

        entries.append(InitiativeEntry(
            player_id=player.id,
            player_name=player.name,
            character_name=character.name if character else None,
            roll=rolls.get(player.id),
            is_npc=False
        ))

    # Sort: players with rolls first (descending), then players without rolls
    entries.sort(key=lambda e: (e.roll is None, -(e.roll or 0)))
    return entries


@router.post("/start")
async def start_combat(
    token: str,
    character_ids: Optional[List[int]] = None,
    db: DBSession = Depends(get_db)
):
    """Start a new combat. GM only. Broadcasts combat_started to all players."""
    player = get_player_by_token(token, db)
    require_gm(player)

    # Create combat
    combat = CombatService.create_combat(db, player.session_id)

    # Add participants if provided (backwards compatibility)
    if character_ids:
        for char_id in character_ids:
            character = db.query(Character).join(Player).filter(
                Character.id == char_id,
                Player.session_id == player.session_id
            ).first()

            if character:
                CombatService.add_participant(db, combat, character)

    db.refresh(combat)
    response = build_combat_response(combat)

    # Broadcast combat started - triggers initiative modal on players
    await manager.broadcast_event("combat_started", {
        "combat_id": combat.id
    })

    return response


@router.post("/end")
async def end_combat(token: str, db: DBSession = Depends(get_db)):
    """End the current combat. GM only."""
    player = get_player_by_token(token, db)
    require_gm(player)

    combat = get_active_combat(db, player.session_id)
    CombatService.end_combat(db, combat)

    # Broadcast combat ended
    await manager.broadcast_event("combat_ended", {})

    return {"message": "Combat ended"}


@router.post("/initiative", response_model=InitiativeRollResponse)
async def roll_initiative(token: str, db: DBSession = Depends(get_db)):
    """Roll initiative for the current player. Returns roll result."""
    player = get_player_by_token(token, db)

    if player.is_gm:
        raise HTTPException(status_code=400, detail="GM cannot roll initiative")

    combat = get_active_combat(db, player.session_id)

    # Check if already rolled
    existing = db.query(InitiativeRoll).filter(
        InitiativeRoll.combat_id == combat.id,
        InitiativeRoll.player_id == player.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already rolled initiative")

    # Roll d20
    roll = DiceService.roll_initiative()

    # Save roll
    initiative_roll = InitiativeRoll(
        combat_id=combat.id,
        player_id=player.id,
        roll=roll
    )
    db.add(initiative_roll)
    db.commit()

    # Send to GM only
    gm_token = get_gm_token(db, player.session_id)
    if gm_token:
        await manager.send_personal(gm_token, {
            "type": "initiative_rolled",
            "payload": {
                "player_id": player.id,
                "player_name": player.name,
                "roll": roll
            }
        })

    return InitiativeRollResponse(roll=roll, player_name=player.name)


@router.get("/initiative", response_model=InitiativeListResponse)
def get_initiative_list(token: str, db: DBSession = Depends(get_db)):
    """Get current initiative list for active combat."""
    player = get_player_by_token(token, db)
    combat = get_active_combat(db, player.session_id)

    entries = build_initiative_list(db, combat)
    return InitiativeListResponse(entries=entries)


@router.post("/next-turn")
async def next_turn(token: str, db: DBSession = Depends(get_db)):
    """Move to the next turn in combat. GM only."""
    player = get_player_by_token(token, db)
    require_gm(player)

    combat = get_active_combat(db, player.session_id)
    next_participant = CombatService.next_turn(db, combat)

    if not next_participant:
        raise HTTPException(status_code=400, detail="No active participants")

    # Broadcast turn change
    await manager.broadcast_event("turn_changed", {
        "participant_id": next_participant.id,
        "character_id": next_participant.character_id,
        "character_name": next_participant.character.name,
        "round_number": combat.round_number,
    })

    return {
        "participant_id": next_participant.id,
        "character_id": next_participant.character_id,
        "round_number": combat.round_number,
    }


@router.post("/action")
async def combat_action(
    action: CombatAction,
    token: str,
    db: DBSession = Depends(get_db)
):
    """Perform a combat action (damage/heal)."""
    player = get_player_by_token(token, db)
    combat = get_active_combat(db, player.session_id)

    result = {"action": action.action_type}

    if action.target_id and action.damage:
        participant = db.query(CombatParticipant).filter(
            CombatParticipant.id == action.target_id,
            CombatParticipant.combat_id == combat.id
        ).first()

        if participant:
            CombatService.apply_damage(db, participant, action.damage)
            result["target_hp"] = participant.current_hp
            result["target_active"] = participant.is_active

            await manager.broadcast_event("hp_changed", {
                "character_id": participant.character_id,
                "hp": participant.current_hp,
                "damage": action.damage,
            })

    if action.target_id and action.healing:
        participant = db.query(CombatParticipant).filter(
            CombatParticipant.id == action.target_id,
            CombatParticipant.combat_id == combat.id
        ).first()

        if participant:
            max_hp = participant.character.max_hp
            CombatService.apply_healing(db, participant, action.healing, max_hp)
            result["target_hp"] = participant.current_hp

            await manager.broadcast_event("hp_changed", {
                "character_id": participant.character_id,
                "hp": participant.current_hp,
                "heal": action.healing,
            })

    return result


@router.get("", response_model=None)
def get_combat_state(token: str, db: DBSession = Depends(get_db)):
    """Get current combat state."""
    player = get_player_by_token(token, db)

    combat = db.query(Combat).filter(
        Combat.session_id == player.session_id,
        Combat.is_active == True
    ).first()

    if not combat:
        return {"active": False}

    response = build_combat_response(combat)
    response["initiative_list"] = [e.model_dump() for e in build_initiative_list(db, combat)]
    return response
