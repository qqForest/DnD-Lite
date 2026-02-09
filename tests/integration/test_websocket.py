import json
import uuid
import pytest
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient

from app.database import get_db
from app.models.session import Session
from app.models.player import Player


def _setup_ws_player(db):
    """Create session + player in DB for WebSocket testing."""
    token = str(uuid.uuid4())
    code = uuid.uuid4().hex[:6].upper()
    session = Session(code=code, gm_token=token, is_active=True)
    db.add(session)
    db.flush()

    player = Player(
        session_id=session.id,
        name="WSPlayer",
        token=token,
        is_gm=True,
    )
    db.add(player)
    db.flush()
    return session, player, token


@pytest.fixture()
def ws_client(db):
    """TestClient with get_db patched at module level in app.main.

    The WS endpoint calls next(get_db()) directly (not via DI),
    so dependency_overrides won't work. We patch the imported name instead.
    We also neuter db.close() so the test session stays open.
    """
    from app.main import app

    original_close = db.close

    def fake_get_db():
        yield db

    # Prevent the WS endpoint from closing our shared test session
    db.close = lambda: None

    with patch("app.main.get_db", fake_get_db):
        client = TestClient(app)
        yield client, db

    db.close = original_close


class TestWebSocketConnection:
    def test_connect_with_valid_token(self, ws_client):
        client, db = ws_client
        _, _, token = _setup_ws_player(db)

        with client.websocket_connect(f"/ws?token={token}") as ws:
            # Should receive a ping eventually or be able to send
            ws.send_json({"type": "pong"})
            # Connection accepted successfully

    def test_reject_no_token(self, ws_client):
        client, db = ws_client
        try:
            with client.websocket_connect("/ws") as ws:
                pytest.fail("Should have been rejected")
        except Exception:
            pass  # Expected: connection closed

    def test_reject_invalid_token(self, ws_client):
        client, db = ws_client
        try:
            with client.websocket_connect("/ws?token=invalid-token") as ws:
                pytest.fail("Should have been rejected")
        except Exception:
            pass  # Expected: connection closed


class TestWebSocketRollDice:
    def test_roll_dice(self, ws_client):
        client, db = ws_client
        _, _, token = _setup_ws_player(db)

        with client.websocket_connect(f"/ws?token={token}") as ws:
            ws.send_json({
                "type": "roll_dice",
                "payload": {"dice": "1d20", "reason": "Test roll"}
            })
            data = ws.receive_json()
            assert data["type"] == "dice_result"
            assert data["payload"]["dice"] == "1d20"
            assert 1 <= data["payload"]["total"] <= 20

    def test_roll_dice_invalid(self, ws_client):
        client, db = ws_client
        _, _, token = _setup_ws_player(db)

        with client.websocket_connect(f"/ws?token={token}") as ws:
            ws.send_json({
                "type": "roll_dice",
                "payload": {"dice": "invalid"}
            })
            data = ws.receive_json()
            assert data["type"] == "error"


class TestWebSocketChat:
    def test_chat_message(self, ws_client):
        client, db = ws_client
        _, _, token = _setup_ws_player(db)

        with client.websocket_connect(f"/ws?token={token}") as ws:
            ws.send_json({
                "type": "chat",
                "payload": {"message": "Hello world"}
            })
            data = ws.receive_json()
            assert data["type"] == "chat"
            assert data["payload"]["message"] == "Hello world"
            assert data["payload"]["player_name"] == "WSPlayer"

    def test_empty_chat_ignored(self, ws_client):
        client, db = ws_client
        _, _, token = _setup_ws_player(db)

        with client.websocket_connect(f"/ws?token={token}") as ws:
            ws.send_json({
                "type": "chat",
                "payload": {"message": ""}
            })
            # Empty message should be ignored - send another to verify
            ws.send_json({
                "type": "chat",
                "payload": {"message": "Real message"}
            })
            data = ws.receive_json()
            assert data["type"] == "chat"
            assert data["payload"]["message"] == "Real message"


class TestWebSocketErrors:
    def test_invalid_json(self, ws_client):
        client, db = ws_client
        _, _, token = _setup_ws_player(db)

        with client.websocket_connect(f"/ws?token={token}") as ws:
            ws.send_text("not json at all")
            data = ws.receive_json()
            assert data["type"] == "error"
            assert "Invalid JSON" in data["payload"]["message"]

    def test_unknown_message_type(self, ws_client):
        client, db = ws_client
        _, _, token = _setup_ws_player(db)

        with client.websocket_connect(f"/ws?token={token}") as ws:
            ws.send_json({"type": "nonexistent_type"})
            # Unknown type is silently ignored (just logged)
            # Send a valid message to confirm connection still works
            ws.send_json({
                "type": "chat",
                "payload": {"message": "Still alive"}
            })
            data = ws.receive_json()
            assert data["type"] == "chat"
