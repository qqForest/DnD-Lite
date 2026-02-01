# Design Tokens

Базовые переменные дизайн-системы DnD Lite GM.

## Цветовая палитра

### Основные цвета

```css
:root {
  /* Фон */
  --color-bg-primary: #1a1a2e;      /* Основной тёмный фон */
  --color-bg-secondary: #16213e;    /* Вторичный фон (панели) */
  --color-bg-tertiary: #0f0f1a;     /* Третичный (карта, глубокий фон) */
  --color-bg-elevated: #252542;     /* Приподнятые элементы (карточки) */

  /* Акценты */
  --color-accent-primary: #e94560;   /* Основной акцент (действия, кнопки) */
  --color-accent-secondary: #7b2cbf; /* Вторичный акцент (магия) */
  --color-accent-gold: #ffd700;      /* Золотой (награды, важное) */

  /* Текст */
  --color-text-primary: #eaeaea;     /* Основной текст */
  --color-text-secondary: #a0a0a0;   /* Вторичный текст */
  --color-text-muted: #666666;       /* Приглушённый текст */
  --color-text-inverse: #1a1a2e;     /* Текст на светлом фоне */

  /* Семантические */
  --color-success: #4ade80;          /* Успех, лечение */
  --color-warning: #fbbf24;          /* Предупреждение */
  --color-danger: #ef4444;           /* Опасность, урон */
  --color-info: #60a5fa;             /* Информация */

  /* Классы D&D */
  --color-class-fighter: #c0392b;    /* Воин - красный */
  --color-class-wizard: #2980b9;     /* Волшебник - синий */
  --color-class-rogue: #27ae60;      /* Плут - зелёный */
  --color-class-cleric: #f1c40f;     /* Жрец - золотой */
  --color-class-barbarian: #e67e22;  /* Варвар - оранжевый */
  --color-class-ranger: #16a085;     /* Следопыт - бирюзовый */
  --color-class-paladin: #9b59b6;    /* Паладин - фиолетовый */
  --color-class-bard: #e91e63;       /* Бард - розовый */
  --color-class-druid: #8bc34a;      /* Друид - салатовый */
  --color-class-monk: #795548;       /* Монах - коричневый */
  --color-class-sorcerer: #ff5722;   /* Чародей - огненный */
  --color-class-warlock: #673ab7;    /* Колдун - тёмно-фиолетовый */
}
```

### Прозрачности

```css
:root {
  --alpha-overlay-light: rgba(255, 255, 255, 0.05);
  --alpha-overlay-medium: rgba(255, 255, 255, 0.1);
  --alpha-overlay-heavy: rgba(0, 0, 0, 0.5);
  --alpha-glass: rgba(22, 33, 62, 0.85);  /* Стеклянный эффект для панелей */
}
```

## Типографика

```css
:root {
  /* Шрифты */
  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-display: 'Cinzel', 'Times New Roman', serif;  /* Заголовки в стиле D&D */
  --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Размеры */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */

  /* Высота строки */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* Вес */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}
```

## Отступы и размеры

```css
:root {
  /* Spacing scale (4px base) */
  --spacing-0: 0;
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-5: 1.25rem;   /* 20px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */
  --spacing-10: 2.5rem;   /* 40px */
  --spacing-12: 3rem;     /* 48px */
  --spacing-16: 4rem;     /* 64px */

  /* Размеры панелей */
  --panel-width-sm: 48px;     /* Свёрнутая боковая панель (только иконки) */
  --panel-width-md: 240px;    /* Развёрнутая боковая панель */
  --panel-width-lg: 320px;    /* Широкая панель (детали персонажа) */
  --panel-height-top: 48px;   /* Верхняя панель */
  --panel-height-bottom: 80px; /* Нижняя панель (кубики) */

  /* Размеры элементов */
  --icon-size-sm: 16px;
  --icon-size-md: 24px;
  --icon-size-lg: 32px;
  --icon-size-xl: 48px;

  --avatar-size-sm: 32px;
  --avatar-size-md: 48px;
  --avatar-size-lg: 64px;
}
```

## Скругления

```css
:root {
  --radius-none: 0;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-full: 9999px;  /* Круглые элементы */
}
```

## Тени

```css
:root {
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.6);

  /* Glow эффекты */
  --glow-accent: 0 0 20px rgba(233, 69, 96, 0.4);
  --glow-magic: 0 0 20px rgba(123, 44, 191, 0.4);
  --glow-gold: 0 0 20px rgba(255, 215, 0, 0.4);
}
```

## Анимации

```css
:root {
  /* Длительность */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;

  /* Easing */
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

## Z-Index

```css
:root {
  --z-base: 0;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-fixed: 300;
  --z-modal-backdrop: 400;
  --z-modal: 500;
  --z-popover: 600;
  --z-tooltip: 700;
  --z-toast: 800;
}
```

## Breakpoints

```css
:root {
  /* Mobile first */
  --breakpoint-sm: 640px;   /* Большой телефон */
  --breakpoint-md: 768px;   /* Планшет */
  --breakpoint-lg: 1024px;  /* Маленький десктоп */
  --breakpoint-xl: 1280px;  /* Десктоп */
  --breakpoint-2xl: 1536px; /* Большой десктоп */
}
```

## Использование

### В компонентах Vue

```vue
<style scoped>
.my-button {
  background: var(--color-accent-primary);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-default);
}

.my-button:hover {
  box-shadow: var(--glow-accent);
}
</style>
```

### Классы D&D (пример)

```vue
<template>
  <div :class="`character-card class-${character.className.toLowerCase()}`">
    {{ character.name }}
  </div>
</template>

<style>
.character-card.class-fighter { border-color: var(--color-class-fighter); }
.character-card.class-wizard { border-color: var(--color-class-wizard); }
/* ... */
</style>
```
