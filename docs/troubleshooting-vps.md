# Troubleshooting на VPS

## Проблема: Создание сессии не работает, разлогинивает после перезагрузки

### Шаг 1: Проверка логов на VPS

```bash
# SSH на VPS
ssh user@your-vps-ip

# Перейти в папку проекта
cd ~/DnD-Lite  # или ваш путь

# Посмотреть логи контейнера
sudo docker compose logs -f app --tail=100
```

**Что искать в логах:**
- Ошибки при создании сессии (POST /api/session)
- 401 Unauthorized errors
- JWT validation errors
- Database errors
- CORS errors

---

### Шаг 2: Проверка .env файла на VPS

```bash
# Проверить что .env файл существует
cat .env

# Должно быть:
# SECRET_KEY=какой-то-уникальный-ключ (НЕ "change-me-in-production")
# JWT_SECRET_KEY=какой-то-уникальный-ключ (НЕ "change-me-in-production")
```

**ВАЖНО:** Если SECRET_KEY и JWT_SECRET_KEY = `change-me-in-production`, нужно их изменить!

```bash
# Сгенерировать случайные ключи
python3 -c "import secrets; print(secrets.token_hex(32))"
# Повторить два раза для двух ключей

# Отредактировать .env
nano .env
# Изменить SECRET_KEY и JWT_SECRET_KEY на сгенерированные

# Перезапустить контейнер
sudo docker compose down
sudo docker compose up -d --build
```

---

### Шаг 3: Проверка порта и доступности API

```bash
# Проверить что контейнер запущен
sudo docker compose ps

# Должно показать:
# NAME    IMAGE    COMMAND    SERVICE    STATUS    PORTS
# app     ...      ...        app        Up        (no ports if network_mode: host)

# Проверить что приложение слушает на 8080
sudo netstat -tulpn | grep 8080
# Должно показать: tcp  0  0.0.0.0:8080  0.0.0.0:*  LISTEN  <PID>/python

# Проверить что API отвечает
curl http://localhost:8080/api/session
# Должен вернуть 401 (не authenticated) - это нормально
```

---

### Шаг 4: Проверка nginx конфигурации (если используется)

Если перед Docker стоит nginx:

```bash
# Проверить nginx конфигурацию
sudo nginx -t

# Посмотреть конфигурацию для вашего сайта
sudo cat /etc/nginx/sites-enabled/dndlite  # или ваше имя
```

**Пример правильной конфигурации nginx:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Проксирование API и WebSocket
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Таймауты для WebSocket
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

---

### Шаг 5: Проверка базы данных

```bash
# Проверить что БД существует и не пустая
ls -lh dnd_lite.db

# Подключиться к БД и проверить таблицы
sqlite3 dnd_lite.db
> .tables
# Должны быть: users, sessions, players, characters, etc.

> SELECT COUNT(*) FROM users;
# Должен показать количество пользователей

> .quit
```

---

### Шаг 6: Проверка frontend build

```bash
# Проверить что frontend собран внутри контейнера
sudo docker compose exec app ls -la /app/frontend/dist

# Должны быть: index.html, assets/
```

---

## Типичные проблемы и решения

### Проблема 1: "Разлогинивает после перезагрузки"

**Причина:** JWT токены становятся невалидными.

**Решение:**
1. Проверить что `JWT_SECRET_KEY` в `.env` **не меняется** между перезапусками
2. Убедиться что `.env` файл существует на VPS и содержит правильные ключи
3. Перезапустить контейнер с правильными ключами

```bash
# Убедиться что .env существует
cat .env

# Если ключей нет, добавить:
nano .env
# Добавить уникальные ключи (сгенерировать через python3 -c "import secrets; print(secrets.token_hex(32))")

# Перезапустить
sudo docker compose down
sudo docker compose up -d --build
```

### Проблема 2: "Создание сессии не работает"

**Возможные причины:**
1. API не отвечает (проверить логи)
2. CORS блокирует запросы (проверить логи на CORS errors)
3. Database ошибки (проверить что dnd_lite.db существует и доступен)
4. Frontend не может достучаться до API (проверить network)

**Диагностика:**
```bash
# 1. Проверить что API отвечает
curl -X POST http://localhost:8080/api/session \
  -H "Content-Type: application/json" \
  -d '{}'

# Должен вернуть 401 или ошибку авторизации (но НЕ connection refused)

# 2. Проверить CORS
sudo docker compose logs app | grep CORS

# 3. Проверить database
sudo docker compose logs app | grep -i "database\|sqlite"

# 4. Проверить что frontend загружается
curl -I http://localhost:8080/
# Должен вернуть 200 OK и HTML
```

### Проблема 3: "WebSocket не подключается"

**Симптомы:** player_joined события не приходят, карта не обновляется в realtime.

**Решение:**
1. Проверить что nginx пропускает Upgrade headers (см. конфигурацию выше)
2. Проверить логи WebSocket подключений

```bash
sudo docker compose logs app | grep "WS "
# Должны быть: "WS Connection attempt", "WS Successfully connected"
```

---

## Полная переустановка (если ничего не помогло)

```bash
# Остановить и удалить контейнеры
sudo docker compose down

# Удалить старый образ
sudo docker image prune -a -f

# Пересобрать с нуля
git pull origin main
sudo docker compose up -d --build

# Проверить логи
sudo docker compose logs -f app
```

---

## Быстрый чеклист для проверки

- [ ] .env файл существует и содержит уникальные SECRET_KEY и JWT_SECRET_KEY
- [ ] Контейнер запущен (docker compose ps)
- [ ] Приложение слушает на 8080 (netstat -tulpn | grep 8080)
- [ ] API отвечает (curl http://localhost:8080/)
- [ ] База данных существует (ls dnd_lite.db)
- [ ] Frontend собран (docker compose exec app ls /app/frontend/dist)
- [ ] Логи не содержат ошибок (docker compose logs app --tail=50)
- [ ] Nginx правильно настроен (если используется)
