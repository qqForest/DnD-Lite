from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base

class Map(Base):
    __tablename__ = "maps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    name = Column(String, nullable=False)
    background_url = Column(String, nullable=True)
    width = Column(Integer, default=1920)
    height = Column(Integer, default=1080)
    grid_scale = Column(Integer, default=50) # pixels per grid cell
    is_active = Column(Boolean, default=False)

    session = relationship("Session", back_populates="maps")
    tokens = relationship("MapToken", back_populates="map", cascade="all, delete-orphan")

class MapToken(Base):
    __tablename__ = "map_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    map_id = Column(String(36), ForeignKey("maps.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True) # If linked to a character
    type = Column(String, default="character") # character, monster, prop
    
    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    scale = Column(Float, default=1.0)
    rotation = Column(Float, default=0.0)
    
    # Optional metadata (colors, labels for non-character tokens)
    label = Column(String, nullable=True)
    color = Column(String, default="#red")
    icon = Column(String, nullable=True)  # ключ иконки из каталога, например "chest"

    # Layer: "tokens", "background", "hidden"
    layer = Column(String, default="tokens")

    map = relationship("Map", back_populates="tokens")
    character = relationship("Character")
