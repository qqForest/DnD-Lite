from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # SQLite specific
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def cleanup_old_sessions(db, days: int = 7) -> int:
    """
    Delete sessions older than N days without active connections.
    Returns count of deleted sessions.
    """
    from datetime import datetime, timedelta
    from app.models.session import Session
    from app.websocket.manager import manager
    import logging

    logger = logging.getLogger(__name__)

    cutoff = datetime.utcnow() - timedelta(days=days)
    old_sessions = db.query(Session).filter(Session.created_at < cutoff).all()

    if not old_sessions:
        return 0

    count = 0
    for session in old_sessions:
        # Skip if has active WebSocket connections
        has_active = False
        for player in session.players:
            if manager.get_player_id(player.token) is not None:
                has_active = True
                break

        if not has_active:
            db.delete(session)
            count += 1

    if count > 0:
        db.commit()
        logger.info(f"Cleanup: Deleted {count} old session(s)")

    return count
