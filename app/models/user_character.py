from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class UserCharacter(Base):
    __tablename__ = "user_characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    class_name = Column(String(50), nullable=True)
    level = Column(Integer, default=1)
    is_npc = Column(Boolean, default=False)

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

    # Armor Class
    armor_class = Column(Integer, default=10)

    # Appearance & Avatar
    appearance = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)

    # Stats
    sessions_played = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="user_characters")
