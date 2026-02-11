#!/bin/bash

# Скрипт диагностики проблем на VPS
# Запуск: bash scripts/diagnose-vps.sh

echo "=== DnD Lite GM - Диагностика VPS ==="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Проверка .env файла
echo "1. Проверка .env файла..."
if [ -f .env ]; then
    check_pass ".env файл существует"

    # Проверка SECRET_KEY
    if grep -q "SECRET_KEY=change-me-in-production" .env; then
        check_fail "SECRET_KEY не изменён! Установите уникальный ключ."
        echo "   Сгенерировать: python3 -c \"import secrets; print(secrets.token_hex(32))\""
    else
        check_pass "SECRET_KEY установлен"
    fi

    # Проверка JWT_SECRET_KEY
    if grep -q "JWT_SECRET_KEY=change-me-in-production" .env; then
        check_fail "JWT_SECRET_KEY не изменён! Установите уникальный ключ."
    else
        check_pass "JWT_SECRET_KEY установлен"
    fi
else
    check_fail ".env файл не найден!"
    echo "   Создайте .env из .env.example: cp .env.example .env"
fi
echo ""

# 2. Проверка Docker контейнера
echo "2. Проверка Docker контейнера..."
if command -v docker &> /dev/null; then
    if sudo docker compose ps | grep -q "Up"; then
        check_pass "Контейнер запущен"
    else
        check_fail "Контейнер не запущен"
        echo "   Запустить: sudo docker compose up -d"
    fi
else
    check_fail "Docker не установлен"
fi
echo ""

# 3. Проверка порта 8080
echo "3. Проверка порта 8080..."
if sudo netstat -tulpn 2>/dev/null | grep -q ":8080"; then
    check_pass "Приложение слушает на порту 8080"
elif ss -tulpn 2>/dev/null | grep -q ":8080"; then
    check_pass "Приложение слушает на порту 8080"
else
    check_fail "Порт 8080 не прослушивается"
    echo "   Проверить логи: sudo docker compose logs app"
fi
echo ""

# 4. Проверка API доступности
echo "4. Проверка API доступности..."
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
        check_pass "API отвечает (HTTP $HTTP_CODE)"
    else
        check_fail "API не отвечает или недоступен (HTTP $HTTP_CODE)"
    fi
else
    check_warn "curl не установлен, пропускаем проверку API"
fi
echo ""

# 5. Проверка базы данных
echo "5. Проверка базы данных..."
if [ -f dnd_lite.db ]; then
    SIZE=$(ls -lh dnd_lite.db | awk '{print $5}')
    check_pass "База данных существует (размер: $SIZE)"

    # Проверка таблиц
    if command -v sqlite3 &> /dev/null; then
        TABLES=$(sqlite3 dnd_lite.db ".tables" 2>/dev/null)
        if [[ $TABLES == *"users"* ]] && [[ $TABLES == *"sessions"* ]]; then
            check_pass "Таблицы созданы"
        else
            check_warn "Таблицы могут быть не созданы"
        fi
    fi
else
    check_fail "База данных не найдена"
    echo "   Она будет создана при первом запуске"
fi
echo ""

# 6. Проверка frontend build
echo "6. Проверка frontend build..."
if sudo docker compose exec -T app test -d /app/frontend/dist 2>/dev/null; then
    check_pass "Frontend собран внутри контейнера"
else
    check_fail "Frontend не собран"
    echo "   Пересобрать: sudo docker compose up -d --build"
fi
echo ""

# 7. Проверка логов на ошибки
echo "7. Проверка последних логов..."
if sudo docker compose logs app --tail=20 2>/dev/null | grep -i "error\|exception\|failed" | head -5; then
    check_warn "Обнаружены ошибки в логах (см. выше)"
    echo "   Полные логи: sudo docker compose logs app --tail=100"
else
    check_pass "Ошибок в последних логах не найдено"
fi
echo ""

# 8. Проверка nginx (если установлен)
echo "8. Проверка nginx (если используется)..."
if command -v nginx &> /dev/null; then
    if sudo nginx -t &>/dev/null; then
        check_pass "Nginx конфигурация корректна"
    else
        check_fail "Nginx конфигурация содержит ошибки"
        echo "   Проверить: sudo nginx -t"
    fi

    # Проверка что nginx запущен
    if systemctl is-active --quiet nginx 2>/dev/null; then
        check_pass "Nginx запущен"
    else
        check_warn "Nginx не запущен"
    fi
else
    check_warn "Nginx не установлен (может не требоваться)"
fi
echo ""

# Итоговые рекомендации
echo "=== Итоговые рекомендации ==="
echo ""

# Подсчёт проблем
ERRORS=$(grep -c "✗" /tmp/diagnose_output 2>/dev/null || echo "0")

if [ -f .env ] && grep -q "change-me-in-production" .env; then
    echo "🔴 КРИТИЧНО: Измените SECRET_KEY и JWT_SECRET_KEY в .env файле!"
    echo "   1. Сгенерировать ключи:"
    echo "      python3 -c \"import secrets; print('SECRET_KEY=' + secrets.token_hex(32))\""
    echo "      python3 -c \"import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))\""
    echo "   2. Обновить .env файл"
    echo "   3. Перезапустить: sudo docker compose down && sudo docker compose up -d"
    echo ""
fi

echo "Для просмотра подробных логов:"
echo "  sudo docker compose logs -f app"
echo ""
echo "Для полной переустановки:"
echo "  git pull origin main && sudo docker compose down && sudo docker compose up -d --build"
echo ""
