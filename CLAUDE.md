# CLAUDE.md

Этот файл предоставляет руководство для Claude Code (claude.ai/code) при работе с кодом в этом репозитории.

## Ведение changelog

Все значимые изменения в проекте **обязательно** фиксируйте в файле `changelog.md` в корне репозитория. Для каждого изменения добавляйте короткое описание и дату в свободном текстовом формате.

## Тестирование бэкенда

Любое изменение бэкенда (новый endpoint, сервис, модель, утилита) **обязательно** сопровождается тестами. Код без тестов не считается завершённым. Подробный регламент — в **[docs/testing.md](docs/testing.md)**.

```bash
# Все тесты
pytest tests/ -v

# Только unit-тесты (быстро, без БД)
pytest tests/unit/ -v

# Только интеграционные тесты (API, сервисы, WebSocket)
pytest tests/integration/ -v

# Конкретный файл
pytest tests/integration/test_session_api.py -v

# Конкретный класс
pytest tests/integration/test_combat_api.py::TestStartCombat -v

# С коротким выводом ошибок
pytest tests/ --tb=short

# Только упавшие тесты
pytest tests/ --lf
```

Перед коммитом бэкенд-изменений убедись, что `pytest tests/ -v` проходит полностью.

## Команды разработки

```bash
# Активация виртуального окружения
source venv/bin/activate

# Запуск сервера разработки (с автоперезагрузкой)
uvicorn app.main:app --reload

# Запуск на конкретном хосте/порту
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Установка зависимостей
pip install -r requirements.txt

# Локальная разработка через Docker
docker compose -f docker-compose.dev.yml up --build

# Продакшн Docker
docker compose up --build
```

Документация API доступна по адресу http://localhost:8000/docs (Swagger UI).

## Архитектура

DnD Lite GM — монолитное FastAPI приложение для проведения игровых сессий D&D. Один сервер, одна база данных SQLite, одна активная сессия за раз. Фронтенд — Vue 3 SPA, собирается и раздаётся через FastAPI в продакшне.

### Структура backend

```
app/
├── main.py              # FastAPI приложение, WebSocket endpoint на /ws, SPA routing
├── config.py            # Настройки (SECRET_KEY, алгоритм JWT)
├── database.py          # SQLAlchemy session factory
├── migrations.py        # Startup-миграции для SQLite
├── api/                 # REST роутеры
│   ├── session.py       # Создание/подключение/старт сессии, готовность, движение
│   ├── characters.py    # CRUD персонажей сессии
│   ├── combat.py        # Управление боем, инициатива
│   ├── dice.py          # Броски кубиков (advantage/disadvantage)
│   ├── maps.py          # Карты сессии + токены
│   ├── templates.py     # Шаблоны классов D&D 5e
│   ├── persistence.py   # Экспорт/импорт сессий
│   ├── users.py         # Регистрация, логин, статистика
│   ├── user_characters.py  # Библиотека персонажей пользователя
│   └── user_maps.py     # Библиотека карт пользователя
├── models/              # SQLAlchemy ORM модели
│   ├── session.py       # Session
│   ├── player.py        # Player (is_gm, is_ready, can_move)
│   ├── character.py     # Character (сессионный)
│   ├── item.py          # Item
│   ├── spell.py         # Spell
│   ├── combat.py        # Combat, CombatParticipant, InitiativeRoll
│   ├── user.py          # User (аккаунт)
│   ├── user_character.py  # UserCharacter (библиотека + NPC)
│   ├── user_map.py      # UserMap (библиотека карт)
│   └── map.py           # Map, MapToken
├── schemas/             # Pydantic схемы валидации (зеркало models/)
├── services/            # Бизнес-логика
│   ├── dice.py          # DiceService (парсинг, броски, advantage/disadvantage)
│   ├── combat.py        # CombatService (инициатива, ходы, урон/лечение)
│   ├── modifiers.py     # ModifierService (модификаторы D&D 5e)
│   └── persistence/     # Экспорт/импорт сессий (Registry + Serializers)
├── websocket/           # ConnectionManager + обработчики событий
│   ├── manager.py       # ConnectionManager (asyncio.Lock, heartbeat, таймауты)
│   └── handlers.py      # Обработка сообщений (dice, chat)
└── core/                # Утилиты и константы
    ├── abilities.py     # Enum характеристик D&D
    ├── dice.py          # Паттерны кубиков
    ├── class_templates.py  # 12 шаблонов классов D&D 5e
    └── auth.py          # JWT токены, хеширование паролей (bcrypt)
```

### Структура frontend

