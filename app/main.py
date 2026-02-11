import asyncio
import json
import logging
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import engine, Base, get_db
from app.api import api_router
from app.websocket.manager import manager
from app.websocket.handlers import handle_message
from app.models.player import Player

logger = logging.getLogger(__name__)

# WebSocket constants
MAX_MESSAGE_SIZE = 10240  # 10 KB
MAX_CONSECUTIVE_ERRORS = 5
RECEIVE_TIMEOUT = 300  # 5 minutes
HEARTBEAT_INTERVAL = 30  # seconds

# Create database tables
Base.metadata.create_all(bind=engine)

# Apply pending column migrations (safe to re-run)
from app.migrations import run_migrations
run_migrations()

# Cleanup old sessions on startup
try:
    from app.database import get_db, cleanup_old_sessions
    db = next(get_db())
    try:
        cleanup_old_sessions(db, days=7)
    finally:
        db.close()
except Exception as e:
    logger.warning(f"Startup cleanup failed: {e}")

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


async def _heartbeat(websocket: WebSocket, token: str):
    """Send periodic ping messages to keep the connection alive."""
    try:
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            await websocket.send_json({"type": "ping"})
    except Exception:
        logger.debug(f"Heartbeat stopped for token {token[:8]}...")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    """WebSocket endpoint for real-time communication."""
    logger.info(f"WS Connection attempt with token: {token[:8] if token else 'None'}...")

    if not token:
        logger.warning("WS Connection rejected: No token provided")
        await websocket.close(code=4003, reason="No token provided")
        return

    # Validate token with a separate DB session (closed immediately after)
    db = next(get_db())
    try:
        player = db.query(Player).filter(Player.token == token).first()
        if not player:
            logger.warning(f"WS Connection rejected: Player not found for token {token[:8]}...")
            await websocket.close(code=4001, reason="Invalid token")
            return
        # Cache player info in local variables
        player_id = player.id
        player_name = player.name
        is_gm = player.is_gm
    finally:
        db.close()

    # Connect player
    try:
        await manager.connect(websocket, token, player_id)
    except Exception as e:
        logger.error(f"WS Failed to connect player {player_name}: {e}")
        return

    logger.info(f"WS Successfully connected: {player_name}")

    # Start heartbeat task
    heartbeat_task = asyncio.create_task(_heartbeat(websocket, token))

    # Broadcast player joined
    await manager.broadcast_event(
        "player_joined",
        {"player_id": player_id, "player_name": player_name, "is_gm": is_gm},
        exclude_token=token
    )

    consecutive_errors = 0

    try:
        while True:
            # Receive with timeout
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=RECEIVE_TIMEOUT
                )
            except asyncio.TimeoutError:
                logger.info(f"WS Timeout for {player_name}, closing connection")
                break

            # Check message size
            if len(data) > MAX_MESSAGE_SIZE:
                await manager.send_personal(token, {
                    "type": "error",
                    "payload": {"message": "Message too large"}
                })
                continue

            # Parse JSON
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_personal(token, {
                    "type": "error",
                    "payload": {"message": "Invalid JSON"}
                })
                continue

            # Handle message with a fresh DB session
            db = next(get_db())
            try:
                # Fetch fresh player from DB for each message
                current_player = db.query(Player).filter(Player.token == token).first()
                if not current_player:
                    logger.warning(f"WS Player no longer exists: {player_name}")
                    break
                await handle_message(db, token, current_player, message)
                consecutive_errors = 0
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"WS Processing error from {player_name}: {e}")
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    logger.error(f"WS Too many consecutive errors for {player_name}, closing")
                    break
            finally:
                db.close()

    except WebSocketDisconnect:
        logger.info(f"WS Disconnected: {player_name}")
    except Exception as e:
        logger.error(f"WS Unexpected error for {player_name}: {e}")
    finally:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass

        # Start grace period for temporary disconnect (unless explicit leave)
        db = next(get_db())
        try:
            player = db.query(Player).filter(Player.token == token).first()
            if player and player.left_at is None:
                # Temporary disconnect - start grace period
                await manager.start_grace_period(token)
                logger.info(f"WS Temporary disconnect for {player_name}, grace period started")
            elif player:
                # Explicit leave already marked
                logger.info(f"WS Player {player_name} explicitly left")
        except Exception as e:
            logger.error(f"WS Failed to start grace period: {e}")
        finally:
            db.close()

        await manager.disconnect(token)
        await manager.broadcast_event(
            "player_left",
            {"player_id": player_id}
        )
        logger.info(f"WS Connection cleanup finished for {player_name}")


# Mount uploads directory for user-uploaded files (map backgrounds, etc.)
from fastapi.staticfiles import StaticFiles
uploads_path = "uploads"
os.makedirs(os.path.join(uploads_path, "maps"), exist_ok=True)
os.makedirs(os.path.join(uploads_path, "avatars"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

# Mount static files from frontend/dist if it exists
static_path = "frontend/dist"
if os.path.exists(static_path):
    # Support assets
    if os.path.exists(os.path.join(static_path, "assets")):
        app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets")), name="static")

    @app.exception_handler(StarletteHTTPException)
    async def spa_exception_handler(request: Request, exc: StarletteHTTPException):
        # For API routes, return JSON errors as-is
        if request.url.path.startswith("/api") or request.url.path.startswith("/ws"):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )

        # For 404 on non-API routes, serve SPA index.html
        if exc.status_code == 404:
            # Check if the requested file exists as a static file
            clean_path = request.url.path.lstrip("/")
            file_path = os.path.join(static_path, clean_path)
            if clean_path and os.path.isfile(file_path):
                return FileResponse(file_path)

            index_path = os.path.join(static_path, "index.html")
            if os.path.isfile(index_path):
                return FileResponse(index_path)

        # For all other HTTP errors on non-API routes, return JSON
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # Serve index.html at root
    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(static_path, "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "DnD Lite GM API", "docs": "/docs", "frontend": "Not built yet. Use npm run build in frontend folder."}
