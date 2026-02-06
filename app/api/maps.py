from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session as DBSession
from typing import List

from app.database import get_db
from app.models.player import Player
from app.models.character import Character
from app.models.map import Map, MapToken
from app.schemas.map import (
    MapCreate, MapResponse, MapUpdate,
    MapTokenCreate, MapTokenUpdate, MapTokenResponse
)
from app.core.auth import get_current_player
from app.websocket.manager import manager

router = APIRouter()

@router.get("/session/maps", response_model=List[MapResponse])
def get_session_maps(
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Get all maps for the current session."""
    maps = db.query(Map).filter(Map.session_id == current_player.session_id).all()
    return maps

@router.post("/session/maps", response_model=MapResponse)
async def create_map(
    map_data: MapCreate,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Create a new map. GM only."""
    if not current_player.is_gm:
        raise HTTPException(status_code=403, detail="Only GM can create maps")

    new_map = Map(
        session_id=current_player.session_id,
        name=map_data.name,
        background_url=map_data.background_url,
        width=map_data.width,
        height=map_data.height,
        grid_scale=map_data.grid_scale
    )
    db.add(new_map)
    db.commit()
    db.refresh(new_map)

    # Broadcast map_created so players know about the new map
    # Exclude the creator to avoid race condition with their REST response
    await manager.broadcast_event(
        "map_created",
        {
            "map": {
                "id": new_map.id,
                "session_id": new_map.session_id,
                "name": new_map.name,
                "background_url": new_map.background_url,
                "width": new_map.width,
                "height": new_map.height,
                "grid_scale": new_map.grid_scale,
                "is_active": new_map.is_active,
                "tokens": []
            }
        },
        exclude_token=current_player.token
    )

    return new_map

@router.get("/maps/{map_id}", response_model=MapResponse)
def get_map(
    map_id: str,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Get map details."""
    map_obj = db.query(Map).filter(Map.id == map_id).first()
    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found")
    
    if map_obj.session_id != current_player.session_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return map_obj

@router.put("/maps/{map_id}/active", response_model=MapResponse)
async def set_active_map(
    map_id: str,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Set map as active. GM only."""
    if not current_player.is_gm:
        raise HTTPException(status_code=403, detail="Only GM can set active map")

    map_obj = db.query(Map).filter(Map.id == map_id).first()
    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found")
    
    if map_obj.session_id != current_player.session_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Deactivate all other maps in session
    db.query(Map).filter(Map.session_id == current_player.session_id).update({"is_active": False})
    
    map_obj.is_active = True
    db.commit()
    db.refresh(map_obj)

    # Broadcast map_changed event
    await manager.broadcast_event(
        "map_changed",
        {"map_id": map_obj.id, "name": map_obj.name, "background_url": map_obj.background_url}
    )

    return map_obj

@router.post("/maps/{map_id}/tokens", response_model=MapTokenResponse)
async def add_token(
    map_id: str,
    token_data: MapTokenCreate,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Add token to map. GM only for now."""
    if not current_player.is_gm:
        raise HTTPException(status_code=403, detail="Only GM can add tokens")

    map_obj = db.query(Map).filter(Map.id == map_id).first()
    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found")
        
    if map_obj.session_id != current_player.session_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Validate character_id belongs to this session
    if token_data.character_id is not None:
        character = db.query(Character).join(Player).filter(
            Character.id == token_data.character_id,
            Player.session_id == current_player.session_id
        ).first()
        if not character:
            raise HTTPException(status_code=400, detail="Character not found in this session")

    new_token = MapToken(
        map_id=map_id,
        character_id=token_data.character_id,
        type=token_data.type,
        x=token_data.x,
        y=token_data.y,
        scale=token_data.scale,
        rotation=token_data.rotation,
        layer=token_data.layer,
        label=token_data.label,
        color=token_data.color
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    # Broadcast token_added with complete token data
    # Exclude the creator to avoid race condition with their REST response
    await manager.broadcast_event(
        "token_added",
        {
            "map_id": map_id,
            "token": {
                "id": new_token.id,
                "map_id": new_token.map_id,
                "character_id": new_token.character_id,
                "type": new_token.type,
                "x": new_token.x,
                "y": new_token.y,
                "scale": new_token.scale,
                "rotation": new_token.rotation,
                "layer": new_token.layer,
                "label": new_token.label,
                "color": new_token.color
            }
        },
        exclude_token=current_player.token
    )

    return new_token

@router.patch("/tokens/{token_id}", response_model=MapTokenResponse)
async def update_token(
    token_id: str,
    token_data: MapTokenUpdate,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Update token (move, scale, etc)."""
    token = db.query(MapToken).filter(MapToken.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # Check session access via map
    map_obj = db.query(Map).filter(Map.id == token.map_id).first()
    if map_obj.session_id != current_player.session_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Non-GM players can only move their own character's token when allowed
    if not current_player.is_gm:
        if token.character_id is None:
            raise HTTPException(status_code=403, detail="Only GM can move this token")
        character = db.query(Character).filter(Character.id == token.character_id).first()
        if not character or character.player_id != current_player.id:
            raise HTTPException(status_code=403, detail="You can only move your own token")
        if not current_player.can_move:
            raise HTTPException(status_code=403, detail="Movement not allowed by GM")

    # Update fields
    # Using exclude_unset=True in Pydantic would be better, but here we do manual check
    if token_data.x is not None: token.x = token_data.x
    if token_data.y is not None: token.y = token_data.y
    if token_data.scale is not None: token.scale = token_data.scale
    if token_data.rotation is not None: token.rotation = token_data.rotation
    if token_data.layer is not None: token.layer = token_data.layer
    if token_data.label is not None: token.label = token_data.label
    if token_data.color is not None: token.color = token_data.color
    
    db.commit()
    db.refresh(token)

    # Broadcast token_updated
    # We broadcast everything that might have changed
    await manager.broadcast_event(
        "token_updated",
        {
            "map_id": token.map_id,
            "token_id": token.id,
            "changes": token_data.dict(exclude_unset=True)
        },
        exclude_token=current_player.token # Don't echo back to sender if possible (frontend handles optimistic update)
    )

    return token

@router.delete("/tokens/{token_id}")
async def delete_token(
    token_id: str,
    current_player: Player = Depends(get_current_player),
    db: DBSession = Depends(get_db)
):
    """Delete token. GM only."""
    if not current_player.is_gm:
        raise HTTPException(status_code=403, detail="Only GM can delete tokens")

    token = db.query(MapToken).filter(MapToken.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
        
    map_obj = db.query(Map).filter(Map.id == token.map_id).first()
    if map_obj.session_id != current_player.session_id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(token)
    db.commit()

    await manager.broadcast_event(
        "token_removed",
        {"map_id": map_obj.id, "token_id": token_id}
    )

    return {"message": "Token deleted"}
