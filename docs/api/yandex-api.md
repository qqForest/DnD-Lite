# Yandex AI Studio SDK — Генерация изображений (YandexART)

Документация по интеграции YandexART через Python SDK для генерации изображений в проекте.

---

## Оглавление

1. [Установка](#установка)
2. [Аутентификация](#аутентификация)
3. [Инициализация SDK](#инициализация-sdk)
4. [Синхронный режим](#синхронный-режим)
5. [Асинхронный режим](#асинхронный-режим)
6. [Параметры конфигурации](#параметры-конфигурации)
7. [Форматы промпта](#форматы-промпта)
8. [Результат генерации](#результат-генерации)
9. [Комбинация YandexGPT + YandexART](#комбинация-yandexgpt--yandexart)
10. [Квоты и лимиты](#квоты-и-лимиты)
11. [Переменные окружения](#переменные-окружения)
12. [Полные примеры кода](#полные-примеры-кода)

---

## Установка

```bash
pip install yandex-ai-studio-sdk
```

Пакет: `yandex-ai-studio-sdk`
Импорт: `from yandex_ai_studio_sdk import AIStudio` (sync) или `from yandex_ai_studio_sdk import AsyncAIStudio` (async)

---

## Аутентификация

SDK поддерживает несколько способов аутентификации. Передаются через параметр `auth` при инициализации или через переменные окружения.

| Способ | Параметр `auth` | Переменная окружения |
|---|---|---|
| **API-ключ** (рекомендуется для серверов) | `auth="AQVN..."` | `YC_API_KEY` |
| **IAM-токен** | `auth="t1.9eu..."` | `YC_IAM_TOKEN` |
| **OAuth-токен** | `auth="y0_AgA..."` | `YC_OAUTH_TOKEN` |
| **Общий токен** | — | `YC_TOKEN` |

**Необходимые роли в Yandex Cloud IAM:**
- `ai.imageGeneration.user` — для генерации изображений
- `ai.languageModels.user` — если используется YandexGPT для генерации промптов

---

## Инициализация SDK

### Явная передача параметров

```python
from yandex_ai_studio_sdk import AIStudio

sdk = AIStudio(
    folder_id="b1gxxxxxxxxx",      # ID каталога в Yandex Cloud
    auth="AQVNxxxxxxxxxxxxxxxxx",   # API-ключ или токен
)
```

### Через переменные окружения

```python
from yandex_ai_studio_sdk import AIStudio

# folder_id берётся из YC_FOLDER_ID
# auth берётся из YC_API_KEY / YC_IAM_TOKEN / YC_OAUTH_TOKEN / YC_TOKEN
sdk = AIStudio()
```

### Включение логирования

```python
sdk.setup_default_logging()
```

---

## Синхронный режим

Используется класс `AIStudio`. Метод `run_deferred()` возвращает объект `Operation`, у которого вызывается `.wait()` для ожидания результата.

```python
from yandex_ai_studio_sdk import AIStudio
import pathlib

sdk = AIStudio(folder_id="<folder_id>", auth="<api_key>")

# Получение модели
model = sdk.models.image_generation("yandex-art")

# Конфигурация (опционально)
model = model.configure(width_ratio=1, height_ratio=2, seed=50)

# Генерация
operation = model.run_deferred("a red cat")
result = operation.wait()

# Сохранение в файл
path = pathlib.Path("image.jpeg")
path.write_bytes(result.image_bytes)
```

### Ключевые методы (sync)

| Метод | Описание |
|---|---|
| `sdk.models.image_generation("yandex-art")` | Получить модель генерации изображений |
| `model.configure(**kwargs)` | Сконфигурировать модель (возвращает новый экземпляр) |
| `model.run_deferred(messages)` | Запустить генерацию, возвращает `Operation` |
| `operation.wait()` | Дождаться результата, возвращает `ImageGenerationModelResult` |

---

## Асинхронный режим

Используется класс `AsyncAIStudio`. Все вызовы через `await`.

```python
import asyncio
from yandex_ai_studio_sdk import AsyncAIStudio
import pathlib

async def main():
    sdk = AsyncAIStudio(folder_id="<folder_id>", auth="<api_key>")

    model = sdk.models.image_generation("yandex-art")
    model = model.configure(width_ratio=1, height_ratio=2, seed=50)

    # Генерация
    operation = await model.run_deferred("a red cat")
    result = await operation

    # Сохранение
    path = pathlib.Path("image.jpeg")
    path.write_bytes(result.image_bytes)

asyncio.run(main())
```

### Ключевые методы (async)

| Метод | Описание |
|---|---|
| `sdk.models.image_generation("yandex-art")` | Получить модель (синхронный вызов) |
| `model.configure(**kwargs)` | Сконфигурировать модель (синхронный вызов) |
| `await model.run_deferred(messages)` | Запустить генерацию, возвращает `Operation` |
| `await operation` | Дождаться результата (`ImageGenerationModelResult`) |

---

## Параметры конфигурации

Передаются через метод `model.configure()`. Метод возвращает новый экземпляр модели с применёнными настройками.

```python
model = model.configure(
    width_ratio=1,    # Пропорция ширины (по умолчанию: 1)
    height_ratio=1,   # Пропорция высоты (по умолчанию: 1)
    seed=42,          # Зерно генерации для воспроизводимости
    mime_type="image/jpeg",  # Формат выходного изображения
)
```

### Параметры

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `width_ratio` | `int` | `1` | Пропорция ширины для соотношения сторон |
| `height_ratio` | `int` | `1` | Пропорция высоты для соотношения сторон |
| `seed` | `int` | случайный | Зерно генерации. Одинаковый seed + промпт = идентичный результат |
| `mime_type` | `str` | `"image/jpeg"` | Формат изображения. На данный момент поддерживается только `image/jpeg` |

### Соотношения сторон

Базовое разрешение: **1024 x 1024 пикселей**.
Размер может увеличиваться или уменьшаться в зависимости от заданного соотношения сторон, но **не более чем на 10%**.

Примеры:

| `width_ratio` | `height_ratio` | Результат |
|---|---|---|
| 1 | 1 | Квадрат (~1024x1024) |
| 1 | 2 | Вертикальный (~512x1024) |
| 2 | 1 | Горизонтальный (~1024x512) |
| 3 | 4 | Вертикальный (соотношение 3:4) |
| 16 | 9 | Широкоформатный (соотношение 16:9) |

### Модель

| Идентификатор SDK | URI модели | Описание |
|---|---|---|
| `"yandex-art"` | `art://<folder_id>/yandex-art/latest` | YandexART — генерация изображений методом каскадной диффузии |

---

## Форматы промпта

Метод `run_deferred()` принимает промпт в нескольких форматах:

### 1. Простая строка

```python
operation = model.run_deferred("красный кот на крыше")
```

### 2. Список строк

Все строки объединяются как описание генерации:

```python
operation = model.run_deferred(["красный кот", "стиль Миядзаки"])
```

### 3. Словарь с весом

Параметр `weight` задаёт приоритет фрагмента промпта:

```python
operation = model.run_deferred({"text": "красный кот", "weight": 5})
```

### 4. Список с комбинацией форматов

```python
operation = model.run_deferred([
    {"text": "красный кот", "weight": 5},
    "стиль Миядзаки",
    {"text": "акварель", "weight": 2},
])
```

### 5. Результат YandexGPT

Результат `gpt.run()` можно передать напрямую:

```python
gpt = sdk.models.completions("yandexgpt")
prompt = gpt.run(["создай промпт для yandexart", "красный кот в стиле Миядзаки"])
operation = model.run_deferred(prompt)
```

### Ограничения промпта

- Максимальная длина: **500 символов**

---

## Результат генерации

Метод `.wait()` (sync) или `await operation` (async) возвращает объект `ImageGenerationModelResult`:

```python
ImageGenerationModelResult(
    model_version='',
    image_bytes=<bytes>
)
```

### Поля результата

| Поле | Тип | Описание |
|---|---|---|
| `model_version` | `str` | Версия модели (может быть пустой строкой) |
| `image_bytes` | `bytes` | Бинарные данные изображения (JPEG) |

### Сохранение изображения

```python
import pathlib

result = operation.wait()
path = pathlib.Path("output.jpeg")
path.write_bytes(result.image_bytes)
```

### Кодирование в Base64

```python
import base64

result = operation.wait()
b64_string = base64.b64encode(result.image_bytes).decode("utf-8")
```

---

## Комбинация YandexGPT + YandexART

YandexGPT можно использовать для генерации детализированного промпта, который затем передаётся в YandexART:

### Sync

```python
sdk = AIStudio(folder_id="<folder_id>", auth="<api_key>")

# Шаг 1: Генерация промпта через YandexGPT
gpt = sdk.models.completions("yandexgpt")
messages = gpt.run([
    "создай детальный промпт для генерации изображения",
    "красный кот в стиле аниме Миядзаки"
])
print(messages)

# Шаг 2: Генерация изображения
art = sdk.models.image_generation("yandex-art")
operation = art.run_deferred(messages)
result = operation.wait()
```

### Async

```python
sdk = AsyncAIStudio(folder_id="<folder_id>", auth="<api_key>")

gpt = sdk.models.completions("yandexgpt")
messages = await gpt.run([
    "создай детальный промпт для генерации изображения",
    "красный кот в стиле аниме Миядзаки"
])

art = sdk.models.image_generation("yandex-art")
operation = await art.run_deferred(messages)
result = await operation
```

**Необходимая роль:** `ai.languageModels.user` (дополнительно к `ai.imageGeneration.user`)

---

## Квоты и лимиты

| Ограничение | Значение |
|---|---|
| Запросов на генерацию в минуту | 500 |
| Запросов на генерацию в день | 5 000 |
| Запросов на получение результата в секунду | 50 |
| Максимальная длина промпта | 500 символов |
| Формат выходного изображения | только `image/jpeg` |
| Базовое разрешение | 1024 x 1024 px |
| Отклонение от базового разрешения | не более 10% |

---

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YC_FOLDER_ID` | ID каталога Yandex Cloud |
| `YC_API_KEY` | API-ключ сервисного аккаунта |
| `YC_IAM_TOKEN` | IAM-токен |
| `YC_OAUTH_TOKEN` | OAuth-токен |
| `YC_TOKEN` | Общий токен (fallback) |

SDK автоматически определяет тип аутентификации в порядке приоритета:
1. Явно переданный `auth` параметр
2. `YC_API_KEY`
3. `YC_IAM_TOKEN`
4. `YC_OAUTH_TOKEN`
5. `YC_TOKEN`
6. Metadata service (внутри Yandex Cloud VM)

---

## Полные примеры кода

### Sync — Полный пример

```python
#!/usr/bin/env python3
from __future__ import annotations

import pathlib
from yandex_ai_studio_sdk import AIStudio


def main() -> None:
    sdk = AIStudio(
        folder_id="<YC_FOLDER_ID>",
        auth="<YC_API_KEY>",
    )
    sdk.setup_default_logging()

    model = sdk.models.image_generation("yandex-art")

    # Конфигурация модели для всех последующих запросов
    model = model.configure(width_ratio=1, height_ratio=2, seed=50)

    # Простой запрос
    operation = model.run_deferred("a red cat")
    result = operation.wait()
    print(result)

    # Запрос с несколькими сообщениями
    operation = model.run_deferred(["a red cat", "Miyazaki style"])
    result = operation.wait()
    print(result)

    # Сохранение в файл
    path = pathlib.Path("image.jpeg")
    operation = model.run_deferred(["a red cat", "Miyazaki style"])
    result = operation.wait()
    path.write_bytes(result.image_bytes)

    # Комбинация YandexGPT + YandexART
    gpt = sdk.models.completions("yandexgpt")
    messages = gpt.run([
        "you need to create a prompt for a yandexart model",
        "of a cat in a Miyazaki style",
    ])
    print(messages)

    operation = model.run_deferred(messages)
    result = operation.wait()
    print(result)


if __name__ == "__main__":
    main()
```

### Async — Полный пример

```python
#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import pathlib
from yandex_ai_studio_sdk import AsyncAIStudio


async def main() -> None:
    sdk = AsyncAIStudio(
        folder_id="<YC_FOLDER_ID>",
        auth="<YC_API_KEY>",
    )
    sdk.setup_default_logging()

    model = sdk.models.image_generation("yandex-art")
    model = model.configure(width_ratio=1, height_ratio=2, seed=50)

    # Простой запрос
    operation = await model.run_deferred("a red cat")
    result = await operation
    print(result)

    # Несколько сообщений
    operation = await model.run_deferred(["a red cat", "Miyazaki style"])
    result = await operation
    print(result)

    # Сохранение в файл
    path = pathlib.Path("image.jpeg")
    operation = await model.run_deferred(["a red cat", "Miyazaki style"])
    result = await operation
    path.write_bytes(result.image_bytes)

    # Комбинация YandexGPT + YandexART
    gpt = sdk.models.completions("yandexgpt")
    messages = await gpt.run([
        "you need to create a prompt for a yandexart model",
        "of a cat in a Miyazaki style",
    ])
    print(messages)

    operation = await model.run_deferred(messages)
    result = await operation
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Ссылки

- [Официальная документация YandexART](https://yandex.cloud/ru/docs/ai-studio/operations/generation/yandexart-request)
- [SDK GitHub-репозиторий](https://github.com/yandex-cloud/yandex-cloud-ml-sdk)
- [Модели генерации](https://yandex.cloud/en/docs/ai-studio/concepts/generation/models)
- [Квоты и лимиты](https://yandex.cloud/en/docs/ai-studio/concepts/limits)
- [Тарификация](https://yandex.cloud/en/docs/ai-studio/pricing)
- [Примеры в репозитории (sync)](https://github.com/yandex-cloud/yandex-cloud-ml-sdk/tree/master/examples/sync/image_generation)
- [Примеры в репозитории (async)](https://github.com/yandex-cloud/yandex-cloud-ml-sdk/tree/master/examples/async/image_generation)
