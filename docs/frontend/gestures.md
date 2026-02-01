# Gestures & Interactions

Спецификация жестов и взаимодействий для DnD Lite GM.

## Общие принципы

1. **Feedback обязателен** — каждое действие должно иметь визуальный/тактильный отклик
2. **Отмена жеста** — пользователь может отменить жест, вернув палец в исходную позицию
3. **Threshold** — жест срабатывает только после преодоления порога (обычно 50px)
4. **Haptic feedback** — использовать вибрацию на мобильных при ключевых действиях

---

## Dice Carousel (Player)

### Свайп влево/вправо — выбор кубика

```
   [d6]  [d8]  [d10]  [d12]  [d20]
          ←────────→
         swipe to select
```

**Параметры:**
- `threshold`: 30px
- `snapPoints`: центр каждого кубика
- `resistance`: 0.5 (сопротивление за пределами списка)
- `animation`: spring с damping

**Реализация:**

```typescript
interface DiceCarouselState {
  selectedIndex: number
  offsetX: number
  isDragging: boolean
}

const DICE_WIDTH = 72 // px
const SNAP_THRESHOLD = 30

function onTouchMove(deltaX: number) {
  state.offsetX = deltaX

  // Визуальный feedback - масштаб активного кубика
  const progress = Math.abs(deltaX) / DICE_WIDTH
  activeScale.value = 1 - progress * 0.1
}

function onTouchEnd(deltaX: number) {
  if (Math.abs(deltaX) > SNAP_THRESHOLD) {
    const direction = deltaX > 0 ? -1 : 1
    state.selectedIndex = clamp(
      state.selectedIndex + direction,
      0,
      diceTypes.length - 1
    )
  }
  // Animate to snap point
  animateToIndex(state.selectedIndex)
}
```

### Свайп вверх — бросить кубик

```
           ↑
         swipe up

     ╭─────────────╮
     │     d20     │
     ╰─────────────╯
```

**Параметры:**
- `threshold`: 50px вверх
- `velocityThreshold`: 0.5 (быстрый свайп тоже считается)
- `maxDistance`: 150px (дальше не тянется)

**Состояния:**

1. **Idle** — кубик в покое
2. **Dragging** — палец тянет вверх, кубик следует с сопротивлением
3. **Releasing** — отпустили до threshold, возврат назад
4. **Rolling** — threshold пройден, анимация броска

**Реализация:**

```typescript
const ROLL_THRESHOLD = 50
const VELOCITY_THRESHOLD = 0.5

function onVerticalDrag(deltaY: number, velocity: number) {
  // Отрицательный deltaY = движение вверх
  if (deltaY > 0) return // Игнорируем свайп вниз

  const progress = Math.min(Math.abs(deltaY) / 150, 1)

  // Визуальный feedback
  diceTransform.value = {
    translateY: deltaY * 0.6, // Сопротивление
    scale: 1 + progress * 0.2,
    rotate: progress * 15
  }

  // Подсказка "отпустите для броска"
  showRollHint.value = Math.abs(deltaY) > ROLL_THRESHOLD * 0.7
}

function onVerticalDragEnd(deltaY: number, velocity: number) {
  const shouldRoll =
    Math.abs(deltaY) > ROLL_THRESHOLD ||
    Math.abs(velocity) > VELOCITY_THRESHOLD

  if (shouldRoll) {
    triggerRoll()
    hapticFeedback('medium')
  } else {
    animateBack()
  }
}
```

**Анимация броска:**

```css
@keyframes diceRoll {
  0% {
    transform: translateY(0) scale(1.2) rotate(15deg);
  }
  20% {
    transform: translateY(-100px) scale(1.4) rotate(180deg);
    opacity: 1;
  }
  40% {
    transform: translateY(-80px) scale(1.2) rotate(360deg);
  }
  100% {
    transform: translateY(0) scale(1) rotate(720deg);
    opacity: 0;
  }
}
```

---

## Character Sheet (Player)

### Drag вверх/вниз — раскрытие карточки

```
         ┌───────────────────┐
   drag  │ ═══════════════   │  ← Handle
    ↕    │                   │
         │  Character Info   │
         │                   │
         └───────────────────┘
```

**Snap points:**
- `peek`: 80px (только имя и HP)
- `half`: 40vh (основная информация)
- `full`: 70vh (полная карточка)

**Реализация:**

