# Design Tokens

Базовые переменные дизайн-системы DnD Lite GM.

Определены в `frontend/src/assets/css/tokens.css`.

## Цветовая палитра

### Основные цвета

```css
:root {
  /* Фон */
  --color-bg-primary: #1a1a2e;      /* Основной тёмный фон */
  --color-bg-secondary: #16213e;    /* Вторичный фон (панели, TopBar) */
  --color-bg-tertiary: #0f0f1a;     /* Третичный (инпуты, глубокий фон) */
  --color-bg-elevated: #252542;     /* Приподнятые элементы (карточки, сайдбары) */

  /* Акценты */
  --color-accent-primary: #e94560;   /* Основной акцент (кнопки, активные элементы) */
  --color-accent-secondary: #7b2cbf; /* Вторичный акцент (магия) */
  --color-accent-gold: #ffd700;      /* Золотой (награды, критические) */

  /* Текст */
  --color-text-primary: #eaeaea;     /* Основной текст */
  --color-text-secondary: #a0a0a0;   /* Вторичный текст */
  --color-text-muted: #666666;       /* Приглушённый текст */
  --color-text-inverse: #1a1a2e;     /* Текст на светлом фоне */

  /* Семантические */
  --color-success: #4ade80;          /* Успех, лечение, «Подключено» */
  --color-warning: #fbbf24;          /* Предупреждение, NPC бейдж */
  --color-danger: #ef4444;           /* Опасность, урон, HP, удаление */
  --color-info: #60a5fa;             /* Информация */
}
```

### Прозрачности

```css
:root {
  --alpha-overlay-light: rgba(255, 255, 255, 0.05);
  --alpha-overlay-medium: rgba(255, 255, 255, 0.1);  /* Кнопки action-btn на обороте карточки */
  --alpha-overlay-heavy: rgba(0, 0, 0, 0.5);         /* Overlay сайдбаров */
  --alpha-glass: rgba(22, 33, 62, 0.85);              /* Стеклянные панели */
}
```

## Типографика

```css
:root {
  /* Шрифты */
  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-display: 'Cinzel', 'Times New Roman', serif;  /* D&D заголовки */
  --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Размеры */
  --font-size-xs: 0.75rem;    /* 12px — бейджи, метки */
  --font-size-sm: 0.875rem;   /* 14px — подписи, secondary text */
  --font-size-base: 1rem;     /* 16px — основной текст */
  --font-size-lg: 1.125rem;   /* 18px — section titles */
  --font-size-xl: 1.25rem;    /* 20px — заголовки TopBar, карточек */
  --font-size-2xl: 1.5rem;    /* 24px — заголовки страниц */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px — коды сессий */
}
```

### Шрифт Cinzel (Google Fonts)

Подключён в `index.html` через preconnect + stylesheet:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&display=swap" rel="stylesheet">
```

Используется через `var(--font-family-display)`:
- Заголовки TopBar: "Профиль", "Лобби", "Присоединиться"
- Section titles: "Мои персонажи", "Ваш персонаж"
- Имя на лицевой стороне CharacterFlipCard
- Лейблы характеристик на обороте (СИЛ, ЛОВ, ТЕЛ...)
- Sidebar header ("Меню")

## Отступы и размеры

```css
:root {
  /* Spacing scale (4px base) */
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */

  /* Панели */
  --panel-height-top: 48px;    /* TopBar всех страниц */
}
```

## Скругления, тени, анимации

```css
:root {
  --radius-sm: 4px;
  --radius-md: 8px;       /* Кнопки, инпуты */
  --radius-lg: 12px;      /* Карточки, CharacterFlipCard */
  --radius-full: 9999px;  /* Круглые элементы, dots */

  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
  --shadow-2xl: ...;      /* Сайдбары */
  --glow-accent: 0 0 20px rgba(233, 69, 96, 0.4);  /* Активные dots, focus */

  --duration-fast: 150ms;     /* Hover, кнопки */
  --duration-normal: 250ms;   /* Sidebar transitions */

  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);   /* Sidebar, карусель */
}
```

## Z-Index

```css
:root {
  --z-modal: 500;         /* Сайдбары (Teleport → overlay) */
  --z-toast: 800;         /* Toast уведомления */
}
```
