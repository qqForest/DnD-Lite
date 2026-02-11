# Инструкция по деплою и обновлению

Проект настроен для работы через Docker Compose. Фронтенд и бэкенд собираются в один контейнер, где FastAPI раздает статику.

## Требования
- Docker
- Docker Compose V2

---

## Первичная установка на VPS

### 1. Клонирование репозитория
```bash
git clone https://github.com/qqForest/DnD-Lite.git
cd DnD-Lite
```

### 2. Настройка .env файла (ОБЯЗАТЕЛЬНО!)

```bash
# Скопировать пример
cp .env.example .env

# Сгенерировать уникальные ключи
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"

# Отредактировать .env и вставить сгенерированные ключи
nano .env
```

**ВАЖНО:** Замените `change-me-in-production` на сгенерированные ключи! Иначе авторизация будет работать неправильно.

### 3. Запуск сборки
```bash
sudo docker compose up -d --build
```

### 4. Проверка
```bash
# Проверить что контейнер запущен
sudo docker compose ps

# Проверить логи
sudo docker compose logs -f app

# Диагностика проблем
bash scripts/diagnose-vps.sh
```

---

## Обновление приложения
Если вы внесли изменения в код и запушили их в GitHub, выполните эти команды на VPS для применения изменений:

### 1. Быстрое обновление (одной строкой)
```bash
git pull origin main && sudo docker compose up -d --build
```

### 2. Пошаговое обновление
```bash
# Подтянуть изменения из репозитория
git pull origin main

# Пересобрать образ и перезапустить контейнеры
# Смарт-сборка: пересоберет только то, что изменилось
sudo docker compose up -d --build

# Очистка старых неиспользуемых образов (чтобы не забивать диск)
sudo docker image prune -f
```

---

---

## Диагностика проблем

Если что-то не работает после деплоя:

```bash
# Автоматическая диагностика
bash scripts/diagnose-vps.sh

# Или вручную проверить логи
sudo docker compose logs -f app --tail=100
```

**Типичные проблемы:**
1. **Разлогинивает после перезагрузки** → Проверьте что SECRET_KEY и JWT_SECRET_KEY установлены в .env
2. **Создание сессии не работает** → Проверьте логи на ошибки: `sudo docker compose logs app`
3. **401 Unauthorized ошибки** → Очистите localStorage в браузере и перелогиньтесь

Подробнее: [docs/troubleshooting-vps.md](./troubleshooting-vps.md)

---

## Полезные команды

### Просмотр логов
```bash
# Все логи в реальном времени
sudo docker compose logs -f

# Логи только бэкенда
sudo docker compose logs -f app
```

### Статус контейнера
```bash
sudo docker compose ps
```

### Остановка проекта
```bash
sudo docker compose down
```

### Данные (База данных)
Файл базы данных `dnd_lite.db` проброшен из контейнера в корень папки проекта на хосте. 
При обновлении контейнера **данные сохраняются**.

Чтобы сделать бэкап, достаточно просто скопировать файл:
```bash
cp dnd_lite.db dnd_lite.db.bak
```
