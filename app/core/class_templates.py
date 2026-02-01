"""Шаблоны классов D&D 5e для быстрого создания персонажей."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class DiceType(str, Enum):
    """Типы костей для hit dice."""
    D6 = "d6"
    D8 = "d8"
    D10 = "d10"
    D12 = "d12"


@dataclass
class StartingItem:
    """Стартовый предмет для шаблона."""
    name: str
    description: Optional[str] = None
    effects: Optional[Dict[str, Any]] = None
    is_equipped: bool = False


@dataclass
class StartingSpell:
    """Стартовое заклинание для шаблона."""
    name: str
    level: int = 0  # 0 = cantrip
    description: Optional[str] = None
    damage_dice: Optional[str] = None


@dataclass
class ClassTemplate:
    """Шаблон класса персонажа."""
    id: str
    name: str
    name_ru: str
    description: str
    description_ru: str
    hit_die: DiceType
    primary_abilities: List[str]
    # Рекомендуемые характеристики для 1 уровня (standard array style)
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    # Стартовое снаряжение и заклинания
    starting_items: List[StartingItem] = field(default_factory=list)
    starting_spells: List[StartingSpell] = field(default_factory=list)

    def calculate_hp(self, level: int = 1) -> int:
        """Рассчитать HP для уровня."""
        from app.core.abilities import calculate_modifier
        con_mod = calculate_modifier(self.constitution)
        die_values = {"d6": 6, "d8": 8, "d10": 10, "d12": 12}
        max_die = die_values[self.hit_die.value]
        # Первый уровень - максимум, дальше среднее
        if level == 1:
            return max_die + con_mod
        avg_roll = (max_die // 2) + 1
        return max_die + con_mod + (level - 1) * (avg_roll + con_mod)


# === ШАБЛОНЫ КЛАССОВ ===

FIGHTER = ClassTemplate(
    id="fighter",
    name="Fighter",
    name_ru="Воин",
    description="A master of martial combat, skilled with a variety of weapons and armor.",
    description_ru="Мастер боевых искусств, владеющий разнообразным оружием и доспехами.",
    hit_die=DiceType.D10,
    primary_abilities=["strength", "constitution"],
    strength=16,
    dexterity=12,
    constitution=14,
    intelligence=10,
    wisdom=12,
    charisma=8,
    starting_items=[
        StartingItem(
            name="Longsword",
            description="Versatile martial weapon",
            effects={"damage": "1d8"},
            is_equipped=True
        ),
        StartingItem(
            name="Chain Mail",
            description="Heavy armor, AC 16",
            effects={"ac_bonus": 16},
            is_equipped=True
        ),
        StartingItem(
            name="Shield",
            description="+2 AC",
            effects={"ac_bonus": 2},
            is_equipped=True
        ),
    ],
)

WIZARD = ClassTemplate(
    id="wizard",
    name="Wizard",
    name_ru="Волшебник",
    description="A scholarly magic-user capable of manipulating the structures of reality.",
    description_ru="Учёный маг, способный изменять структуру реальности.",
    hit_die=DiceType.D6,
    primary_abilities=["intelligence", "constitution"],
    strength=8,
    dexterity=14,
    constitution=14,
    intelligence=16,
    wisdom=12,
    charisma=10,
    starting_items=[
        StartingItem(
            name="Quarterstaff",
            description="Simple melee weapon",
            effects={"damage": "1d6"},
            is_equipped=True
        ),
        StartingItem(
            name="Spellbook",
            description="Contains your wizard spells",
        ),
        StartingItem(
            name="Arcane Focus",
            description="Crystal orb for casting spells",
        ),
    ],
    starting_spells=[
        StartingSpell(name="Fire Bolt", level=0, damage_dice="1d10",
                     description="Ranged fire attack"),
        StartingSpell(name="Mage Hand", level=0,
                     description="Spectral hand for manipulation"),
        StartingSpell(name="Magic Missile", level=1, damage_dice="3d4+3",
                     description="Automatic hit force damage"),
        StartingSpell(name="Shield", level=1,
                     description="+5 AC as reaction"),
    ],
)

ROGUE = ClassTemplate(
    id="rogue",
    name="Rogue",
    name_ru="Плут",
    description="A scoundrel who uses stealth and trickery to overcome obstacles.",
    description_ru="Хитрец, использующий скрытность и обман для достижения целей.",
    hit_die=DiceType.D8,
    primary_abilities=["dexterity", "intelligence"],
    strength=10,
    dexterity=16,
    constitution=12,
    intelligence=14,
    wisdom=12,
    charisma=10,
    starting_items=[
        StartingItem(
            name="Shortsword",
            description="Finesse weapon",
            effects={"damage": "1d6"},
            is_equipped=True
        ),
        StartingItem(
            name="Shortbow",
            description="Ranged weapon",
            effects={"damage": "1d6", "range": "80/320"},
        ),
        StartingItem(
            name="Leather Armor",
            description="Light armor, AC 11 + Dex",
            effects={"ac_bonus": 11},
            is_equipped=True
        ),
        StartingItem(
            name="Thieves' Tools",
            description="For picking locks and disabling traps",
        ),
    ],
)

CLERIC = ClassTemplate(
    id="cleric",
    name="Cleric",
    name_ru="Жрец",
    description="A priestly champion who wields divine magic in service of a higher power.",
    description_ru="Священный воитель, использующий божественную магию.",
    hit_die=DiceType.D8,
    primary_abilities=["wisdom", "constitution"],
    strength=14,
    dexterity=10,
    constitution=14,
    intelligence=10,
    wisdom=16,
    charisma=12,
    starting_items=[
        StartingItem(
            name="Mace",
            description="Simple melee weapon",
            effects={"damage": "1d6"},
            is_equipped=True
        ),
        StartingItem(
            name="Scale Mail",
            description="Medium armor, AC 14 + Dex (max 2)",
            effects={"ac_bonus": 14},
            is_equipped=True
        ),
        StartingItem(
            name="Shield",
            description="+2 AC",
            effects={"ac_bonus": 2},
            is_equipped=True
        ),
        StartingItem(
            name="Holy Symbol",
            description="Divine focus for spellcasting",
        ),
    ],
    starting_spells=[
        StartingSpell(name="Sacred Flame", level=0, damage_dice="1d8",
                     description="Radiant damage, Dex save"),
        StartingSpell(name="Guidance", level=0,
                     description="+1d4 to one ability check"),
        StartingSpell(name="Cure Wounds", level=1, damage_dice="1d8",
                     description="Heal 1d8 + Wis modifier"),
        StartingSpell(name="Bless", level=1,
                     description="+1d4 to attacks and saves for allies"),
    ],
)

BARBARIAN = ClassTemplate(
    id="barbarian",
    name="Barbarian",
    name_ru="Варвар",
    description="A fierce warrior who can enter a battle rage.",
    description_ru="Свирепый воин, способный впадать в боевую ярость.",
    hit_die=DiceType.D12,
    primary_abilities=["strength", "constitution"],
    strength=16,
    dexterity=14,
    constitution=16,
    intelligence=8,
    wisdom=10,
    charisma=10,
    starting_items=[
        StartingItem(
            name="Greataxe",
            description="Heavy two-handed weapon",
            effects={"damage": "1d12"},
            is_equipped=True
        ),
        StartingItem(
            name="Handaxe",
            description="Light throwing weapon",
            effects={"damage": "1d6", "range": "20/60"},
        ),
        StartingItem(
            name="Explorer's Pack",
            description="Adventuring supplies",
        ),
    ],
)

RANGER = ClassTemplate(
    id="ranger",
    name="Ranger",
    name_ru="Следопыт",
    description="A warrior who combats threats on the edges of civilization.",
    description_ru="Воин, сражающийся с угрозами на границах цивилизации.",
    hit_die=DiceType.D10,
    primary_abilities=["dexterity", "wisdom"],
    strength=12,
    dexterity=16,
    constitution=14,
    intelligence=10,
    wisdom=14,
    charisma=8,
    starting_items=[
        StartingItem(
            name="Longbow",
            description="Martial ranged weapon",
            effects={"damage": "1d8", "range": "150/600"},
            is_equipped=True
        ),
        StartingItem(
            name="Shortsword",
            description="Finesse weapon",
            effects={"damage": "1d6"},
        ),
        StartingItem(
            name="Scale Mail",
            description="Medium armor, AC 14 + Dex (max 2)",
            effects={"ac_bonus": 14},
            is_equipped=True
        ),
    ],
)

PALADIN = ClassTemplate(
    id="paladin",
    name="Paladin",
    name_ru="Паладин",
    description="A holy warrior bound to a sacred oath.",
    description_ru="Священный воин, связанный священной клятвой.",
    hit_die=DiceType.D10,
    primary_abilities=["strength", "charisma"],
    strength=16,
    dexterity=10,
    constitution=14,
    intelligence=8,
    wisdom=10,
    charisma=14,
    starting_items=[
        StartingItem(
            name="Longsword",
            description="Versatile martial weapon",
            effects={"damage": "1d8"},
            is_equipped=True
        ),
        StartingItem(
            name="Chain Mail",
            description="Heavy armor, AC 16",
            effects={"ac_bonus": 16},
            is_equipped=True
        ),
        StartingItem(
            name="Shield",
            description="+2 AC",
            effects={"ac_bonus": 2},
            is_equipped=True
        ),
        StartingItem(
            name="Holy Symbol",
            description="Divine focus",
        ),
    ],
    starting_spells=[
        StartingSpell(name="Divine Sense", level=0,
                     description="Detect celestials, fiends, undead"),
        StartingSpell(name="Lay on Hands", level=0,
                     description="Heal pool equal to Paladin level x 5"),
    ],
)

BARD = ClassTemplate(
    id="bard",
    name="Bard",
    name_ru="Бард",
    description="An inspiring magician whose power echoes the music of creation.",
    description_ru="Вдохновляющий маг, чья сила отражает музыку творения.",
    hit_die=DiceType.D8,
    primary_abilities=["charisma", "dexterity"],
    strength=8,
    dexterity=14,
    constitution=12,
    intelligence=12,
    wisdom=10,
    charisma=16,
    starting_items=[
        StartingItem(
            name="Rapier",
            description="Finesse martial weapon",
            effects={"damage": "1d8"},
            is_equipped=True
        ),
        StartingItem(
            name="Leather Armor",
            description="Light armor, AC 11 + Dex",
            effects={"ac_bonus": 11},
            is_equipped=True
        ),
        StartingItem(
            name="Lute",
            description="Musical instrument, spellcasting focus",
        ),
    ],
    starting_spells=[
        StartingSpell(name="Vicious Mockery", level=0, damage_dice="1d4",
                     description="Psychic damage and disadvantage"),
        StartingSpell(name="Minor Illusion", level=0,
                     description="Create a sound or image"),
        StartingSpell(name="Healing Word", level=1, damage_dice="1d4",
                     description="Bonus action heal at range"),
        StartingSpell(name="Dissonant Whispers", level=1, damage_dice="3d6",
                     description="Psychic damage, target flees"),
    ],
)

DRUID = ClassTemplate(
    id="druid",
    name="Druid",
    name_ru="Друид",
    description="A priest of the Old Faith, wielding the powers of nature.",
    description_ru="Жрец Старой Веры, владеющий силами природы.",
    hit_die=DiceType.D8,
    primary_abilities=["wisdom", "constitution"],
    strength=10,
    dexterity=12,
    constitution=14,
    intelligence=12,
    wisdom=16,
    charisma=10,
    starting_items=[
        StartingItem(
            name="Quarterstaff",
            description="Simple melee weapon",
            effects={"damage": "1d6"},
            is_equipped=True
        ),
        StartingItem(
            name="Leather Armor",
            description="Light armor (druids won't wear metal)",
            effects={"ac_bonus": 11},
            is_equipped=True
        ),
        StartingItem(
            name="Druidic Focus",
            description="Wooden staff or mistletoe",
        ),
    ],
    starting_spells=[
        StartingSpell(name="Produce Flame", level=0, damage_dice="1d8",
                     description="Fire attack or light source"),
        StartingSpell(name="Druidcraft", level=0,
                     description="Minor nature effects"),
        StartingSpell(name="Entangle", level=1,
                     description="Restrain creatures in area"),
        StartingSpell(name="Healing Word", level=1, damage_dice="1d4",
                     description="Bonus action heal at range"),
    ],
)

MONK = ClassTemplate(
    id="monk",
    name="Monk",
    name_ru="Монах",
    description="A master of martial arts, harnessing the power of body and soul.",
    description_ru="Мастер боевых искусств, использующий силу тела и духа.",
    hit_die=DiceType.D8,
    primary_abilities=["dexterity", "wisdom"],
    strength=10,
    dexterity=16,
    constitution=14,
    intelligence=10,
    wisdom=16,
    charisma=8,
    starting_items=[
        StartingItem(
            name="Shortsword",
            description="Monk weapon",
            effects={"damage": "1d6"},
            is_equipped=True
        ),
        StartingItem(
            name="Dart",
            description="Simple ranged weapon (10)",
            effects={"damage": "1d4", "range": "20/60"},
        ),
    ],
)

SORCERER = ClassTemplate(
    id="sorcerer",
    name="Sorcerer",
    name_ru="Чародей",
    description="A spellcaster who draws on inherent magic from a gift or bloodline.",
    description_ru="Заклинатель с врождённой магией, даром или наследием.",
    hit_die=DiceType.D6,
    primary_abilities=["charisma", "constitution"],
    strength=8,
    dexterity=14,
    constitution=14,
    intelligence=10,
    wisdom=12,
    charisma=16,
    starting_items=[
        StartingItem(
            name="Light Crossbow",
            description="Simple ranged weapon",
            effects={"damage": "1d8", "range": "80/320"},
            is_equipped=True
        ),
        StartingItem(
            name="Arcane Focus",
            description="Crystal or orb for spellcasting",
        ),
        StartingItem(
            name="Dagger",
            description="Simple melee weapon",
            effects={"damage": "1d4"},
        ),
    ],
    starting_spells=[
        StartingSpell(name="Fire Bolt", level=0, damage_dice="1d10",
                     description="Ranged fire attack"),
        StartingSpell(name="Ray of Frost", level=0, damage_dice="1d8",
                     description="Cold damage, reduce speed"),
        StartingSpell(name="Burning Hands", level=1, damage_dice="3d6",
                     description="Cone of fire"),
        StartingSpell(name="Chromatic Orb", level=1, damage_dice="3d8",
                     description="Choose damage type"),
    ],
)

WARLOCK = ClassTemplate(
    id="warlock",
    name="Warlock",
    name_ru="Колдун",
    description="A wielder of magic derived from a bargain with an extraplanar entity.",
    description_ru="Маг, получивший силу через сделку с потусторонней сущностью.",
    hit_die=DiceType.D8,
    primary_abilities=["charisma", "constitution"],
    strength=8,
    dexterity=14,
    constitution=14,
    intelligence=12,
    wisdom=10,
    charisma=16,
    starting_items=[
        StartingItem(
            name="Light Crossbow",
            description="Simple ranged weapon",
            effects={"damage": "1d8", "range": "80/320"},
            is_equipped=True
        ),
        StartingItem(
            name="Arcane Focus",
            description="Rod, staff, or amulet",
        ),
        StartingItem(
            name="Leather Armor",
            description="Light armor",
            effects={"ac_bonus": 11},
            is_equipped=True
        ),
    ],
    starting_spells=[
        StartingSpell(name="Eldritch Blast", level=0, damage_dice="1d10",
                     description="Signature warlock cantrip"),
        StartingSpell(name="Minor Illusion", level=0,
                     description="Create a sound or image"),
        StartingSpell(name="Hex", level=1, damage_dice="1d6",
                     description="Bonus damage and ability penalty"),
        StartingSpell(name="Armor of Agathys", level=1,
                     description="Temp HP and cold damage to attackers"),
    ],
)


# Реестр всех шаблонов
CLASS_TEMPLATES: Dict[str, ClassTemplate] = {
    "fighter": FIGHTER,
    "wizard": WIZARD,
    "rogue": ROGUE,
    "cleric": CLERIC,
    "barbarian": BARBARIAN,
    "ranger": RANGER,
    "paladin": PALADIN,
    "bard": BARD,
    "druid": DRUID,
    "monk": MONK,
    "sorcerer": SORCERER,
    "warlock": WARLOCK,
}


def get_template(template_id: str) -> Optional[ClassTemplate]:
    """Получить шаблон по ID."""
    return CLASS_TEMPLATES.get(template_id.lower())


def list_templates() -> List[ClassTemplate]:
    """Получить список всех шаблонов."""
    return list(CLASS_TEMPLATES.values())
