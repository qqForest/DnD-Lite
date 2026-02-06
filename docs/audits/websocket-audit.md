# Аудит WebSocket соединений GM-Сессия-Игрок

**Дата:** 2026-02-05
**Цель:** Выявление проблемных мест, где может быть прервано/сломано соединение при работе на VPS

---

## Резюме

Обнаружено **8 критических/высокоприоритетных** и **4 средних** проблемы, которые могут привести к:
- Разрывам соединений без корректной очистки
- Утечкам памяти
- Race conditions
- Потере данных при broadcast
- Невозможности переподключения

---

## Критические проблемы

### 1. Race condition в ConnectionManager

**Файл:** `app/websocket/manager.py:6-46`

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.token_to_player: Dict[str, int] = {}
        # НЕТ asyncio.Lock!
```

**Проблема:** Словари изменяются без синхронизации. При одновременном connect/disconnect или итерации во время broadcast:

```python
async def broadcast(self, data: dict, exclude_token: Optional[str] = None):
    for token, websocket in self.active_connections.items():  # <-- Может измениться
        # ...
```

**Последствия:**
- `RuntimeError: dictionary changed size during iteration`
- Утечки памяти: сокеты остаются после отключения
- Сообщения не доходят до части игроков

**Решение:** Добавить `asyncio.Lock()` для всех операций со словарями.

---

### 2. Отсутствие обработки ошибок при отправке

**Файл:** `app/websocket/manager.py:31-45`

```python
async def send_personal(self, token: str, data: dict):
    websocket = self.active_connections.get(token)
    if websocket:
        await websocket.send_json(data)  # <-- Нет try-except!

async def broadcast(self, data: dict, exclude_token: Optional[str] = None):
    for token, websocket in self.active_connections.items():
        try:
            await websocket.send_json(data)
        except Exception:
            pass  # <-- Соединение остаётся в active_connections!
```

**Проблема:** При ошибке отправки соединение НЕ удаляется из словаря. "Мёртвые" сокеты накапливаются.

**Последствия:**
- Утечка памяти
- Игрок не может переподключиться (токен "занят")
- Broadcast замедляется при отправке мёртвым сокетам

**Решение:** Удалять соединение из `active_connections` при ошибке отправки.

---

### 3. Отсутствие heartbeat/keep-alive механизма

**Файлы:** `app/main.py`, `app/websocket/manager.py`

**Проблема:** Нет ping-pong механизма. Если клиент потерял сеть без явного close:
1. TCP соединение "зависает"
2. Сервер не знает, что клиент отключился
3. Сокет остаётся "активным" неопределённо долго

**Последствия:**
- "Призраки" в списке подключённых
- Невозможность переподключения
- Broadcast пытается отправить сообщения мёртвым соединениям

**Решение:** Реализовать ping каждые 30 секунд с таймаутом pong 10 секунд.

---

### 4. Утечка ресурсов при исключениях до manager.connect()

**Файл:** `app/main.py:54-71`

```python
player = db.query(Player).filter(Player.token == token).first()
# Если исключение здесь ↓
print(f"WS Found player: {player.name}...")  # <-- unicode ошибка?
await manager.connect(websocket, token, player.id)  # <-- Не достигнется
```

**Проблема:** Если исключение между проверкой токена и `manager.connect()`, websocket никогда не будет принят, но ресурсы не освободятся.

**Решение:** Обернуть в try-except, явно закрывать websocket при ошибке.

---

## Высокоприоритетные проблемы

### 5. Недостаточная обработка WebSocketDisconnect

**Файл:** `app/main.py:82-114`

```python
while True:
    try:
        data = await websocket.receive_text()
        message = json.loads(data)
        await handle_message(db, token, player, message)
    except WebSocketDisconnect:
        raise
    except json.JSONDecodeError:
        await manager.send_personal(token, {...})  # <-- Цикл продолжается!
    except Exception as e:
        print(f"WS Processing Error: {str(e)}")
        # <-- Цикл продолжается при любой ошибке!
```

**Проблема:** При ошибках цикл не прерывается. Может привести к бесконечным циклам обработки ошибок.

**Решение:** Добавить счётчик ошибок, отключать после N ошибок подряд.

---

### 6. Один Database Session на всё время соединения

**Файл:** `app/main.py:55, 112`

```python
db = next(get_db())  # <-- Один session
try:
    # ... вся обработка WebSocket ...
finally:
    db.close()  # <-- Закрывается в конце
```

**Проблема:**
- Session может быть в несогласованном состоянии
- В `handlers.py` нет явных `db.commit()`
- Стейл данные при долгих соединениях

**Решение:** Создавать новый session для каждого сообщения или явно управлять транзакциями.

---

### 7. Молчаливое игнорирование ошибок broadcast

**Файл:** `app/websocket/manager.py:37-45`

```python
try:
    await websocket.send_json(data)
except Exception:
    pass  # <-- Ни логирования, ни очистки!
