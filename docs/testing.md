# Стандарт написания тестов

## Обязательное правило

Любое изменение бэкенда (новый endpoint, сервис, модель, утилита) **должно** сопровождаться тестами. Код без тестов не считается завершённым.

## Команды

```bash
# Активация окружения
source venv/bin/activate

# Все тесты
pytest tests/ -v

# Только unit-тесты (быстро, без БД)
pytest tests/unit/ -v

# Только интеграционные тесты (API, сервисы с БД, WebSocket)
pytest tests/integration/ -v

# Конкретный файл
pytest tests/integration/test_session_api.py -v

# Конкретный класс или метод
pytest tests/integration/test_session_api.py::TestCreateSession -v
pytest tests/integration/test_session_api.py::TestCreateSession::test_creates_session -v

# С коротким выводом ошибок
pytest tests/ --tb=short

# Только упавшие тесты из прошлого запуска
pytest tests/ --lf
```

## Структура тестов

```
tests/
├── conftest.py              # Фикстуры: engine, db, client, фабрики
├── unit/                    # Чистые функции без БД и сети
│   ├── test_abilities.py
│   ├── test_auth.py
│   ├── test_class_templates.py
│   └── test_dice_service.py
└── integration/             # Сервисы с БД + API endpoints + WebSocket
    ├── test_session_api.py
    ├── test_users_api.py
    ├── test_characters_api.py
    ├── test_templates_api.py
    ├── test_dice_api.py
    ├── test_combat_api.py
    ├── test_maps_api.py
    ├── test_user_characters_api.py
    ├── test_user_maps_api.py
    ├── test_persistence_api.py
    ├── test_modifier_service.py
    ├── test_combat_service.py
    └── test_websocket.py
```

### Куда класть тест

| Что тестируешь | Куда | Фикстуры |
|---|---|---|
| Чистая функция без БД (`calculate_modifier`, `parse_dice`, `hash_password`) | `tests/unit/` | Никаких, только `pytest.mark.parametrize` и `unittest.mock` |
| Сервис, работающий с БД (`CombatService`, `ModifierService`) | `tests/integration/` | `db`, фабрики (`create_session_fixture`, `create_character_fixture`) |
| REST API endpoint | `tests/integration/` | `client` (httpx AsyncClient) |
| WebSocket endpoint | `tests/integration/` | `ws_client` (starlette TestClient с патчем `get_db`) |

## Фикстуры (conftest.py)

Все основные фикстуры определены в `tests/conftest.py`. Не дублируй их в файлах тестов.

### `db` — SQLAlchemy сессия с откатом

Каждый тест получает чистую БД. После теста транзакция откатывается — данные не утекают между тестами.

```python
def test_something(self, db):
    # db — SQLAlchemy Session, привязанная к in-memory SQLite
    session = Session(code="ABC123", gm_token="...", is_active=True)
    db.add(session)
    db.flush()  # flush, не commit — работаем внутри транзакции
```

### `client` — httpx AsyncClient

Для тестирования REST API. Автоматически подменяет `get_db` через `dependency_overrides`.

```python
@pytest.mark.asyncio
class TestMyEndpoint:
    async def test_something(self, client):
        resp = await client.get("/api/something", headers=headers)
        assert resp.status_code == 200
```

### Фабрики

```python
# Создать сессию + GM
session, gm_player = create_session_fixture()

# Создать обычного игрока
player = create_player_fixture(session, name="Player1")

# Создать персонажа
character = create_character_fixture(player, name="Hero", max_hp=20)

# Создать пользователя
user = create_user_fixture(username="testuser")
```

### Хелперы для заголовков авторизации

```python
from tests.conftest import make_player_headers, make_user_headers

headers = make_player_headers(gm_player)   # {"Authorization": "Bearer <jwt>"}
headers = make_user_headers(user)           # {"Authorization": "Bearer <jwt>"}
```

## Паттерны написания тестов

### 1. Unit-тесты: parametrize для однотипных проверок

```python
class TestCalculateModifier:
    @pytest.mark.parametrize("score,expected", [
        (1, -5),
        (10, 0),
        (20, 5),
    ])
    def test_modifier_values(self, score, expected):
        assert calculate_modifier(score) == expected
```

### 2. Unit-тесты: mock для случайности и внешних зависимостей

```python
from unittest.mock import patch

class TestRoll:
    @patch("app.services.dice.random.randint")
    def test_roll_basic(self, mock_randint):
        mock_randint.side_effect = [3, 5]
        rolls, modifier, total = DiceService.roll("2d6+3")
        assert total == 11
```

### 3. API-тесты: классы группируют по endpoint/ресурсу

```python
@pytest.mark.asyncio
class TestCreateCharacter:
    async def test_create_success(self, client):
        # setup...
        resp = await client.post("/api/characters", json={...}, headers=gm_h)
        assert resp.status_code == 200

    async def test_requires_auth(self, client):
        resp = await client.post("/api/characters", json={...})
        assert resp.status_code in (401, 403)
```

