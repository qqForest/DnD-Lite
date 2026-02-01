# Layouts

Описание лейаутов интерфейса DnD Lite GM.

## GM Layout (Desktop)

```
┌─────────────────────────────────────────────────────────────────┐
│  [≡]  DnD Lite GM           Session: ABC123    [⚙] [?] [👤]    │  ← Top Bar (48px)
├────┬────────────────────────────────────────────────────────────┤
│    │                                                            │
│ 👥 │                                                            │
│    │                                                            │
│ 📜 │                      CANVAS MAP                            │
│    │                      (full area)                           │
│ ⚔️  │                                                            │
│    │                                                            │
│ 📊 │                                                            │
│    │                                                            │
├────┴────────────────────────────────────────────────────────────┤
│  [d4] [d6] [d8] [d10] [d12] [d20] [d100]    [Custom: 2d6+3]    │  ← Bottom Bar (80px)
└─────────────────────────────────────────────────────────────────┘
     ↑
  Left Panel (48px collapsed, 240px expanded)
```

### Структура GM Layout

```
AppLayout
├── TopBar
│   ├── MenuButton (hamburger)
│   ├── Logo
│   ├── SessionInfo (code, players count)
│   └── Actions (settings, help, profile)
│
├── LeftPanel (collapsible)
│   ├── PlayersTab
│   │   ├── PlayerList
│   │   └── PlayerCard (on select)
│   ├── EventLogTab
│   │   └── EventList (dice rolls, combat, etc.)
│   ├── CombatTab
│   │   ├── InitiativeTracker
│   │   └── CombatControls
│   └── StatsTab
│       └── SessionStats
│
├── MainArea
│   └── CanvasMap
│       ├── MapLayer (background, terrain)
│       ├── TokensLayer (characters, enemies)
│       ├── EffectsLayer (spells, highlights)
│       └── UILayer (selection, grid)
│
└── BottomBar
    ├── DiceSelector
    │   └── DiceButton[] (d4, d6, d8, d10, d12, d20, d100)
    ├── CustomRollInput
    └── RollHistory (last 3 rolls)
```

### CSS Grid для GM

```css
.gm-layout {
  display: grid;
  grid-template-areas:
    "top    top"
    "left   main"
    "bottom bottom";
  grid-template-columns: var(--panel-width-sm) 1fr;
  grid-template-rows: var(--panel-height-top) 1fr var(--panel-height-bottom);
  height: 100vh;
  overflow: hidden;
}

.gm-layout.panel-expanded {
  grid-template-columns: var(--panel-width-md) 1fr;
}

.top-bar { grid-area: top; }
.left-panel { grid-area: left; }
.main-area { grid-area: main; }
.bottom-bar { grid-area: bottom; }
```

---

## Player Layout (Mobile)

```
┌─────────────────────────┐
│  Session: ABC123   [≡]  │  ← Top Bar (compact, 44px)
├─────────────────────────┤
│                         │
│                         │
│      CANVAS MAP         │
│      (main area)        │
│                         │
│                         │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │   Character Card    │ │  ← Character Sheet (swipeable)
│ │   HP: ████░░ 45/60  │ │
│ │   AC: 16  Init: +2  │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│    ← [d6] [d8] [d20] →  │  ← Dice Carousel (swipe to select)
│       ↑ swipe to roll   │
└─────────────────────────┘
```

### Структура Player Layout

```
PlayerLayout
├── TopBar (compact)
│   ├── SessionCode
│   ├── ConnectionStatus
│   └── MenuButton
│
├── MainArea
│   └── CanvasMap (same as GM but view-only tokens)
│
├── CharacterSheet (bottom sheet, draggable)
│   ├── Handle (drag indicator)
│   ├── CharacterHeader
│   │   ├── Avatar
│   │   ├── Name & Class
│   │   └── Level
│   ├── StatsBar
│   │   ├── HPBar
│   │   ├── AC
│   │   └── Initiative
│   └── QuickActions (collapsed by default)
│       ├── Items
│       ├── Spells
│       └── Abilities
│
└── DiceCarousel
    ├── DiceCard[] (swipeable)
    └── RollIndicator (swipe up gesture area)
```

### CSS для Player

```css
.player-layout {
  display: grid;
  grid-template-areas:
    "top"
    "main"
    "sheet"
    "dice";
  grid-template-rows: 44px 1fr auto 100px;
  height: 100vh;
  height: 100dvh; /* Dynamic viewport for mobile */
  overflow: hidden;
}

.character-sheet {
  grid-area: sheet;
  max-height: 40vh;
  overflow-y: auto;
  transition: max-height var(--duration-normal) var(--ease-out);
}

.character-sheet.expanded {
  max-height: 70vh;
}

.dice-carousel {
  grid-area: dice;
  touch-action: pan-x;
}
```

---

## Responsive Behavior

### GM на планшете (portrait)

```css
@media (max-width: 1024px) and (orientation: portrait) {
  .gm-layout {
    grid-template-areas:
      "top"
      "main"
      "left"
      "bottom";
    grid-template-columns: 1fr;
    grid-template-rows: 48px 1fr auto 80px;
  }

  .left-panel {
    position: fixed;
    bottom: 80px;
    left: 0;
    right: 0;
    max-height: 50vh;
    transform: translateY(100%);
    transition: transform var(--duration-normal);
  }

  .left-panel.open {
    transform: translateY(0);
  }
}
```

### Player на десктопе

На десктопе Player Layout может быть расширен:

```css
@media (min-width: 1024px) {
  .player-layout {
    grid-template-areas:
      "top    top"
      "main   sheet"
      "dice   sheet";
    grid-template-columns: 1fr 320px;
    grid-template-rows: 48px 1fr 100px;
  }

  .character-sheet {
    max-height: none;
    border-left: 1px solid var(--color-bg-elevated);
  }
}
```

---

## Панели и их состояния

### Left Panel (GM)

| Состояние | Ширина | Содержимое |
|-----------|--------|------------|
| Collapsed | 48px | Только иконки табов |
| Expanded | 240px | Иконки + текст + контент |
| Overlay (mobile) | 100% | Полноэкранное меню |

### Character Sheet (Player)

| Состояние | Высота | Триггер |
|-----------|--------|---------|
| Peek | 80px | По умолчанию (только имя и HP) |
| Half | 40vh | Tap или drag |
| Full | 70vh | Drag вверх |

### Dice Carousel (Player)

| Жест | Действие |
|------|----------|
| Swipe left/right | Выбор кубика |
| Swipe up | Бросить выбранный кубик |
| Long press | Модификатор (+1, +2, etc.) |

---

## Vue компоненты

```
src/
├── layouts/
│   ├── GMLayout.vue
│   └── PlayerLayout.vue
│
├── components/
│   ├── common/
│   │   ├── TopBar.vue
│   │   ├── BottomBar.vue
│   │   └── Panel.vue
│   │
│   ├── gm/
│   │   ├── LeftPanel.vue
│   │   ├── PlayersTab.vue
│   │   ├── EventLogTab.vue
│   │   ├── CombatTab.vue
│   │   └── InitiativeTracker.vue
│   │
│   ├── player/
│   │   ├── CharacterSheet.vue
│   │   ├── CharacterHeader.vue
│   │   ├── StatsBar.vue
│   │   └── QuickActions.vue
│   │
│   ├── dice/
│   │   ├── DiceSelector.vue
│   │   ├── DiceCarousel.vue
│   │   ├── DiceButton.vue
│   │   └── RollResult.vue
│   │
│   └── map/
│       ├── CanvasMap.vue
│       ├── MapControls.vue
│       └── TokenLayer.vue
```
