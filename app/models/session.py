from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, index=True, nullable=False)
    gm_token = Column(String(36), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    session_started = Column(Boolean, default=False)

    players = relationship("Player", back_populates="session", cascade="all, delete-orphan")
    combats = relationship("Combat", back_populates="session", cascade="all, delete-orphan")
    maps = relationship("Map", back_populates="session", cascade="all, delete-orphan")