### 4. API-тесты: setup-хелперы для сложных сценариев

Если тесту нужна сессия с GM, игроком и персонажем — выноси setup в функцию:

```python
async def _setup_combat_session(client):
    """Create session with GM + player who has a character."""
    resp, _, _ = await create_session_with_user(client)
    session_data = resp.json()
    gm_h = {"Authorization": f"Bearer {session_data['access_token']}"}
    # ... join player, create characters ...
    return session_data, gm_h, join_data, player_h, char_data
```

Хелперы `register_user()` и `create_session_with_user()` из `test_session_api.py` можно импортировать в другие файлы:

```python
from tests.integration.test_session_api import register_user, create_session_with_user
```

### 5. Мок WebSocket broadcast

Все endpoint'ы, которые отправляют WebSocket-события, нужно оборачивать в мок `broadcast_event`. Иначе тест упадёт, потому что нет активных WS-подключений.

```python
from unittest.mock import patch, AsyncMock

with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
    resp = await client.post("/api/session/join", json={...}, headers=h)
```

Путь для патча — **всегда** `"app.websocket.manager.manager.broadcast_event"` (глобальный singleton). Не `"app.api.session.manager.broadcast_event"`.

Если endpoint также вызывает `send_personal`, добавь второй патч:

```python
with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock), \
     patch("app.websocket.manager.manager.send_personal", new_callable=AsyncMock):
    resp = await client.post("/api/combat/initiative", headers=player_h)
```

### 6. WebSocket-тесты: патч get_db на уровне модуля

WebSocket endpoint вызывает `next(get_db())` напрямую (не через FastAPI DI), поэтому `dependency_overrides` не работает. Используй фикстуру `ws_client`, которая патчит `app.main.get_db`:

```python
class TestMyWebSocket:
    def test_something(self, ws_client):
        client, db = ws_client
        # создай Session + Player в db
        _, _, token = _setup_ws_player(db)

        with client.websocket_connect(f"/ws?token={token}") as ws:
            ws.send_json({"type": "chat", "payload": {"message": "hi"}})
            data = ws.receive_json()
            assert data["type"] == "chat"
```

WebSocket-тесты **синхронные** (starlette TestClient), не `async`.

### 7. Проверка прав доступа

Каждый endpoint с авторизацией должен иметь тесты:
- Успешный вызов с правильной ролью (GM / player / user)
- Отказ `403` для неправильной роли
- Отказ `401`/`403` без токена

```python
async def test_player_cannot_create(self, client):
    _, _, _, player_h = await _setup_map_session(client)
    resp = await client.post("/api/session/maps", json={...}, headers=player_h)
    assert resp.status_code == 403
```

### 8. Проверка граничных случаев

- Несуществующий ID → `404`
- Дубликат (имя, username) → `400`
- Пустые/невалидные данные → `400` или `422`
- Доступ к чужому ресурсу → `404` (не `403`, чтобы не раскрывать существование)

## Что проверять для нового endpoint

| Аспект | Пример теста |
|---|---|
| Happy path | Создание ресурса возвращает 200/201 с правильным телом |
| Авторизация | Без токена → 401; чужая роль → 403 |
| Валидация | Невалидный payload → 400/422 |
| Not found | Несуществующий ID → 404 |
| Бизнес-логика | Дубликаты, граничные значения, переполнение |
| Побочные эффекты | WebSocket broadcast вызван (мок проверяет `.assert_called`) |

## Что проверять для нового сервиса

| Аспект | Пример теста |
|---|---|
| Основная логика | Метод возвращает правильный результат |
| Граничные случаи | Пустые входы, нулевые значения, максимумы |
| Ошибки | ValueError/Exception при невалидных аргументах |
| Взаимодействие с БД | Данные создаются/обновляются/удаляются корректно |

## Добавление новой ORM-модели

Если добавляешь новую модель в `app/models/`, **обязательно** импортируй её в `tests/conftest.py` до строки `Base.metadata.create_all`. Иначе relationship'ы не резолвятся и тесты упадут с ошибкой вида `expression 'ModelName' failed to locate a name`.

```python
# tests/conftest.py — секция импортов моделей
from app.models.my_new_model import MyNewModel  # noqa: F401
```

## Именование

- Файл: `test_<module>.py` — по имени тестируемого модуля (`test_session_api.py`, `test_dice_service.py`)
- Класс: `Test<Feature>` — по фиче или ресурсу (`TestCreateSession`, `TestRollDice`)
- Метод: `test_<что_проверяем>` — описание поведения (`test_gm_can_start`, `test_requires_auth`, `test_invalid_notation`)
- Setup-хелпер: `_setup_<context>(...)` — приватная async-функция на уровне модуля

## Чеклист перед коммитом

1. Написаны тесты для всех новых/изменённых endpoint'ов и сервисов
2. `pytest tests/ -v` — все тесты проходят (включая старые)
3. Тесты проверяют не только happy path, но и ошибки/авторизацию
4. Новые модели импортированы в `conftest.py`
5. WebSocket broadcast замокан там, где нужно
