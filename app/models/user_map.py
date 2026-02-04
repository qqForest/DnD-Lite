import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
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
