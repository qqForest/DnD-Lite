# Система сохранения сессий DnD Lite GM

## Обзор

Система сохранения позволяет экспортировать и импортировать игровые сессии в формате JSON. Это полезно для:
- Резервного копирования сессий
- Переноса сессий между серверами
- Восстановления после сбоев
- Шаринга пресетов персонажей и сессий

## Архитектура

Система построена на паттерне **Registry** с использованием протоколов Python:

```
app/services/persistence/
├── types.py              # IdMapping, ExportContext, ImportContext
├── registry.py           # SaveableRegistry (singleton)
├── serializers/
│   ├── base.py           # Saveable протокол
│   ├── player.py
│   ├── character.py
│   ├── item.py
│   ├── spell.py
│   └── combat.py
├── session_exporter.py   # Экспорт сессии
├── session_importer.py   # Импорт сессии
└── migrations.py         # Версионирование формата
```

### Ключевые компоненты

**SaveableRegistry** — singleton реестр сериализаторов. Автоматически управляет порядком экспорта/импорта на основе зависимостей.

**Saveable** — протокол, который должен реализовать каждый сериализатор:
- `entity_name()` — уникальное имя сущности
- `version()` — версия формата
- `dependencies()` — зависимости от других сущностей
- `export(context)` — экспорт в список словарей
- `import_(data, context)` — импорт из списка словарей
- `validate(data, context)` — валидация без импорта

**IdMapping** — маппинг старых ID на новые при импорте для корректной привязки внешних ключей.

## Формат экспорта

```json
{
  "format_version": "1.0",
  "exported_at": "2024-01-15T10:30:00Z",
  "session_info": {
    "code": "ABC123",
    "created_at": "2024-01-14T20:00:00Z"
  },
  "entities": {
    "players": {
      "version": 1,
      "data": [
        {
          "id": 1,
          "name": "Game Master",
          "is_gm": true
        },
        {
          "id": 2,
          "name": "Алекс",
          "is_gm": false
        }
      ]
    },
    "characters": {
      "version": 1,
      "data": [
        {
          "id": 1,
          "player_id": 2,
          "name": "Торин Дубощит",
          "class_name": "Fighter",
          "level": 5,
          "strength": 16,
          "dexterity": 12,
          "constitution": 14,
          "intelligence": 10,
          "wisdom": 13,
          "charisma": 8,
          "max_hp": 52,
          "current_hp": 45
        }
      ]
    },
    "items": {
      "version": 1,
      "data": [
        {
          "id": 1,
          "character_id": 1,
          "name": "Длинный меч +1",
          "description": "Магический меч с бонусом +1",
          "effects": {"attack_bonus": 1, "damage_bonus": 1},
          "is_equipped": true
        }
      ]
    },
    "spells": {
      "version": 1,
      "data": []
    },
    "combats": {
      "version": 1,
      "data": []
    }
  }
}
```

## API Endpoints

### POST /api/session/export

Экспортировать текущую сессию. **Только для GM.**

**Query параметры:**
- `token` (required) — GM токен

**Body (опционально):**
```json
{
  "include_combat": true
}
```

**Ответ:**
```json
{
  "success": true,
  "data": { /* данные экспорта */ }
}
```

### POST /api/session/export/download

Скачать экспорт как файл. **Только для GM.**

**Query параметры:**
- `token` (required) — GM токен

**Ответ:** JSON файл `dnd_session_{CODE}.json`

### POST /api/session/import

Импортировать сессию из JSON. Создаёт новую сессию с новыми токенами.

**Body:**
```json
{
  "data": { /* данные экспорта */ },
  "new_session_code": "CUSTOM"  // опционально
}
```

**Ответ:**
```json
{
  "success": true,
  "session_id": 5,
  "session_code": "XYZ789",
  "gm_token": "uuid-gm-token",
  "player_tokens": {
    "Game Master": "uuid-gm-token",
    "Алекс": "uuid-player-token"
  },
  "entity_counts": {
    "players": 2,
    "characters": 1,
    "items": 1,
    "spells": 0,
    "combats": 0
  },
  "warnings": [],
  "errors": []
}
```

### POST /api/session/validate

Валидация данных без импорта.

