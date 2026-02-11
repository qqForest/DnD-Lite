import asyncio
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.websocket.manager import ConnectionManager
from app.models.player import Player
from app.models.session import Session


@pytest.mark.asyncio
class TestGracePeriod:
    async def test_start_grace_period_creates_timer(self, db):
        """start_grace_period creates an asyncio task."""
        manager = ConnectionManager()
        token = "test-token-123"

        # Create session and player
        session = Session(code="ABC123", gm_token=token, is_active=True)
        db.add(session)
        db.flush()

        player = Player(
            session_id=session.id,
            name="TestPlayer",
            token=token,
            is_gm=False
        )
        db.add(player)
        db.commit()

        await manager.start_grace_period(token)

        # Timer should be created
        assert token in manager._grace_timers
        assert isinstance(manager._grace_timers[token], asyncio.Task)

        # Cleanup
        await manager.cancel_grace_period(token)

    async def test_cancel_grace_period_removes_timer(self, db):
        """cancel_grace_period stops and removes the timer."""
        manager = ConnectionManager()
        token = "test-token-456"

        # Create session and player
        session = Session(code="DEF456", gm_token=token, is_active=True)
        db.add(session)
        db.flush()

        player = Player(
            session_id=session.id,
            name="TestPlayer",
            token=token,
            is_gm=False
        )
        db.add(player)
        db.commit()

        await manager.start_grace_period(token)
        assert token in manager._grace_timers

        await manager.cancel_grace_period(token)
        assert token not in manager._grace_timers

    async def test_grace_period_marks_player_as_left_after_timeout(self, db):
        """After grace period expires, player.left_at is set."""
        manager = ConnectionManager()
        manager._grace_period = 0.1  # 100ms for testing
        token = "test-token-789"

        # Create session and player
        session = Session(code="GHI789", gm_token=token, is_active=True)
        db.add(session)
        db.flush()

        player = Player(
            session_id=session.id,
            name="TestPlayer",
            token=token,
            is_gm=False,
            left_at=None
        )
        db.add(player)
        db.commit()

        # Mock get_db in app.database module (where it's imported from)
        def fake_get_db():
            yield db

        with patch("app.database.get_db", fake_get_db):
            await manager.start_grace_period(token)

            # Wait for grace period to expire
            await asyncio.sleep(0.2)

        # Player should be marked as left (query fresh from DB)
        updated_player = db.query(Player).filter(Player.token == token).first()
        assert updated_player is not None
        assert updated_player.left_at is not None

    async def test_reconnect_cancels_grace_period(self, db):
        """Connecting cancels grace period."""
        from fastapi import WebSocket
        from unittest.mock import AsyncMock

        manager = ConnectionManager()
        manager._grace_period = 0.1
        token = "test-token-reconnect"

        # Create session and player
        session = Session(code="REC001", gm_token=token, is_active=True)
        db.add(session)
        db.flush()

        player = Player(
            session_id=session.id,
            name="TestPlayer",
            token=token,
            is_gm=False,
            left_at=None
        )
        db.add(player)
        db.commit()

        await manager.start_grace_period(token)
        assert token in manager._grace_timers

        # Mock WebSocket
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.accept = AsyncMock()

        # Reconnect should cancel grace period
        await manager.connect(mock_ws, token, player.id)

        # Grace period should be cancelled
        assert token not in manager._grace_timers

        # Player should still be active (query fresh from DB)
        updated_player = db.query(Player).filter(Player.token == token).first()
        assert updated_player is not None
        assert updated_player.left_at is None

    async def test_multiple_start_grace_period_cancels_previous(self, db):
        """Starting grace period twice cancels the first timer."""
        manager = ConnectionManager()
        manager._grace_period = 1.0
        token = "test-token-multi"

        # Create session and player
        session = Session(code="MUL001", gm_token=token, is_active=True)
        db.add(session)
        db.flush()

        player = Player(
            session_id=session.id,
            name="TestPlayer",
            token=token,
            is_gm=False
        )
        db.add(player)
        db.commit()

        await manager.start_grace_period(token)
        first_task = manager._grace_timers[token]

        await manager.start_grace_period(token)
        second_task = manager._grace_timers[token]

        # Second task should be different
        assert first_task is not second_task
        # First task should be cancelled
        assert first_task.cancelled()

        # Cleanup
        await manager.cancel_grace_period(token)
