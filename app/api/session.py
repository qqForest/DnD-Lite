import uuid
import string
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.session import Session
from app.models.player import Player
from app.schemas.session import (
    SessionResponse,
    SessionJoin,
    SessionJoinResponse,
    SessionState,
    PlayerReadyRequest,
)
from app.schemas.player import PlayerResponse

router = APIRouter()


def generate_room_code(length: int = 6) -> str:
    """Generate a random alphanumeric room code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


@router.post("/session", response_model=SessionResponse)
def create_session(db: DBSession = Depends(get_db)):
    """Create a new game session. Returns room code and GM token."""
    # Generate unique room code
    while True:
        code = generate_room_code()
        existing = db.query(Session).filter(Session.code == code).first()
        if not existing:
            break

    gm_token = str(uuid.uuid4())

    session = Session(code=code, gm_token=gm_token, is_active=True)
    db.add(session)
    db.commit()
    db.refresh(session)

    # Create GM player
    gm_player = Player(
        session_id=session.id,
        name="Game Master",
        token=gm_token,
        is_gm=True
    )
    db.add(gm_player)
    db.commit()

    return SessionResponse(code=code, gm_token=gm_token)


@router.post("/session/join", response_model=SessionJoinResponse)
def join_session(data: SessionJoin, db: DBSession = Depends(get_db)):
    """Join an existing session by room code."""
    session = db.query(Session).filter(
        Session.code == data.code.upper(),
        Session.is_active == True
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if player name already exists in session
    existing_player = db.query(Player).filter(
        Player.session_id == session.id,
        Player.name == data.name
    ).first()

    if existing_player:
        raise HTTPException(status_code=400, detail="Player name already taken")

    player_token = str(uuid.uuid4())
    player = Player(
        session_id=session.id,
        name=data.name,
        token=player_token,
        is_gm=False
    )
    db.add(player)
    db.commit()
    db.refresh(player)

    return SessionJoinResponse(
        player_id=player.id,
        token=player_token,
        session_code=session.code
    )


@router.get("/session", response_model=SessionState)
def get_session_state(token: str, db: DBSession = Depends(get_db)):
    """Get current session state. Requires player or GM token."""
    player = db.query(Player).filter(Player.token == token).first()
    if not player:
        raise HTTPException(status_code=401, detail="Invalid token")

    session = player.session
    player_count = db.query(Player).filter(Player.session_id == session.id).count()

    return SessionState(
        id=session.id,
        code=session.code,
        is_active=session.is_active,
        session_started=session.session_started,
        created_at=session.created_at,
        player_count=player_count
    )


@router.post("/session/start")
async def start_session(token: str, db: DBSession = Depends(get_db)):
    """Start the session. Only GM can start the session."""
    player = db.query(Player).filter(Player.token == token).first()
    if not player:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not player.is_gm:
        raise HTTPException(status_code=403, detail="Only GM can start the session")
    
    session = player.session
    session.session_started = True
    db.commit()
    db.refresh(session)
    
    # Broadcast session_started event
    from app.websocket.manager import manager
    await manager.broadcast_event(
        "session_started",
        {"session_id": session.id, "session_code": session.code}
    )
    
    return {"message": "Session started", "session_started": True}


@router.get("/session/players", response_model=list[PlayerResponse])
def get_session_players(token: str, db: DBSession = Depends(get_db)):
    """Get all players in the session."""
    player = db.query(Player).filter(Player.token == token).first()
    if not player:
        raise HTTPException(status_code=401, detail="Invalid token")

    players = db.query(Player).filter(Player.session_id == player.session_id).all()
    return players


@router.post("/session/ready")
async def set_player_ready(
    data: PlayerReadyRequest,
    token: str,
    db: DBSession = Depends(get_db)
):
    """Set player ready status. Only for non-GM players."""
    player = db.query(Player).filter(Player.token == token).first()
    if not player:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if player.is_gm:
        raise HTTPException(status_code=403, detail="GM cannot set ready status")
    
    player.is_ready = data.is_ready
    db.commit()
    db.refresh(player)
    
    # Broadcast player_ready event
    from app.websocket.manager import manager
    await manager.broadcast_event(
        "player_ready",
        {"player_id": player.id, "player_name": player.name, "is_ready": data.is_ready}
    )
    
    return {"message": f"Player ready status set to {data.is_ready}", "is_ready": data.is_ready}
