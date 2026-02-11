from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Combat(Base):
    __tablename__ = "combats"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    round_number = Column(Integer, default=1)
    current_turn_id = Column(Integer, ForeignKey("combat_participants.id"), nullable=True)

    session = relationship("Session", back_populates="combats")
    participants = relationship(
        "CombatParticipant",
        back_populates="combat",
        foreign_keys="CombatParticipant.combat_id",
        cascade="all, delete-orphan"
    )
    initiative_rolls = relationship(
        "InitiativeRoll",
        back_populates="combat",
        cascade="all, delete-orphan"
    )


class CombatParticipant(Base):
    __tablename__ = "combat_participants"

    id = Column(Integer, primary_key=True, index=True)
    combat_id = Column(Integer, ForeignKey("combats.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    initiative = Column(Integer, default=0)
    current_hp = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    combat = relationship("Combat", back_populates="participants", foreign_keys=[combat_id])
    character = relationship("Character", back_populates="combat_participations")


class InitiativeRoll(Base):
    """Stores individual initiative rolls for players and NPCs in combat.

    For player initiative: player_id is set, character_id is None
    For NPC initiative: character_id is set, player_id is None
    """
    __tablename__ = "initiative_rolls"

    id = Column(Integer, primary_key=True, index=True)
    combat_id = Column(Integer, ForeignKey("combats.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=True)
    roll = Column(Integer, nullable=False)
    rolled_at = Column(DateTime, default=datetime.utcnow)

    combat = relationship("Combat", back_populates="initiative_rolls")
    player = relationship("Player")
    character = relationship("Character")

