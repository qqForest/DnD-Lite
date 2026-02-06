# Gestures & Interactions

Спецификация жестов и взаимодействий DnD Lite GM.

## useSwipe Composable

Основной механизм свайп-жестов. Реализован на Pointer Events (работает и touch, и desktop).

**Файл:** `frontend/src/composables/useSwipe.ts`

### API

```typescript
function useSwipe(options?: { threshold?: number }) {
  return {
    offsetX: Ref<number>,          // Текущее смещение в px
    isSwiping: Ref<boolean>,       // true во время горизонтального свайпа
    handlers: {                     // Привязать через v-bind к элементу
      onPointerdown, onPointermove, onPointerup, onPointercancel
    },
    onSwipeLeft: (fn: () => void) => void,   // Callback при свайпе влево
    onSwipeRight: (fn: () => void) => void,  // Callback при свайпе вправо
  }
}
```

### Логика

1. `pointerdown` → запоминаем `startX`, `startY`, вызываем `setPointerCapture`
2. `pointermove` → после 10px движения определяем направление:
   - Горизонтальное: `preventDefault()`, обновляем `offsetX`, `isSwiping = true`
   - Вертикальное: игнорируем (не мешаем скроллу)
3. `pointerup` → если `|offsetX| >= threshold (50px)`, вызываем `onSwipeLeft`/`onSwipeRight`

### Использование (CharacterCarousel)

```vue
<template>
  <div class="carousel" v-bind="handlers" style="touch-action: pan-y">
    <div class="track" :style="trackStyle">
      <div v-for="item in items" class="slide">...</div>
    </div>
  </div>
</template>

<script setup>
const { offsetX, isSwiping, handlers, onSwipeLeft, onSwipeRight } = useSwipe()

onSwipeLeft(() => { if (index < max) index++ })
onSwipeRight(() => { if (index > 0) index-- })

const trackStyle = computed(() => ({
  transform: `translateX(${-(index * 100) + dragPercent}%)`,
  transition: isSwiping.value ? 'none' : 'transform 300ms ease-out',
}))
</script>
```

**`touch-action: pan-y`** на контейнере — разрешает вертикальный скролл, горизонтальный контролируем вручную.

---

## CharacterFlipCard — тап

Простой toggle `flipped = !flipped` по `@click`.

```css
.flip-card { perspective: 1000px; }
.flip-card-inner {
  transform-style: preserve-3d;
  transition: transform 300ms ease;
}
.flip-card.flipped .flip-card-inner {
  transform: rotateY(180deg);
}
.flip-card-front, .flip-card-back {
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}
.flip-card-back { transform: rotateY(180deg); }
```

---

## Sidebar — slide-in

Паттерн для всех сайдбаров (ProfileSidebar, PlayerLobbySidebar, PlayerSidebar):

```vue
<Teleport to="body">
  <Transition name="sidebar">
    <div v-if="open" class="overlay" @click="close">
      <div class="sidebar" @click.stop>...</div>
    </div>
  </Transition>
</Teleport>
```

```css
/* Overlay fade */
.sidebar-enter-from, .sidebar-leave-to { opacity: 0; }
.sidebar-enter-active, .sidebar-leave-active {
  transition: opacity var(--duration-normal) var(--ease-out);
}

/* Panel slide */
.sidebar-enter-from .sidebar, .sidebar-leave-to .sidebar {
  transform: translateX(-100%);
}
.sidebar-enter-active .sidebar, .sidebar-leave-active .sidebar {
  transition: transform var(--duration-normal) var(--ease-out);
}
```

---

## Canvas Map (Konva.js)

### Zoom

- **Колесо мыши:** `@wheel` → изменение `stageScale`, зум к позиции курсора
- **Pinch (touch):** обрабатывается Konva.js нативно
- **Кнопки:** ZoomIn / ZoomOut в тулбаре карты
- Диапазон: 0.5x — 3.0x

### Pan

- **Drag** по пустой области стейджа → `stage.draggable(true)`
- GM: свободное перемещение
- Player: свободное перемещение (readonly для токенов)

### Токены

- **GM:** drag любого токена → `@dragend` → API `PATCH /maps/{id}/tokens/{tokenId}`
- **Player:** drag только своего токена при `can_move = true`
- Снэп к сетке при отпускании

### Контекстное меню (GM)

- **ПКМ на токене** → позиционируемое меню: "Удалить", "Убить"
- Закрывается по клику вне области

---

## Touch Targets

Все интерактивные элементы имеют минимальный размер 44x44px:

| Элемент | Реализация |
|---------|------------|
| BaseButton sm/md | `@media (max-width: 768px) { min-height: 44px }` |
| Hamburger (Menu) | `width: 44px; height: 44px` |
| Close button (×) | `width: 44px; height: 44px` |
| Carousel dots | `min-width: 44px; min-height: 44px` (padding вокруг 8px dot) |
| Action buttons (edit/delete) | `min-width: 44px; min-height: 44px` |
| Nav buttons (sidebar) | `min-height: 48px; width: 100%` |

---

## Accessibility

### Альтернативы для жестов

| Жест | Альтернатива |
|------|-------------|
| Свайп карусели | Клик по dots |
| Тап flip-карточки | Любой клик/тап |
| Свайп sidebar | Клик по гамбургеру |
| Pinch zoom | Кнопки +/- на карте |

### Reduced Motion

Анимации используют CSS transitions/transforms — при `prefers-reduced-motion: reduce` можно обнулить `transition-duration`.
