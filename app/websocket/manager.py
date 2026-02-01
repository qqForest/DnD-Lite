from typing import Dict, Optional
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        # Map: player_token -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Map: player_token -> player_id
        self.token_to_player: Dict[str, int] = {}

    async def connect(self, websocket: WebSocket, token: str, player_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[token] = websocket
        self.token_to_player[token] = player_id
        print(f"Manager: Connected player {player_id} with token {token[:8]}...")

    def disconnect(self, token: str):
        """Remove a WebSocket connection."""
        player_id = self.token_to_player.get(token)
        self.active_connections.pop(token, None)
        self.token_to_player.pop(token, None)
        print(f"Manager: Disconnected player {player_id} with token {token[:8]}...")

    def get_player_id(self, token: str) -> Optional[int]:
        """Get player_id from token."""
        return self.token_to_player.get(token)

    async def send_personal(self, token: str, data: dict):
        """Send message to a specific player."""
        websocket = self.active_connections.get(token)
        if websocket:
            await websocket.send_json(data)

    async def broadcast(self, data: dict, exclude_token: Optional[str] = None):
        """Send message to all connected players."""
        for token, websocket in self.active_connections.items():
            if exclude_token and token == exclude_token:
                continue
            try:
                await websocket.send_json(data)
            except Exception:
                pass  # Connection might be closed

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
