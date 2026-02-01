# UI Components

Спецификация UI компонентов DnD Lite GM.

## Принципы

1. **Все размеры через токены** — используй `var(--spacing-*)`, `var(--radius-*)` и т.д.
2. **Семантические цвета** — `var(--color-danger)` вместо `#ef4444`
3. **Анимации обязательны** — все интерактивные элементы должны иметь hover/active состояния
4. **Touch-friendly** — минимальный размер тач-цели 44x44px

---

## Кнопки

### BaseButton

```vue
<template>
  <button
    :class="['btn', `btn-${variant}`, `btn-${size}`, { 'btn-icon-only': iconOnly }]"
    :disabled="disabled"
  >
    <span v-if="icon" class="btn-icon">
      <component :is="icon" />
    </span>
    <span v-if="!iconOnly" class="btn-text">
      <slot />
    </span>
  </button>
</template>
```

### Варианты

| Variant | Использование | Стиль |
|---------|--------------|-------|
| `primary` | Основные действия | Filled, accent color |
| `secondary` | Вторичные действия | Outlined |
| `ghost` | Третичные действия | Transparent, text only |
| `danger` | Деструктивные действия | Red filled |

### Размеры

| Size | Padding | Font | Min Height |
|------|---------|------|------------|
| `sm` | 6px 12px | 14px | 32px |
| `md` | 8px 16px | 16px | 40px |
| `lg` | 12px 24px | 18px | 48px |

### CSS

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-family-primary);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.btn-primary {
  background: var(--color-accent-primary);
  color: var(--color-text-primary);
}

.btn-primary:hover {
  filter: brightness(1.1);
  box-shadow: var(--glow-accent);
}

.btn-primary:active {
  transform: scale(0.98);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon-only {
  aspect-ratio: 1;
  padding: var(--spacing-2);
}
```

---

## Панели

### Panel

Контейнер для группировки контента.

```vue
<template>
  <div :class="['panel', `panel-${variant}`]">
    <header v-if="$slots.header || title" class="panel-header">
      <slot name="header">
        <h3 class="panel-title">{{ title }}</h3>
      </slot>
    </header>
    <div class="panel-content">
      <slot />
    </div>
    <footer v-if="$slots.footer" class="panel-footer">
      <slot name="footer" />
    </footer>
  </div>
</template>
```

### Варианты панелей

| Variant | Использование |
|---------|--------------|
| `default` | Стандартная панель |
| `glass` | Полупрозрачная (overlay поверх карты) |
| `elevated` | С тенью (карточки) |
| `flat` | Без фона (inline контент) |

```css
.panel {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.panel-glass {
  background: var(--alpha-glass);
  backdrop-filter: blur(12px);
  border: 1px solid var(--alpha-overlay-medium);
}

.panel-elevated {
  background: var(--color-bg-elevated);
  box-shadow: var(--shadow-lg);
}

.panel-header {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--alpha-overlay-light);
}

.panel-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.panel-content {
  padding: var(--spacing-4);
}

.panel-footer {
  padding: var(--spacing-3) var(--spacing-4);
  border-top: 1px solid var(--alpha-overlay-light);
  background: var(--alpha-overlay-light);
}
```

---

## Карточки

### CharacterCard

Компактная карточка персонажа для списков.

```
┌──────────────────────────────────┐
│ [Avatar]  Торин Дубощит          │
│           Воин • Уровень 5       │
│  ████████░░░░  45/60 HP          │
└──────────────────────────────────┘
```

```vue
<template>
  <div :class="['character-card', `class-${classType}`]">
    <div class="character-avatar">
      <img v-if="avatar" :src="avatar" :alt="name" />
      <span v-else class="avatar-placeholder">{{ initials }}</span>
    </div>
    <div class="character-info">
      <h4 class="character-name">{{ name }}</h4>
      <p class="character-meta">{{ className }} • Уровень {{ level }}</p>
      <HPBar :current="currentHp" :max="maxHp" />
    </div>
  </div>
</template>
```

```css
.character-card {
  display: flex;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-class-fighter); /* Dynamic by class */
  transition: all var(--duration-fast);
}

.character-card:hover {
  background: var(--alpha-overlay-light);
  transform: translateX(4px);
}

.character-avatar {
  width: var(--avatar-size-md);
  height: var(--avatar-size-md);
  border-radius: var(--radius-full);
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: var(--color-accent-secondary);
  font-weight: var(--font-weight-bold);
}

.character-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.character-meta {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: var(--spacing-1) 0;
}
```

---

## HP Bar

Индикатор здоровья.

```vue
<template>
  <div class="hp-bar">
    <div class="hp-bar-track">
      <div
        class="hp-bar-fill"
        :class="hpState"
        :style="{ width: `${percentage}%` }"
      />
    </div>
    <span class="hp-bar-text">{{ current }}/{{ max }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  current: Number,
  max: Number
})

