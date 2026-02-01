from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    effects = Column(JSON, nullable=True)  # {"str_bonus": 2, "ac_bonus": 1}
    is_equipped = Column(Boolean, default=False)

    character = relationship("Character", back_populates="items")
