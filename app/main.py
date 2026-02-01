from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession
import json

from app.database import engine, Base, get_db
from app.api import api_router
from app.websocket.manager import manager
from app.websocket.handlers import handle_message
from app.models.player import Player

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DnD Lite GM",
    description="Lightweight D&D Game Master assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

# Include API routes
app.include_router(api_router)

# Mount static files from frontend/dist if it exists
static_path = "frontend/dist"
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
else:
    @app.get("/")
    def root():
        return {"message": "DnD Lite GM API", "docs": "/docs", "frontend": "Not built yet. Use npm run build in frontend folder."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time communication."""
    # Get database session
    db = next(get_db())

    try:
        # Validate token and get player
        player = db.query(Player).filter(Player.token == token).first()
        if not player:
            await websocket.close(code=4001, reason="Invalid token")
            return

        # Connect player
        await manager.connect(websocket, token, player.id)

        # Broadcast player joined
        await manager.broadcast_event(
            "player_joined",
            {"player_id": player.id, "player_name": player.name, "is_gm": player.is_gm},
            exclude_token=token
        )

        # Handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                await handle_message(db, token, player, message)
            except json.JSONDecodeError:
                await manager.send_personal(token, {
                    "type": "error",
                    "payload": {"message": "Invalid JSON"}
                })

    except WebSocketDisconnect:
        manager.disconnect(token)
        # Broadcast player left
        await manager.broadcast_event(
            "player_left",
            {"player_id": player.id}
        )
    finally:
        db.close()
