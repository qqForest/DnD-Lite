---
trigger: always_on
---

## Ведение changelog

Все значимые изменения в проекте **обязательно** фиксируйте в файле `changelog` в корне репозитория. Для каждого изменения добавляйте короткое описание и дату в свободном текстовом формате.

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
```

Документация API доступна по адресу http://localhost:8000/docs (Swagger UI).

## Архитектура

DnD Lite GM — это монолитное FastAPI приложение для проведения игровых сессий D&D. Один сервер, одна база данных SQLite, одна активная сессия за раз.

### Структура слоёв

```
app/
├── main.py              # FastAPI приложение, WebSocket endpoint на /ws
├── api/                 # REST роутеры: session, characters, combat, dice
├── models/              # SQLAlchemy ORM модели
├── schemas/             # Pydantic схемы валидации (зеркало models/)
├── services/            # Бизнес-логика (броски кубиков, бой, модификаторы D&D)
├── websocket/           # ConnectionManager + обработчики событий
└── core/                # Константы D&D (характеристики, типы кубиков)
```

### Поток данных

1. **Аутентификация**: 6-символьный код комнаты (в стиле Jackbox) + UUID токены для GM и игроков
2. **REST API** (`/api/*`): CRUD операции, все требуют параметр запроса `?token=`
3. **WebSocket** (`/ws?token=`): События в реальном времени, транслируемые всем подключённым игрокам

### Ключевые модели

- **Session** → имеет много **Players** → каждый имеет много **Characters**
- **Character** → имеет **Items** и **Spells**
- **Combat** → имеет **CombatParticipants** (связи с Characters с отслеживанием инициативы/HP)

### Сервисы

- `DiceService`: Парсит нотацию типа "2d6+3", бросает кубики
- `CombatService`: Порядок инициативы, управление ходами, урон/лечение
- `ModifierService`: Расчёты модификаторов характеристик D&D 5e

### События WebSocket

Сервер транслирует: `player_joined`, `player_left`, `dice_result`, `combat_started`, `combat_ended`, `turn_changed`, `character_updated`, `hp_changed`

Клиент отправляет: `roll_dice`, `chat`
