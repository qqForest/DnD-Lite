import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class UserMap(Base):
    __tablename__ = "user_maps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    background_url = Column(String(500), nullable=True)
    width = Column(Integer, default=1920)
    height = Column(Integer, default=1080)
    grid_scale = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="user_maps")
    tokens = relationship("UserMapToken", back_populates="user_map", cascade="all, delete-orphan")


class UserMapToken(Base):
    __tablename__ = "user_map_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_map_id = Column(String(36), ForeignKey("user_maps.id"), nullable=False)
    type = Column(String, default="monster")
    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    scale = Column(Float, default=1.0)
    rotation = Column(Float, default=0.0)
    label = Column(String, nullable=True)
    color = Column(String, default="#D94A4A")
    icon = Column(String, nullable=True)
    layer = Column(String, default="tokens")

    user_map = relationship("UserMap", back_populates="tokens")
