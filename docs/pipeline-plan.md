# План дореализации полного пайплайна

Что нужно реализовать, чтобы все пути пользователя работали от начала до конца.

---

## 1. Создание персонажа (User-level)

**Сейчас**: кнопка "+" показывает toast "будет доступно в следующем обновлении"
**Нужно**: полноценная форма создания

### Задачи

- [ ] **CreateCharacterView** (`/profile/characters/create`)
  - Форма: имя, класс, уровень (1-20), характеристики (СИЛ/ЛОВ/ТЕЛ/ИНТ/МДР/ХАР), HP
  - Валидация: имя обязательно (1-100 символов), характеристики 1-30, HP >= 1, уровень 1-20
  - Опционально: выбор шаблона класса (переиспользовать существующий `templatesApi`) для предзаполнения характеристик
  - Вызов `userCharactersApi.create()` → редирект на `/profile`
  - Кнопка "Отмена" → назад на `/profile`

- [ ] **Маршрут** в router: `/profile/characters/create` → `CreateCharacterView`, `meta: { requiresUser: true }`

- [ ] **Убрать toast** из AddCard в секции "Мои персонажи", заменить на `router.push({ name: 'create-character' })`

---

## 2. Создание NPC (User-level)

**Сейчас**: кнопка "+" показывает toast
**Нужно**: та же форма создания, но с `is_npc: true`

### Задачи

- [ ] **CreateNpcView** (`/profile/npcs/create`) — либо тот же `CreateCharacterView` с query-параметром `?npc=true`
  - Если отдельный view — дублирование. Лучше один `CreateCharacterView` с prop/query `isNpc`
  - При `isNpc=true` → отправляет `is_npc: true` в `userCharactersApi.create()`
  - Заголовок формы: "Новый NPC" вместо "Новый персонаж"

- [ ] **Маршрут**: `/profile/characters/create?npc=true` (или `/profile/npcs/create` → тот же компонент)

- [ ] **Убрать toast** из AddCard в секции NPC

---

## 3. Создание карты (User-level)

**Сейчас**: кнопка "+" показывает toast
**Нужно**: форма создания карты

### Задачи

- [ ] **CreateMapView** (`/profile/maps/create`)
  - Форма: название, ширина (default 1920), высота (default 1080), размер сетки (default 50), URL фона (опционально)
  - Валидация: название обязательно, ширина/высота >= 100, grid_scale >= 10
  - Вызов `userMapsApi.create()` → редирект на `/profile`

- [ ] **Маршрут**: `/profile/maps/create` → `CreateMapView`, `meta: { requiresUser: true }`

- [ ] **Убрать toast** из AddCard в секции карт

---

## 4. Редактирование персонажа/NPC

**Сейчас**: только просмотр и удаление
**Нужно**: возможность изменять характеристики

### Задачи

- [ ] **EditCharacterView** (`/profile/characters/:id/edit`)
  - Загрузка данных через `userCharactersApi.get(id)`
  - Та же форма что и создание, но предзаполнена
  - Кнопка "Сохранить" → `userCharactersApi.update(id, data)` → редирект на `/profile`
  - Валидация: те же правила что при создании
  - Проверка владельца (backend уже фильтрует по user_id)

- [ ] **Маршрут**: `/profile/characters/:id/edit`

- [ ] **UserCharacterCard**: добавить кнопку редактирования (иконка карандаша) рядом с кнопкой удаления, клик → `router.push({ name: 'edit-character', params: { id } })`

---

## 5. Подключение к сессии (JoinSessionView)

**Сейчас**: работает, но есть нюансы
**Нужно**: доработки

### Задачи

- [ ] **Валидация**: если персонажей нет — показать сообщение "Создайте персонажа перед присоединением" + ссылку на создание
- [ ] **Отсутствие персонажа**: разрешить join без персонажа (уже работает на backend), но показать предупреждение "Вы войдёте без персонажа"
- [ ] **Ошибки backend**: корректно показывать "Сессия не найдена", "Имя уже занято" из ответа API (уже частично есть)
- [ ] **Предзаполнение имени**: уже берётся из `authStore.user?.display_name` — ок
- [ ] **Обработка `character_id` в ответе**: если вернулся `character_id` — сохранить для дальнейшего использования в PlayerLobbyView (например, автовыбор персонажа)

---

## 6. Создание сессии (GM из профиля)