```
frontend/src/
├── views/               # Страницы приложения
│   ├── LoginView.vue    # Авторизация
│   ├── RegisterView.vue # Регистрация
│   ├── HomeView.vue     # Dashboard со статистикой
│   ├── ProfileView.vue  # Профиль (персонажи, карты, NPC)
│   ├── GMLobbyView.vue  # Лобби GM (код, игроки, карты, старт)
│   ├── GMView.vue       # Основной интерфейс GM (карта, боковая панель, бой)
│   ├── PlayerLobbyView.vue  # Лобби игрока (выбор персонажа, готовность)
│   ├── PlayerView.vue   # Основной интерфейс игрока (карта, сайдбар)
│   ├── CreateCharacterView.vue  # Создание персонажа/NPC
│   ├── EditCharacterView.vue    # Редактирование персонажа
│   └── CreateMapView.vue        # Создание карты
├── stores/              # Pinia stores
│   ├── auth.ts          # Регистрация/логин/logout
│   ├── session.ts       # Состояние сессии, WebSocket подключение
│   ├── characters.ts    # Персонажи сессии
│   ├── combat.ts        # Бой, инициатива
│   ├── dice.ts          # История бросков
│   ├── map.ts           # Карты, токены, WebSocket обработчики
│   └── profile.ts       # Библиотека персонажей/карт пользователя
├── components/
│   ├── common/          # BaseButton, BaseInput, BaseModal, BasePanel, ConfirmModal, Toast
│   ├── map/             # GameMap (Konva.js), MapToken, AddTokenModal
│   ├── character/       # CharacterCard, CharacterSheet, HPBar
│   ├── dice/            # DiceRollModal, RollResult, RollHistory
│   ├── combat/          # CombatTab, InitiativeBar, InitiativeRollModal
│   ├── gm/              # GMLayout, PlayersTab, NPCSection
│   ├── player/          # PlayerLayout, PlayerSidebar, PlayerTopBar
│   ├── profile/         # UserCharacterCard, UserMapCard, AddCard
│   └── templates/       # ClassTemplateCard, TemplateSelector
├── composables/         # useAuth, useToast, useWebSocket
├── services/            # api.ts (Axios), websocket.ts (реконнект)
├── types/               # models.ts, events.ts, api.ts
├── data/                # tokenIcons.ts (15 SVG иконок для токенов карты)
├── router/              # Vue Router с guards
└── layouts/             # GMLayout, PlayerLayout
```

**Стек фронтенда**: Vue 3 + TypeScript + Vite + Pinia + Axios + Konva.js (vue-konva)

### Аутентификация

Двухуровневая система:

1. **Аккаунты пользователей**: Регистрация/логин → JWT (access + refresh токены). Пароли хешируются bcrypt. Роли: player, gm.
2. **Сессионные токены**: Создание/подключение к сессии → JWT с sub = player_token UUID. 6-символьный код комнаты (в стиле Jackbox).

REST API защищён Bearer токенами. WebSocket подключение через `/ws?token=`. Axios interceptors автоматически обновляют access token при 401.

### Ключевые модели

**Сессионные:**
- **Session** → имеет много **Players** → каждый имеет много **Characters**
- **Character** → имеет **Items** и **Spells**
- **Combat** → имеет **CombatParticipants** и **InitiativeRolls**
- **Map** → имеет много **MapTokens** (привязка к Character опциональна)

**Пользовательские (вне сессий):**
- **User** → имеет **UserCharacters** (библиотека + NPC) и **UserMaps** (библиотека карт)
- При подключении к сессии UserCharacter копируется в сессионный Character

### Система карт

- **Backend**: Map (UUID, session_id, name, background_url, width, height, grid_scale, is_active) и MapToken (UUID, map_id, character_id, type, x, y, scale, rotation, layer, label, color, icon)
- **Frontend**: Konva.js canvas с зумом, панорамированием, слоями (фон, сетка, токены)
- **Токены**: Персонажные (цветной круг с именем) и произвольные (15 SVG иконок: сундук, бочка, костёр и т.д.)
- **Права**: GM управляет всеми токенами. Игроки двигают только свой токен при наличии разрешения (Player.can_move)

### Сервисы

- `DiceService`: Парсит нотацию типа "2d6+3", бросает кубики, поддерживает advantage/disadvantage
- `CombatService`: Порядок инициативы, управление ходами, урон/лечение, автоотключение при 0 HP
- `ModifierService`: Расчёты модификаторов характеристик D&D 5e
- `PersistenceService`: Экспорт/импорт сессий в JSON (Registry + Serializers)

### Миграции БД

Alembic не используется. Вместо этого — лёгкий startup-скрипт `app/migrations.py`.

При запуске `run_migrations()` проверяет схему SQLite и добавляет недостающие столбцы. Вызывается в `main.py` после `Base.metadata.create_all()`.

Чтобы добавить новую миграцию, добавь запись в список `MIGRATIONS` в `app/migrations.py`:

```python
{
    "table": "имя_таблицы",
    "column": "имя_столбца",
    "sql": "ALTER TABLE имя_таблицы ADD COLUMN имя_столбца ТИП DEFAULT значение",
},
```

Скрипт идемпотентный — пропускает уже существующие столбцы.

### События WebSocket

Сервер транслирует: `player_joined`, `player_left`, `player_ready`, `player_movement_changed`, `session_started`, `dice_result`, `character_created`, `character_updated`, `character_deleted`, `combat_started`, `combat_ended`, `turn_changed`, `hp_changed`, `initiative_rolled`, `map_created`, `map_changed`, `token_added`, `token_updated`, `token_removed`, `ping`

Клиент отправляет: `roll_dice`, `chat`, `pong`

### Деплой

- **Dockerfile**: Мультистадийная сборка (Node → фронтенд, Python → бэкенд). Фронтенд собирается и раздаётся через FastAPI.
- **docker-compose.yml**: Продакшн (network_mode: host, volume для SQLite БД).
- **docker-compose.dev.yml**: Разработка (два сервиса: backend с --reload на :8000, frontend с Vite на :5173).
- **SPA routing**: StarletteHTTPException handler отдаёт index.html для не-API 404 ошибок.

### CI/CD

GitHub Actions workflow (`.github/workflows/deploy.yml`):

1. **test** — запускается на каждый push и PR в `main`. Ставит Python 3.11, устанавливает зависимости, прогоняет `pytest tests/ -v --tb=short`.
2. **deploy** — запускается только при push в `main` и только если `test` прошёл. SSH на VPS → `git pull && docker compose up -d --build`.

Секреты (Settings → Secrets → Actions): `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_PORT`.
