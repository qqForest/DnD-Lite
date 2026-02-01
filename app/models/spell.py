from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Spell(Base):
    __tablename__ = "spells"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    name = Column(String(100), nullable=False)
    level = Column(Integer, default=0)  # 0 = cantrip
    description = Column(String(1000), nullable=True)
    damage_dice = Column(String(20), nullable=True)  # "2d6", "1d10+4"

    character = relationship("Character", back_populates="spells")