**Сейчас**: кнопка в ProfileView вызывает `sessionStore.createSession()` → `/gm/lobby`
**Нужно**: проверить и доработать

### Задачи

- [ ] **Привязка user_id к GM**: при создании сессии — сохранять `user_id` текущего пользователя в GM Player (backend уже поддерживает `Player.user_id`, но при createSession оно не устанавливается)
- [ ] **Импорт NPC в сессию**: в GM Lobby добавить возможность импортировать user-level NPC (UserCharacter с is_npc=true) в сессию как session Character
  - Кнопка "Импортировать NPC из профиля" в NPCSection
  - Модалка с выбором из `profileStore.npcCharacters`
  - При выборе: создавать session Character через `charactersApi.create()` с данными из UserCharacter
- [ ] **Импорт карты в сессию**: в GM View или GM Lobby добавить возможность импортировать UserMap как session Map
  - Кнопка "Загрузить карту из профиля"
  - Модалка с выбором из `profileStore.maps`
  - При выборе: `mapsApi.create()` с данными из UserMap

---

## 7. Валидации (сводная)

### Frontend

- [ ] **CreateCharacterView**: имя 1-100, уровень 1-20, характеристики 1-30, max_hp >= 1, current_hp >= 0 и <= max_hp
- [ ] **CreateMapView**: название 1-200, ширина/высота >= 100, grid_scale >= 10
- [ ] **JoinSessionView**: код >= 6 символов, имя > 0 символов
- [ ] **Inline-валидация**: показывать ошибки под полями в реальном времени, а не только при submit
- [ ] **Подтверждение удаления**: диалог "Вы уверены?" перед удалением персонажа/карты/NPC

### Backend (уже реализовано через Pydantic)

- Все Field constraints в схемах UserCharacterCreate, UserCharacterUpdate, UserMapCreate, UserMapUpdate
- Проверка владельца (user_id) во всех CRUD операциях

---

## 8. Редиректы и навигация (сводная)

### Уже работает

- `/login`, `/register` → если залогинен, редирект на `/`
- `/`, `/profile`, `/join` → если не залогинен, редирект на `/login`
- `/gm/lobby` ↔ `/gm` → автоматический редирект по состоянию `session_started`
- `/play/lobby` ↔ `/play` → аналогично
- Роль GM не может попасть на player-маршруты и наоборот

### Нужно добавить

- [ ] `/profile/characters/create` → `meta: { requiresUser: true }`
- [ ] `/profile/characters/:id/edit` → `meta: { requiresUser: true }`
- [ ] `/profile/maps/create` → `meta: { requiresUser: true }`
- [ ] `/profile/npcs/create` → `meta: { requiresUser: true }` (если отдельный маршрут)
- [ ] После создания/редактирования → редирект на `/profile`
- [ ] Кнопка "Назад" на всех create/edit view → `/profile`
- [ ] **Выход из сессии**: кнопка в GM/Player views для возврата на `/profile` с очисткой session store
- [ ] **Подтверждение выхода**: "Вы уверены, что хотите покинуть сессию?"

---

## 9. UX-улучшения (по приоритету)

- [ ] **Loading states**: спиннеры на кнопках при загрузке (в AddCard, при сохранении формы)
- [ ] **Toast-система**: переиспользуемый компонент Toast вместо inline-toast в ProfileView
- [ ] **Empty states**: красивые заглушки когда списки пустые ("У вас пока нет персонажей")
- [ ] **Подтверждение удаления**: модалка вместо мгновенного удаления

---

## Порядок реализации (рекомендуемый)

| Шаг | Задача | Зависимости |
|-----|--------|-------------|
| 1 | CreateCharacterView + маршрут | — |
| 2 | NPC-режим в CreateCharacterView | Шаг 1 |
| 3 | CreateMapView + маршрут | — |
| 4 | EditCharacterView + маршрут | Шаг 1 |
| 5 | Inline-валидация в формах | Шаги 1-4 |
| 6 | Подтверждение удаления | — |
| 7 | Доработка JoinSessionView | — |
| 8 | Импорт NPC из профиля в сессию (GM Lobby) | Шаг 2 |
| 9 | Импорт карты из профиля в сессию | Шаг 3 |
| 10 | Привязка user_id к GM при создании сессии | — |
| 11 | Кнопка выхода из сессии | — |
| 12 | Toast-система, loading states, empty states | — |
