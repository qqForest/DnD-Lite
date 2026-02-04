from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session as DBSession
import json
import os

from app.database import engine, Base, get_db
from app.api import api_router
from app.websocket.manager import manager
from app.websocket.handlers import handle_message
from app.models.player import Player

# Create database tables
Base.metadata.create_all(bind=engine)

# Apply pending column migrations (safe to re-run)
from app.migrations import run_migrations
run_migrations()

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

# Include API routes
app.include_router(api_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    """WebSocket endpoint for real-time communication."""
    print(f"WS Connection attempt. Token from Query: {token}")
    print(f"WS Headers: {dict(websocket.headers)}")
    
    if not token:
        print("WS Connection rejected: No token provided in Query")
        # If no token, we can't search for player. 
        # But we must close or reject. Let's send 4003 (Forbidden)
        await websocket.close(code=4003, reason="No token provided")
        return

    # Get database session
    db = next(get_db())

    player = None
    try:
        # Validate token and get player
        print(f"WS Searching for player with token: {token}")
        player = db.query(Player).filter(Player.token == token).first()
        
        if not player:
            print(f"WS Connection rejected: Player not found for token {token}")
            await websocket.close(code=4001, reason="Invalid token")
            return

        print(f"WS Found player: {player.name} (id: {player.id}). Accepting connection...")
        # Connect player
        await manager.connect(websocket, token, player.id)
        print(f"WS Successfully connected and accepted: {player.name}")

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
                # print(f"WS Message from {player.name}: {message}")
                await handle_message(db, token, player, message)
            except WebSocketDisconnect:
                raise
            except json.JSONDecodeError:
                await manager.send_personal(token, {
                    "type": "error",
                    "payload": {"message": "Invalid JSON"}
                })
            except Exception as e:
                print(f"WS Processing Error from {player.name}: {str(e)}")

    except WebSocketDisconnect:
        if player:
            print(f"WS Disconnected: {player.name}")
            manager.disconnect(token)
            await manager.broadcast_event(
                "player_left",
                {"player_id": player.id}
            )
        else:
            print("WS Disconnected during handshake or unknown player")
    except Exception as e:
        print(f"WS Top-level Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print(f"WS Connection cleanup finished for token: {token[:8]}...")


# Mount static files from frontend/dist if it exists
static_path = "frontend/dist"
if os.path.exists(static_path):
    from fastapi.staticfiles import StaticFiles
    # Support assets
    if os.path.exists(os.path.join(static_path, "assets")):
        app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets")), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Prevent catching API calls
        if full_path.startswith("api"):
            return {"error": "Not Found"}
            
        # Check if the requested file exists in the static_path
        file_path = os.path.join(static_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Otherwise return index.html for SPA routing
        return FileResponse(os.path.join(static_path, "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "DnD Lite GM API", "docs": "/docs", "frontend": "Not built yet. Use npm run build in frontend folder."}