const percentage = computed(() => (props.current / props.max) * 100)
const hpState = computed(() => {
  if (percentage.value > 50) return 'hp-healthy'
  if (percentage.value > 25) return 'hp-wounded'
  return 'hp-critical'
})
</script>
```

```css
.hp-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.hp-bar-track {
  flex: 1;
  height: 8px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.hp-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--duration-normal) var(--ease-out);
}

.hp-healthy { background: var(--color-success); }
.hp-wounded { background: var(--color-warning); }
.hp-critical {
  background: var(--color-danger);
  animation: pulse 1s infinite;
}

.hp-bar-text {
  font-size: var(--font-size-sm);
  font-family: var(--font-family-mono);
  min-width: 60px;
  text-align: right;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
```

---

## Dice Components

### DiceButton

Кнопка выбора кубика.

```vue
<template>
  <button
    :class="['dice-btn', { active: isSelected }]"
    @click="$emit('select')"
  >
    <DiceIcon :type="type" />
    <span class="dice-label">{{ type }}</span>
  </button>
</template>
```

```css
.dice-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-2);
  background: var(--color-bg-elevated);
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  min-width: 56px;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.dice-btn:hover {
  background: var(--alpha-overlay-medium);
  transform: translateY(-2px);
}

.dice-btn.active {
  border-color: var(--color-accent-primary);
  box-shadow: var(--glow-accent);
}

.dice-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
}
```

### RollResult

Отображение результата броска.

```
┌────────────────────────┐
│         🎲 20          │  ← Результат (большой)
│     Критический!       │  ← Статус
│   d20 + 5 = 25         │  ← Формула
│   Атака: Торин         │  ← Контекст
└────────────────────────┘
```

```css
.roll-result {
  text-align: center;
  padding: var(--spacing-6);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  animation: rollIn var(--duration-normal) var(--ease-bounce);
}

.roll-result.crit {
  background: linear-gradient(135deg, var(--color-accent-gold), var(--color-warning));
  color: var(--color-text-inverse);
}

.roll-result.fail {
  background: var(--color-danger);
}

.roll-value {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
}

.roll-formula {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

@keyframes rollIn {
  0% {
    transform: scale(0.5) rotate(-10deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.1) rotate(5deg);
  }
  100% {
    transform: scale(1) rotate(0);
    opacity: 1;
  }
}
```

---

## Inputs

### TextInput

```css
.input {
  width: 100%;
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-tertiary);
  border: 1px solid var(--alpha-overlay-medium);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  transition: all var(--duration-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 0 3px rgba(233, 69, 96, 0.2);
}

.input::placeholder {
  color: var(--color-text-muted);
}
```

---

## Icons

Используй иконки из **Lucide** (легковесная библиотека).

```bash
npm install lucide-vue-next
```

```vue
<script setup>
import { Sword, Shield, Heart, Sparkles, Dice6 } from 'lucide-vue-next'
</script>

<template>
  <Sword :size="24" />
</template>
```

### Рекомендуемые иконки

| Назначение | Иконка |
|------------|--------|
| Игроки | `Users` |
| Персонаж | `User` |
| События | `ScrollText` |
| Бой | `Swords` |
| Настройки | `Settings` |
| HP | `Heart` |
| AC | `Shield` |
| Магия | `Sparkles` |
| Инвентарь | `Backpack` |
| Кубик | `Dice6` |

---

## Модальные окна

### Modal

```vue
<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-backdrop" @click.self="close">
        <div class="modal" :class="`modal-${size}`">
          <header class="modal-header">
            <h2 class="modal-title">{{ title }}</h2>
            <button class="modal-close" @click="close">
              <X :size="20" />
            </button>
          </header>
          <div class="modal-body">
            <slot />
          </div>
          <footer v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
```

```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--alpha-overlay-heavy);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal-backdrop);
}

.modal {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-sm { width: min(400px, 90vw); }
.modal-md { width: min(560px, 90vw); }
.modal-lg { width: min(800px, 90vw); }

.modal-enter-active,
.modal-leave-active {
  transition: all var(--duration-normal) var(--ease-default);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal,
.modal-leave-to .modal {
  transform: scale(0.95) translateY(20px);
}
```

---

## Toast Notifications

```css
.toast-container {
  position: fixed;
  bottom: var(--spacing-4);
  right: var(--spacing-4);
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.toast {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  animation: slideIn var(--duration-normal) var(--ease-out);
}

.toast-success { border-left: 3px solid var(--color-success); }
.toast-error { border-left: 3px solid var(--color-danger); }
.toast-info { border-left: 3px solid var(--color-info); }

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
}
```
