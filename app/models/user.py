from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default="player")  # "player", "gm", "both"
    created_at = Column(DateTime, default=datetime.utcnow)

    user_characters = relationship("UserCharacter", back_populates="user", cascade="all, delete-orphan")
    user_maps = relationship("UserMap", back_populates="user", cascade="all, delete-orphan")
