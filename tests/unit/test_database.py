import pytest
from datetime import datetime, timedelta
from app.models.session import Session
from app.models.player import Player
from app.database import cleanup_old_sessions


@pytest.mark.asyncio
class TestCleanupSessions:
    async def test_deletes_old_sessions(self, db):
        """Sessions older than cutoff are deleted"""
        # Create old session (10 days ago)
        old_date = datetime.utcnow() - timedelta(days=10)
        old_session = Session(
            code="OLD123",
            gm_token="old-token",
            created_at=old_date,
            is_active=True
        )
        db.add(old_session)
        db.commit()
        db.refresh(old_session)

        # Run cleanup (days=7)
        count = cleanup_old_sessions(db, days=7)

        # Verify deleted
        assert count == 1
        session = db.query(Session).filter(Session.code == "OLD123").first()
        assert session is None

    async def test_keeps_recent_sessions(self, db):
        """Recent sessions are not deleted"""
        # Create recent session (3 days ago)
        recent_date = datetime.utcnow() - timedelta(days=3)
        recent_session = Session(
            code="NEW123",
            gm_token="new-token",
            created_at=recent_date,
            is_active=True
        )
        db.add(recent_session)
        db.commit()
        db.refresh(recent_session)
        session_id = recent_session.id

        # Run cleanup (days=7)
        count = cleanup_old_sessions(db, days=7)

        # Verify still exists
        assert count == 0
        session = db.query(Session).filter(Session.id == session_id).first()
        assert session is not None

    async def test_skips_sessions_with_active_connections(self, db):
        """Old sessions with active WebSocket connections are not deleted"""
        from unittest.mock import patch

        # Create old session
        old_date = datetime.utcnow() - timedelta(days=10)
        old_session = Session(
            code="ACT123",
            gm_token="active-token",
            created_at=old_date,
            is_active=True
        )
        db.add(old_session)
        db.commit()
        db.refresh(old_session)

        # Add player
        player = Player(
            session_id=old_session.id,
            name="ActiveGM",
            token="player-token",
            is_gm=True
        )
        db.add(player)
        db.commit()

        # Mock manager to return active connection
        with patch("app.websocket.manager.manager.get_player_id") as mock_get_player:
            mock_get_player.return_value = player.id
            count = cleanup_old_sessions(db, days=7)

        # Verify NOT deleted (active connection)
        assert count == 0
        session = db.query(Session).filter(Session.code == "ACT123").first()
        assert session is not None

    async def test_deletes_multiple_old_sessions(self, db):
        """Multiple old sessions are deleted in one cleanup"""
        old_date = datetime.utcnow() - timedelta(days=10)

        for i in range(3):
            session = Session(
                code=f"OLD{i}",
                gm_token=f"token-{i}",
                created_at=old_date,
                is_active=True
            )
            db.add(session)
        db.commit()

        # Run cleanup
        count = cleanup_old_sessions(db, days=7)

        # Verify all deleted
        assert count == 3
        sessions = db.query(Session).filter(Session.code.like("OLD%")).all()
        assert len(sessions) == 0