```

**Проблема:** Невозможно отладить проблемы с соединениями. Администратор не знает о потерях.

**Решение:** Логировать ошибки, удалять мёртвые соединения, уведомлять GM.

---

### 8. Отсутствие проверки состояния соединения

**Файл:** `app/websocket/manager.py:31-45`

```python
websocket = self.active_connections.get(token)
if websocket:
    await websocket.send_json(data)  # <-- Нет проверки состояния!
```

**Проблема:** Соединение может быть в состоянии CLOSING/CLOSED.

**Решение:** Проверять `websocket.application_state == WebSocketState.CONNECTED`.

---

## Средние проблемы

### 9. Отсутствие таймаута при receive_text()

**Файл:** `app/main.py:83`

```python
data = await websocket.receive_text()  # <-- Бесконечное ожидание
```

**Решение:** `asyncio.wait_for(websocket.receive_text(), timeout=300)`

---

### 10. Отсутствие лимита размера сообщения

**Файл:** `app/main.py:83`

```python
data = await websocket.receive_text()  # <-- Нет проверки размера
```

**Последствия:** DoS атака через огромные сообщения.

**Решение:** Проверять `len(data) > MAX_MESSAGE_SIZE` (например, 10KB).

---

### 11. Невозможность переподключения с тем же токеном

**Файл:** `app/api/session.py:126-137`

**Проблема:** При каждом join создаётся новый Player с новым токеном. Если соединение оборвалось:
1. Старый токен "занят" мёртвым соединением
2. Игрок не может продолжить с того же места
3. Нужно создавать нового Player

**Решение:** Логика reconnect или cleanup мёртвых соединений по таймауту.

---

### 12. Отсутствие обработки исключений в handlers

**Файл:** `app/websocket/handlers.py:9-25`

```python
handler = handlers.get(msg_type)
if handler:
    await handler(db, token, player, message.get("payload", {}))
    # <-- Исключение пойдёт выше без обработки
```

**Решение:** Оборачивать вызов handler в try-except, отправлять клиенту error.

---

## Матрица рисков

| # | Проблема | Тяжесть | Вероятность | Последствие |
|---|----------|---------|-------------|-------------|
| 1 | Race condition | Критическая | Средняя | Crash, утечка |
| 2 | Ошибки send | Высокая | Высокая | Утечка памяти |
| 3 | Нет heartbeat | Высокая | Высокая | Зависшие соединения |
| 4 | Утечка до connect | Критическая | Низкая | Исчерпание сокетов |
| 5 | Бесконечный цикл ошибок | Высокая | Средняя | Нагрузка CPU |
| 6 | Один DB session | Высокая | Средняя | Несогласованность |
| 7 | Нет логирования | Высокая | Высокая | Невозможно отладить |
| 8 | Нет проверки состояния | Средняя | Высокая | Исключения |
| 9 | Нет таймаута | Средняя | Средняя | Утечка потоков |
| 10 | Нет лимита размера | Средняя | Средняя | DoS |
| 11 | Нет reconnect | Высокая | Высокая | Плохой UX |
| 12 | Нет обработки в handlers | Средняя | Средняя | Зависание |

---

## Рекомендации по исправлению

### Приоритет 1 (Критично) — День 1

1. **asyncio.Lock в ConnectionManager**
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.token_to_player: Dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket, token, player_id):
        async with self._lock:
            # ...
```

2. **Удаление мёртвых соединений при ошибке**
```python
async def broadcast(self, data: dict, exclude_token: Optional[str] = None):
    dead_tokens = []
    async with self._lock:
        for token, websocket in self.active_connections.items():
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Failed to send to {token}: {e}")
                dead_tokens.append(token)

        for token in dead_tokens:
            self.active_connections.pop(token, None)
            self.token_to_player.pop(token, None)
```

3. **Heartbeat механизм**
```python
async def heartbeat_task(websocket, token):
    while True:
        await asyncio.sleep(30)
        try:
            await websocket.send_json({"type": "ping"})
        except:
            break
```

### Приоритет 2 (Высокий) — Неделя 1

4. Session per message в WebSocket handler
5. Счётчик ошибок с лимитом
6. Полное логирование через `logging` модуль

### Приоритет 3 (Средний) — Неделя 2

7. Таймаут на receive_text()
8. Лимит размера сообщения
9. Проверка состояния соединения
10. Логика reconnect

---

## Файлы требующие изменений

| Файл | Проблемы |
|------|----------|
| `app/websocket/manager.py` | #1, #2, #7, #8 |
| `app/main.py` | #3, #4, #5, #6, #9, #10 |
| `app/websocket/handlers.py` | #12 |
| `app/api/session.py` | #11 |

---

## Дополнительные рекомендации для VPS

- **Мониторинг:** Prometheus метрики на количество соединений, ошибок, latency
- **Ограничение:** Max соединений на IP (защита от DoS)
- **Graceful shutdown:** Корректное закрытие всех соединений при перезапуске
- **Load testing:** Симуляция 100+ одновременных игроков
- **Nginx proxy:** WebSocket timeout настройки, keepalive
