from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    name = Column(String(100), nullable=False)
    class_name = Column(String(50), nullable=True)
    level = Column(Integer, default=1)

    # Ability scores
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)

    # Hit points
    max_hp = Column(Integer, default=10)
    current_hp = Column(Integer, default=10)

    player = relationship("Player", back_populates="characters")
    items = relationship("Item", back_populates="character", cascade="all, delete-orphan")
    spells = relationship("Spell", back_populates="character", cascade="all, delete-orphan")
    combat_participations = relationship("CombatParticipant", back_populates="character")
    map_tokens = relationship("MapToken", back_populates="character", cascade="all, delete-orphan")