```typescript
const SNAP_POINTS = {
  peek: 80,
  half: window.innerHeight * 0.4,
  full: window.innerHeight * 0.7
}

function onSheetDrag(deltaY: number, startHeight: number) {
  const newHeight = startHeight - deltaY
  sheetHeight.value = clamp(newHeight, SNAP_POINTS.peek, SNAP_POINTS.full)
}

function onSheetDragEnd(velocity: number) {
  // Найти ближайший snap point
  const currentHeight = sheetHeight.value
  let targetSnap = 'half'

  // Учитываем скорость
  if (velocity < -0.5) {
    // Быстрый свайп вниз
    targetSnap = 'peek'
  } else if (velocity > 0.5) {
    // Быстрый свайп вверх
    targetSnap = 'full'
  } else {
    // Ближайший по позиции
    const distances = Object.entries(SNAP_POINTS).map(([name, height]) => ({
      name,
      distance: Math.abs(currentHeight - height)
    }))
    targetSnap = distances.sort((a, b) => a.distance - b.distance)[0].name
  }

  animateToHeight(SNAP_POINTS[targetSnap])
}
```

---

## Canvas Map

### Pinch to zoom

```
     👆         👆
      \       /
       \     /
        ╲   ╱
         ╲ ╱
          ●  ← центр масштабирования
```

**Параметры:**
- `minZoom`: 0.5
- `maxZoom`: 3.0
- `zoomStep`: 0.1 (для колеса мыши)

**Реализация:**

```typescript
function onPinch(scale: number, center: Point) {
  const newZoom = clamp(
    baseZoom * scale,
    MIN_ZOOM,
    MAX_ZOOM
  )

  // Масштабирование относительно центра жеста
  const zoomDelta = newZoom / mapState.zoom
  mapState.offsetX = center.x - (center.x - mapState.offsetX) * zoomDelta
  mapState.offsetY = center.y - (center.y - mapState.offsetY) * zoomDelta
  mapState.zoom = newZoom
}
```

### Pan (перемещение)

```
      👆────────→
       drag to pan
```

**Для GM:**
- Свободное перемещение одним или двумя пальцами

**Для Player:**
- Только двумя пальцами (один палец — выбор токена)

### Long press — контекстное меню

```
      👆
      ████  1.5s

   ┌─────────────┐
   │ Move        │
   │ Attack      │
   │ Cast Spell  │
   └─────────────┘
```

**Параметры:**
- `duration`: 500ms
- `moveTolerance`: 10px (если сдвинулся — отмена)

---

## GM Interactions

### Drag токена

```
     👆═══════════════→ 🎯
     drag token to move
```

**Параметры:**
- `gridSnap`: true (привязка к сетке)
- `ghostOpacity`: 0.5 (полупрозрачный клон при перетаскивании)

**Состояния:**

```typescript
interface TokenDragState {
  token: Token | null
  startPosition: Point
  currentPosition: Point
  validDropTarget: boolean
}

function onTokenDragStart(token: Token) {
  state.token = token
  state.startPosition = token.position
  showMovementRange(token) // Показать радиус перемещения
}

function onTokenDrag(position: Point) {
  const snapped = snapToGrid(position)
  state.currentPosition = snapped
  state.validDropTarget = isValidMove(state.token, snapped)
}

function onTokenDragEnd() {
  if (state.validDropTarget) {
    moveToken(state.token, state.currentPosition)
    hapticFeedback('light')
  } else {
    animateBack(state.token, state.startPosition)
  }
  hideMovementRange()
}
```

### Double tap — быстрое действие

- На токене: открыть карточку персонажа
- На пустой клетке: создать маркер

---

## Библиотека для жестов

Рекомендую **@vueuse/gesture** или **Hammer.js**.

### Установка

```bash
npm install @vueuse/gesture
```

### Использование

```vue
<script setup>
import { useGesture } from '@vueuse/gesture'

const target = ref(null)

useGesture({
  onDrag: ({ movement: [mx, my], velocity }) => {
    // ...
  },
  onPinch: ({ offset: [scale], origin }) => {
    // ...
  }
}, {
  domTarget: target,
  eventOptions: { passive: false }
})
</script>

<template>
  <div ref="target" class="gesture-area">
    <!-- content -->
  </div>
</template>
```

---

## Haptic Feedback

```typescript
function hapticFeedback(intensity: 'light' | 'medium' | 'heavy') {
  if (!navigator.vibrate) return

  const patterns = {
    light: [10],
    medium: [20],
    heavy: [30, 10, 30]
  }

  navigator.vibrate(patterns[intensity])
}

// Использование
hapticFeedback('medium') // При броске кубика
hapticFeedback('light')  // При выборе кубика
hapticFeedback('heavy')  // При критическом ударе
```

---

## Accessibility

### Альтернативы для жестов

| Жест | Альтернатива |
|------|-------------|
| Свайп выбора кубика | Стрелки ← → |
| Свайп вверх (бросок) | Кнопка "Roll" / Enter |
| Pinch zoom | Кнопки +/- или Ctrl+колесо |
| Long press | Right click |

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

```typescript
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches

function animateDiceRoll() {
  if (prefersReducedMotion) {
    // Мгновенный результат без анимации
    showResult()
  } else {
    // Полная анимация
    playRollAnimation()
  }
}
```
