# DnD Lite GM Frontend

Фронтенд приложения для Game Master интерфейса DnD Lite GM.

## Технологии

- Vue 3 (Composition API)
- TypeScript
- Vite
- Pinia (State Management)
- Vue Router
- Axios (HTTP Client)
- Lucide Vue Next (Icons)

## Установка

```bash
cd frontend
npm install
```

## Разработка

```bash
npm run dev
```

Приложение будет доступно по адресу http://localhost:3000

## Сборка

```bash
npm run build
```

## Структура проекта

```
frontend/
├── src/
│   ├── assets/css/      # Design tokens и базовые стили
│   ├── components/       # Vue компоненты
│   │   ├── common/      # Базовые компоненты
│   │   ├── gm/          # Компоненты для GM интерфейса
│   │   └── character/   # Компоненты персонажей
│   ├── composables/      # Vue composables
│   ├── layouts/          # Layout компоненты
│   ├── router/           # Vue Router конфигурация
│   ├── services/         # API и WebSocket сервисы
│   ├── stores/           # Pinia stores
│   ├── types/            # TypeScript типы
│   └── views/            # Страницы приложения
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Переменные окружения

Создайте файл `.env.development`:

```
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

## Требования

- Node.js 18+
- npm или yarn
- Запущенный бэкенд сервер на порту 8000
