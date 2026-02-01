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
from app.core.auth import create_access_token, create_refresh_token, get_current_player
from app.schemas.auth import Token

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

    access_token = create_access_token(data={"sub": gm_token})
    refresh_token = create_refresh_token(data={"sub": gm_token})

    return SessionResponse(
        code=code, 
        gm_token=gm_token,
        access_token=access_token,
        refresh_token=refresh_token
    )


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

    access_token = create_access_token(data={"sub": player_token})
    refresh_token = create_refresh_token(data={"sub": player_token})

    return SessionJoinResponse(
        player_id=player.id,
        token=player_token,
        session_code=session.code,
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/auth/refresh", response_model=Token)
def refresh_token(token: Token):
    """Refresh access token."""
    # We'll use the same get_current_player dependency but we might need a separate one that accepts refresh tokens?
    # Actually get_current_player validates against secret key. 
    # But usually refresh endpoints verification is slightly different (checks if it IS a refresh token).
    # For now, let's manually verify.
    from jose import jwt, JWTError
    from app.config import get_settings
    settings = get_settings()
    
    try:
        payload = jwt.decode(token.refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        player_token = payload.get("sub")
        if player_token is None:
             raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    access_token = create_access_token(data={"sub": player_token})
    # Optionally rotate refresh token
    return Token(access_token=access_token, refresh_token=token.refresh_token, token_type="bearer")


@router.get("/session", response_model=SessionState)
def get_session_state(
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Get current session state. Requires authentication."""
    session = current_player.session
    player_count = db.query(Player).filter(Player.session_id == session.id).count()

    return SessionState(
        id=session.id,
        code=session.code,
        is_active=session.is_active,
        session_started=session.session_started,
        created_at=session.created_at,
        player_count=player_count,
        player_id=current_player.id
    )


@router.post("/session/start")
async def start_session(
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Start the session. Only GM can start the session."""
    if not current_player.is_gm:
        raise HTTPException(status_code=403, detail="Only GM can start the session")
    
    session = current_player.session
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
def get_session_players(
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Get all players in the session."""
    players = db.query(Player).filter(Player.session_id == current_player.session_id).all()
    return players


@router.post("/session/ready")
async def set_player_ready(
    data: PlayerReadyRequest,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Set player ready status. Only for non-GM players."""
    if current_player.is_gm:
        raise HTTPException(status_code=403, detail="GM cannot set ready status")
    
    current_player.is_ready = data.is_ready
    db.commit()
    db.refresh(current_player)
    
    # Broadcast player_ready event
    from app.websocket.manager import manager
    await manager.broadcast_event(
        "player_ready",
        {"player_id": current_player.id, "player_name": current_player.name, "is_ready": data.is_ready}
    )
    
    return {"message": f"Player ready status set to {data.is_ready}", "is_ready": data.is_ready}
