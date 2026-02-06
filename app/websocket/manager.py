import asyncio
import logging
from typing import Dict, Optional

from fastapi import WebSocket
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Map: player_token -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Map: player_token -> player_id
        self.token_to_player: Dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, token: str, player_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            # Handle reconnect: close old socket if token already exists
            old_ws = self.active_connections.get(token)
            if old_ws is not None:
                logger.info(f"Reconnect detected for player {player_id}, closing old socket")
                try:
                    await old_ws.close(code=4000, reason="Reconnected from another client")
                except Exception:
                    pass
            self.active_connections[token] = websocket
            self.token_to_player[token] = player_id
        logger.info(f"Connected player {player_id} with token {token[:8]}...")

    async def disconnect(self, token: str):
        """Remove a WebSocket connection."""
        async with self._lock:
            player_id = self.token_to_player.get(token)
            self.active_connections.pop(token, None)
            self.token_to_player.pop(token, None)
        logger.info(f"Disconnected player {player_id} with token {token[:8]}...")

    def get_player_id(self, token: str) -> Optional[int]:
        """Get player_id from token."""
        return self.token_to_player.get(token)

    def _is_connected(self, websocket: WebSocket) -> bool:
        """Check if a WebSocket is still in CONNECTED state."""
        try:
            return websocket.client_state == WebSocketState.CONNECTED
        except Exception:
            return False

    async def _remove_dead(self, token: str):
        """Remove a single dead connection under lock."""
        async with self._lock:
            self.active_connections.pop(token, None)
            self.token_to_player.pop(token, None)
        logger.warning(f"Removed dead connection for token {token[:8]}...")

    async def _remove_dead_batch(self, tokens: list):
        """Remove multiple dead connections under lock."""
        if not tokens:
            return
        async with self._lock:
            for token in tokens:
                self.active_connections.pop(token, None)
                self.token_to_player.pop(token, None)
        logger.warning(f"Removed {len(tokens)} dead connection(s)")

    async def send_personal(self, token: str, data: dict):
        """Send message to a specific player."""
        websocket = self.active_connections.get(token)
        if websocket and self._is_connected(websocket):
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to {token[:8]}...: {e}")
                await self._remove_dead(token)

    async def broadcast(self, data: dict, exclude_token: Optional[str] = None):
        """Send message to all connected players."""
        # Snapshot connections under lock
        async with self._lock:
            connections = list(self.active_connections.items())

        dead_tokens = []
        for token, websocket in connections:
            if exclude_token and token == exclude_token:
                continue
            if not self._is_connected(websocket):
                dead_tokens.append(token)
                continue
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Broadcast error for {token[:8]}...: {e}")
                dead_tokens.append(token)

        await self._remove_dead_batch(dead_tokens)

    async def broadcast_event(
        self,
        event_type: str,
        payload: dict,
        exclude_token: Optional[str] = None
    ):
        """Broadcast an event with type and payload."""
        await self.broadcast(
            {"type": event_type, "payload": payload},
            exclude_token=exclude_token
        )


# Global connection manager instance
manager = ConnectionManager()
