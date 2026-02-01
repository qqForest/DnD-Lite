from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    name = Column(String(100), nullable=False)
    token = Column(String(36), unique=True, nullable=False)
    is_gm = Column(Boolean, default=False)
    is_ready = Column(Boolean, default=False)

    session = relationship("Session", back_populates="players")
    characters = relationship("Character", back_populates="player", cascade="all, delete-orphan")