**Body:**
```json
{
  "data": { /* данные экспорта */ }
}
```

**Ответ:**
```json
{
  "is_valid": true,
  "format_version": "1.0",
  "entity_counts": {
    "players": 2,
    "characters": 1,
    "items": 1
  },
  "warnings": [],
  "errors": []
}
```

## Примеры использования

### Экспорт сессии (curl)

```bash
# Получить JSON
curl -X POST "http://localhost:8000/api/session/export?token=YOUR_GM_TOKEN" \
  -H "Content-Type: application/json"

# Скачать файл
curl -X POST "http://localhost:8000/api/session/export/download?token=YOUR_GM_TOKEN" \
  -H "Content-Type: application/json" \
  -o backup.json
```

### Импорт сессии (curl)

```bash
# Валидация перед импортом
curl -X POST "http://localhost:8000/api/session/validate" \
  -H "Content-Type: application/json" \
  -d @backup.json

# Импорт
curl -X POST "http://localhost:8000/api/session/import" \
  -H "Content-Type: application/json" \
  -d '{"data": '"$(cat backup.json)"'}'
```

### Python клиент

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Экспорт
response = requests.post(
    f"{BASE_URL}/session/export",
    params={"token": gm_token},
    json={"include_combat": True}
)
export_data = response.json()["data"]

# Сохранение в файл
with open("backup.json", "w") as f:
    json.dump(export_data, f, ensure_ascii=False, indent=2)

# Импорт
with open("backup.json") as f:
    data = json.load(f)

response = requests.post(
    f"{BASE_URL}/session/import",
    json={"data": data}
)
result = response.json()
print(f"New session code: {result['session_code']}")
print(f"GM token: {result['gm_token']}")
```

## Расширение системы

### Добавление новой сущности

1. Создайте модель SQLAlchemy в `app/models/`
2. Создайте сериализатор:

```python
# app/services/persistence/serializers/note.py
from typing import List, Dict, Any
from app.models.note import Note
from app.services.persistence.types import ExportContext, ImportContext
from app.services.persistence.registry import registry


@registry.register
class NoteSerializer:
    @classmethod
    def entity_name(cls) -> str:
        return "notes"

    @classmethod
    def version(cls) -> int:
        return 1

    @classmethod
    def dependencies(cls) -> List[str]:
        return ["characters"]  # если заметки привязаны к персонажам

    @classmethod
    def export(cls, context: ExportContext) -> List[Dict[str, Any]]:
        notes = context.db.query(Note).filter(...).all()
        return [{"id": n.id, "text": n.text, ...} for n in notes]

    @classmethod
    def import_(cls, data: List[Dict[str, Any]], context: ImportContext) -> int:
        count = 0
        for note_data in data:
            note = Note(...)
            context.db.add(note)
            context.db.flush()
            context.id_mapping.set("notes", note_data["id"], note.id)
            count += 1
        return count

    @classmethod
    def validate(cls, data: List[Dict[str, Any]], context: ImportContext) -> None:
        for i, note_data in enumerate(data):
            if "text" not in note_data:
                context.add_error(f"notes[{i}]: отсутствует поле 'text'")
```

3. Импортируйте в `app/services/persistence/serializers/__init__.py`:

```python
from app.services.persistence.serializers.note import NoteSerializer
```

Система автоматически подхватит новый сериализатор через Registry.

### Миграции формата

При изменении формата данных:

1. Увеличьте версию в сериализаторе
2. Обновите `CURRENT_FORMAT_VERSION` в `migrations.py`
3. Добавьте функцию миграции:

```python
# app/services/persistence/migrations.py

@register_migration("1.0", "1.1")
def migrate_1_0_to_1_1(data: Dict[str, Any]) -> Dict[str, Any]:
    """Добавляем armor_class к персонажам."""
    for char in data.get("entities", {}).get("characters", {}).get("data", []):
        char.setdefault("armor_class", 10)
    return data
```

## Версионирование

- **format_version** — версия общего формата экспорта
- **entity.version** — версия формата конкретной сущности

Система автоматически мигрирует данные при импорте.

## Ограничения

- Токены игроков генерируются заново при импорте
- GM создаётся автоматически с новой сессией
- Активные бои можно отключить при экспорте (`include_combat: false`)
