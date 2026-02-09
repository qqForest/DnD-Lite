2026-02-09: Редизайн создания/редактирования персонажей — 3-шаговый визард
  - CreateCharacterView: переписан как пошаговый визард (класс → аватар → предпросмотр)
  - Шаг 1: карусель классов (TemplateCarousel + ClassCard) с свайпом, выбор класса и ввод имени
  - Шаг 2: генерация аватара через YandexART (textarea описания + кнопка генерации), возможность пропустить
  - Шаг 3: предпросмотр CharacterFlipCard (тап → оборот), кнопка «Готово»
  - Все характеристики берутся из шаблона класса автоматически, без ручной настройки
  - ClassCard.vue: портретная карточка класса (3:4, градиент по классу, hit die badge, описание)
  - TemplateCarousel.vue: свайп-карусель классов по паттерну CharacterCarousel (доты, touch-жесты)
  - EditCharacterView: упрощён — только FlipCard-превью, имя, описание внешности, перегенерация аватара
  - Убраны: класс, уровень, 6 характеристик, HP поля из редактора
  - TopBar с ArrowLeft и степ-индикатором (1/3, 2/3, 3/3) + dot-навигация
  - Мобильный стиль: max-width 480px, 100dvh, touch-friendly

2026-02-09: Редизайн главной страницы → Дашборд (мобильный стиль)
  - Маршрут '/' → redirect на '/dashboard', name 'home' → 'dashboard' во всех файлах
  - DashboardTopBar: топ-бар с гамбургер-меню и заголовком «Дашборд» (Cinzel)
  - DashboardSidebar: выдвижной сайдбар с профилем пользователя, навигацией и выходом
  - HomeView переделан: лого DnD Lite (Cinzel, крупный), карточка пользователя (имя + роль-бейдж + «Мой профиль»)
  - Кнопки «Быстрое подключение» (player) и «Создать сессию» (GM) на полную ширину с иконками
  - Статистика: компактные карточки с числами в Cinzel
  - Топ персонажей: ранги, имена и классы в стиле Cinzel
  - Убрана карточка «Новый персонаж» (дублирует функцию в профиле)
  - Убран старый header (лого + greeting + ghost-кнопки)
  - max-width: 480px, touch-friendly, 100dvh

2026-02-09: CI/CD — GitHub Actions (тесты + деплой на VPS)
  - Создан .github/workflows/deploy.yml
  - Job test: Python 3.11, pip install, pytest — запускается на push и PR в main
  - Job deploy: SSH на VPS, git pull, docker compose up — только при push в main после успешных тестов
  - Секреты: VPS_HOST, VPS_USER, VPS_SSH_KEY, VPS_PORT
  - CLAUDE.md: добавлен раздел CI/CD

2026-02-09: Документация стандарта тестирования
  - Создан docs/testing.md — регламент написания тестов (структура, паттерны, фикстуры, чеклист)
  - CLAUDE.md: добавлен раздел «Тестирование бэкенда» с командами и ссылкой на регламент
  - Правило: любое изменение бэкенда обязательно сопровождается тестами

2026-02-09: Полное покрытие бэкенда тестами (206 тестов)
  - Инфраструктура: pytest + pytest-asyncio + httpx, conftest с фикстурами (in-memory SQLite, транзакционный rollback)
  - Unit-тесты: abilities, class_templates, auth (JWT/bcrypt), dice_service (парсинг, броски, advantage/disadvantage)
  - Интеграционные тесты сервисов: ModifierService, CombatService (инициатива, ходы, урон/лечение)
  - API тесты: session, users, characters, templates, dice, combat, maps, user_characters, user_maps, persistence (export/import)
  - WebSocket тесты: подключение/отказ, roll_dice, chat, обработка ошибок (невалидный JSON, неизвестный тип)
  - Итого: 65 unit + 141 integration = 206 тестов, все проходят

2026-02-07: Редизайн PlayerView (игровой интерфейс игрока) для мобильных
  - CharacterFlipCard: добавлен проп compact для мини-карточки (120px, уменьшенные шрифты/статы, скрыты кнопки)
  - PlayerView: нижний блок заменён на character-bar (инвентарь-заглушка + мини FlipCard + индикатор движения) + кнопка «Бросок» + последний результат
  - GameMap: реализован pinch-to-zoom через нативные touch-события (двупальцевый зум к центру пинча + pan)
  - PlayerSidebar: заголовок шрифтом Cinzel, кнопка закрытия 44px (тач-таргет)
  - Убраны CharacterSheet и PlayerDiceSelector из PlayerView, логика инлайнена

2026-02-06: Редизайн PlayerLobbyView для мобильных устройств
  - PlayerLobbyTopBar: топ-бар с гамбургер-меню и заголовком «Лобби» шрифтом Cinzel
  - PlayerLobbySidebar: выдвижной сайдбар со статусом подключения и кнопкой «Покинуть сессию»
  - CharacterFlipCard вместо CharacterCard — flip-карточка персонажа (readonly, без edit/delete)
  - Инлайн кнопка «Готов» с иконками CheckCircle/Circle вместо отдельного ReadyButton
  - Счётчик «X из Y игроков готовы» под кнопкой
  - Исправлен баг: кнопка «Готов» была disabled из-за отсутствия charactersStore.selectedId — добавлен авто-select персонажа в onMounted
  - Убраны: SessionCodeDisplay, BasePanel-обёртка, блок «Ожидание начала игры»

2026-02-06: Редизайн JoinSessionView для мобильных устройств
  - Карусель flip-карточек (CharacterCarousel) вместо грида UserCharacterCard для выбора персонажа
  - CharacterCarousel: добавлен проп readonly (скрывает кнопки edit/delete) и expose currentIndex
  - Убрано поле ввода имени — берётся автоматически из аккаунта (display_name)
  - Вход без персонажа заблокирован — кнопка disabled если нет персонажей
  - Стилизованное поле кода комнаты: monospace, uppercase, крупный шрифт, по центру
  - Экран «Подключение...» с CSS-спиннером при загрузке
  - Пустое состояние: текст + кнопка «Создать персонажа»
  - Заголовок шрифтом Cinzel

2026-02-06: Редизайн профиля игрока для мобильных устройств
  - Подключён шрифт Cinzel через Google Fonts (ранее объявлен в tokens.css, но не загружался)
  - CharacterFlipCard: flip-карточка с аватаром на лицевой стороне и характеристиками/HP на обратной
  - CharacterCarousel: свайп-карусель персонажей с точечными индикаторами и touch-жестами
  - ProfileTopBar: топ-бар с гамбургер-меню и заголовком шрифтом Cinzel
  - ProfileSidebar: выдвижной сайдбар с информацией о пользователе, навигацией и выходом
  - useSwipe composable: обработка свайпов через Pointer Events (touch + desktop)
  - ProfileView переделан: карусель вместо грида, кнопки на полную ширину, touch-friendly
  - BaseButton: min-height 44px на мобильных для удобного тапа
  - GM-секция (карты, NPC, создание сессии) без изменений

2026-02-06: Редактор карт в профиле GM + сохранение карты из сессии
  - Backend: Модель UserMapToken (type, x, y, scale, rotation, label, color, icon, layer) + relationship в UserMap
  - Backend: Поле source_user_map_id в Map для отслеживания связи сессионной карты с UserMap
  - Backend: Миграция для source_user_map_id + автосоздание таблицы user_map_tokens
  - Backend: Pydantic-схемы UserMapTokenCreate/Update/Response, обновлён UserMapResponse с tokens
  - Backend: API token CRUD для редактора — POST /me/maps/{id}/tokens, PATCH /me/maps/tokens/{id}, DELETE /me/maps/tokens/{id}
  - Backend: Копирование UserMapTokens при создании сессии (UserMap → Map + MapTokens)
  - Backend: Endpoint POST /maps/{map_id}/save-to-library — GM сохраняет сессионную карту обратно в библиотеку (без токенов игроков)
  - Frontend: Store mapEditor (loadMap, addToken, updateToken, deleteToken, activeMapForCanvas computed)
  - Frontend: GameMap.vue — editorMode prop (displayMap, emit editor-* событий вместо mapStore, пропуск WS/fetch)
  - Frontend: AddTokenModal — hideCharacterTab prop (скрывает вкладку персонажей в редакторе)
  - Frontend: EditMapView — страница редактора карты (/profile/maps/:id/edit), Konva-канвас с тулбаром
  - Frontend: Кнопка "Редактировать" (✎) на UserMapCard, навигация из ProfileView
  - Frontend: Кнопка "Сохранить в библиотеку" (Save) в тулбаре карты во время игровой сессии (только GM)
  - Токены игроков (character_id != null) не сохраняются в библиотеку — они сессионные

2026-02-06: Отображение аватаров персонажей во всём интерфейсе
  - CharacterCard: автоматически показывает avatar_url из Character без явного пропа
  - Лобби GM (PlayersLobbyList): аватар в карточке персонажа при раскрытии игрока
  - Лобби игрока (PlayerLobbyView): аватар в карточке персонажа
  - Интерфейс игрока (PlayerView): аватар в нижней панели с персонажем
  - Панель GM (PlayersTab): мини-аватар (32px) рядом с именем игрока + имя персонажа
  - Редактор персонажа (EditCharacterView): большой аватар 160px по центру с именем под ним

2026-02-06: Генерация аватара персонажа через YandexART
  - Backend: Поля appearance (Text) и avatar_url (String) в моделях UserCharacter и Character + миграции
  - Backend: Сервис app/services/avatar.py — генерация через YandexART SDK (yandex-cloud-ml-sdk), сохранение в uploads/avatars/
  - Backend: Стилевой промпт D&D 5e в app/core/avatar.py
  - Backend: Эндпоинты POST /me/characters/{id}/generate-avatar и POST /characters/{id}/generate-avatar
  - Backend: Копирование appearance и avatar_url при join сессии (UserCharacter → Character)
  - Frontend: Поле описания внешности в CreateCharacterView и EditCharacterView
  - Frontend: Секция «Внешность и аватар» в EditCharacterView с превью, кнопкой генерации и спиннером
  - Frontend: MapToken — аватар персонажа в круглом токене через Konva clipFunc + v-image (вместо цветного круга)
  - Frontend: UserCharacterCard — маленький аватар-превью рядом с именем
  - Frontend: API методы generateAvatar в userCharactersApi и charactersApi

2026-02-06: Редизайн управления картой + контекстное меню токенов
  - Тулбар карты: иконки lucide (Maximize2, ZoomIn, ZoomOut, Plus) вместо текстовых кнопок, стилизация под дизайн-систему
  - ПКМ на токене (только GM): контекстное меню с опциями «Удалить» и «Убить» (для монстров)
  - Подтверждение через ConfirmModal перед удалением/убийством токена
  - Меню позиционируется у курсора, закрывается по клику вне области
  - Vite proxy: добавлен /uploads → backend для dev-режима (фоновые изображения)

2026-02-06: Загрузка фоновых изображений для карт + рендеринг на canvas
  - Backend: Endpoint POST /me/maps/upload-background — загрузка JPG/PNG (макс. 10МБ), определение размеров через Pillow, сохранение в uploads/maps/
  - Backend: Раздача загруженных файлов через StaticFiles mount /uploads
  - Frontend: CreateMapView — зона drag&drop загрузки вместо текстового поля URL, автоподстановка width/height из разрешения изображения, превью
  - Frontend: GameMap.vue — рендеринг background_url через Konva v-image поверх серого фона, под сеткой
  - Frontend: UserMapCard — превью фона карты, кнопка "Загрузить/Сменить фон" при наведении
  - Frontend: ProfileView — загрузка фона для существующих карт с обновлением размеров
  - Frontend: API методы uploadBackground (FormData) и update (PATCH) в userMapsApi
  - Добавлен тип UserMapUpdate в models.ts

2026-02-06: Обновлён CLAUDE.md до актуального состояния кодовой базы
  - Добавлена полная структура backend (10 API роутеров, 10 моделей, 4 сервиса)
  - Добавлена структура frontend (11 views, 7 Pinia stores, компоненты по категориям)
  - Добавлены секции: аутентификация (JWT + аккаунты), система карт, деплой
  - Обновлены модели (User, UserCharacter, UserMap, Map, MapToken, InitiativeRoll)
  - Обновлены WebSocket события (20 серверных + 3 клиентских)
  - Обновлены сервисы (добавлен PersistenceService)

2026-02-06: Фентези-иконки для токенов карты + шаблоны объектов
  - Backend: Поле icon в модели MapToken + миграция + Pydantic-схемы + API (create/update/broadcast)
  - Frontend: Каталог из 15 SVG-иконок с game-icons.net (CC BY 3.0): сундук, бочка, костёр, дверь, ловушка, камень, факел, алтарь, зелье, свиток, кристалл, череп, дерево, ключ, книга
  - Frontend: MapToken.vue — белый SVG-силуэт иконки поверх цветного круга через Konva v-path
  - Frontend: AddTokenModal — таб "Произвольный" с двумя подрежимами: "Шаблоны" (сетка 3x5 готовых объектов с preview) и "Ручной" (существующие поля + выбор иконки из каталога)
  - Frontend: При выборе шаблона автоматически заполняются label/color/icon/type
  - Frontend: Ручной режим без иконки — обычный цветной круг (как раньше)
  - Токены персонажей не затронуты — отображаются как цветные круги с именами

2026-02-06: Исправлен бесконечный цикл переподключений WebSocket на VPS
  - Причина 1: отсутствовал import asyncio в main.py после мержа — heartbeat/timeout код падал с NameError сразу после подключения, WS закрывался, клиент переподключался бесконечно
  - Причина 2: disconnect() в websocket.ts вызывал ws.close(), но async onclose запускал attemptReconnect(), создавая каскад лишних подключений
  - Исправление: добавлен import asyncio, убраны дублированные импорты в main.py
  - Исправление: disconnect() обнуляет onclose/onerror/onmessage перед close() чтобы предотвратить auto-reconnect

2026-02-06: Исправлена потеря состояния сессии при обновлении страницы
  - isGm не сохранялся в localStorage → после F5 роутер считал GM игроком и перенаправлял
  - Backend: добавлено поле is_gm в SessionState ответ GET /session
  - Frontend: isGm персистится в localStorage и восстанавливается из fetchSessionState
  - Роутер корректно определяет роль после перезагрузки страницы

2026-02-06: Исправлен статус "Отключено" и невидимость игроков у ГМ на VPS
  - Причина: при перезагрузке страницы useWebSocket подключал WS напрямую через wsService, минуя session store
  - Обработчики session store (player_joined, player_left, etc.) не регистрировались → новые игроки не появлялись
  - sessionStore.isConnected не обновлялся → статус показывал "Отключено"
  - Исправление: вынесен setupWebSocketHandlers() из connectWebSocket(), вызывается из useWebSocket composable
  - useWebSocket теперь использует sessionStore.connectWebSocket() вместо прямого wsService.connect()
  - Добавлена защита от двойного переподключения через wsService.isActiveFor(token)

2026-02-06: Исправлен баг дублирования токенов у ГМ при перемещении игроком
  - Причина: race condition между REST-ответом и WebSocket-событием token_added при создании токена
  - WS-событие приходило раньше REST-ответа, создавая вторую копию токена в массиве
  - Дубликат был невидим (обе копии на одной позиции), проявлялся при перемещении одной из них
  - Исправление: добавлен exclude_token для broadcast token_added и map_created
  - Дополнительно: dedup-проверки в store при addToken и createMap на фронтенде

2026-02-06: Исправлена ошибка 405 при POST/PATCH/DELETE запросах на VPS
  - Причина: catch-all маршрут @app.get("/{full_path:path}") для SPA перехватывал все пути, но только для GET — POST/PATCH/DELETE возвращали 405 Method Not Allowed
  - Исправление: заменён catch-all GET маршрут на exception handler для StarletteHTTPException
  - API маршруты (/api/*, /ws) возвращают JSON-ошибки как обычно
  - Не-API 404 ошибки отдают index.html для SPA-роутинга
  - Работает корректно для всех HTTP методов на всех маршрутах

2026-02-06: Привязка токенов к персонажам и управление движением игроков
  - Backend: Валидация character_id при создании токена — проверка принадлежности персонажа к сессии
  - Backend: Проверка прав при обновлении токена — только GM или владелец персонажа (с разрешением) может двигать
  - Backend: Поле can_move в модели Player + миграция — GM может разрешать/запрещать движение каждому игроку
  - Backend: Endpoint PATCH /players/{player_id}/movement — toggle движения с WebSocket broadcast
  - Frontend: AddTokenModal — модалка создания токена с выбором персонажа из сессии или произвольного токена
  - Frontend: Автоматическое имя и цвет токена из данных персонажа/игрока
  - Frontend: Per-token read-only — игроки двигают только свой токен и только с разрешения GM
  - Frontend: PlayersTab — dropdown меню с кнопками Информация, Инвентарь, Движение для каждого игрока
  - Frontend: Зелёная обводка токена игрока при включённом разрешении на движение
  - Frontend: WebSocket handler player_movement_changed для синхронизации разрешений в реальном времени
2026-02-05: Исправлены критические баги WebSocket: race conditions (asyncio.Lock),
  утечки мёртвых соединений, heartbeat/ping, DB session per message, reconnect,
  таймаут receive, лимит размера сообщений, обработка ошибок в handlers,
  logging вместо print.

2026-02-04: Исправлена ошибка 405 на VPS при создании персонажей/NPC/карт
  - Причина: catch-all GET маршрут для SPA (`/{full_path:path}`) перехватывал POST/PUT/DELETE запросы к API при наличии собранного фронтенда
  - Заменён catch-all route на exception handler для StarletteHTTPException
  - API роуты больше не конфликтуют с раздачей SPA статики

2026-02-04: Выбор карты из профиля при создании сессии
  - Backend: SessionCreate принимает user_map_id — опциональный ID карты из профиля
  - Backend: POST /session копирует UserMap в Map сессии с is_active=True при указании user_map_id
  - Frontend: CreateSessionModal — модалка выбора карты при создании сессии
  - Frontend: Список карт из профиля с возможностью выбора, создание без карты
  - Frontend: sessionApi.createSession и sessionStore.createSession принимают user_map_id
  - Frontend: GMLobbyView — секция «Карты» с отображением карт сессии, выбором активной и импортом из профиля

2026-02-04: Броски с преимуществом и помехой (Advantage/Disadvantage)
  - Backend: DiceRoll схема принимает roll_type ("normal" | "advantage" | "disadvantage")
  - Backend: DiceResult возвращает all_rolls (оба набора бросков) и chosen_index (какой выбран)
  - Backend: DiceService.roll_with_type() — кидает два набора и выбирает лучший/худший
  - Frontend: DiceRollModal — два чекбокса "Преимущество" и "Помеха" в секции типа броска
  - Frontend: RollResult — визуальное отображение двух кубиков: выбранный подсвечен золотом и увеличен, отброшенный затемнён и зачёркнут
  - Frontend: Бейдж типа броска (Преимущество/Помеха) над результатом
  - Frontend: Увеличен таймер автозакрытия до 3 секунд для advantage/disadvantage бросков

2026-02-04: Исправлена синхронизация токенов карты в реальном времени
  - Исправлен broadcast token_added — теперь отправляются все поля токена (scale, rotation, layer, label, color, map_id), а не только id/x/y/type
  - Добавлен broadcast map_created при создании карты — игроки получают карту без перезагрузки
  - Добавлен fallback fetchSessionMaps() в обработчиках token_added/token_updated при отсутствии карты в локальном сторе (race condition)
  - Добавлен обработчик события map_created во фронтенд map store

2026-02-04: Исправлена авторизация, разлогин и автозаполнение форм
  - Разделение токенов: пользовательские JWT сохраняются в userAccessToken/userRefreshToken перед перезаписью сессионными
  - clearSession() восстанавливает пользовательские токены вместо удаления — выход из сессии больше не разлогинивает
  - Исправлен URL refresh-токена: /session/auth/refresh → /auth/refresh
  - Автозаполнение: handleLogin/handleRegister читают значения из FormData (DOM) вместо пустых Vue refs
  - Кнопка входа больше не disabled при автозаполнении (валидация перенесена в обработчик)
  - LoginView и RegisterView обёрнуты в <form> с name/autocomplete атрибутами
  - BaseButton: добавлен проп type для type="submit"

2026-02-04: Исправлена передача персонажа игрока к GM в лобби
  - При join_session с персонажем теперь отправляется WebSocket broadcast character_created
  - GM получает персонажа в реальном времени через существующий handler в characters store

2026-02-04: Startup-миграции для SQLite
  - Добавлен app/migrations.py — лёгкий скрипт миграций, запускается при старте приложения
  - Автоматически проверяет схему БД и добавляет недостающие столбцы (ALTER TABLE)
  - Идемпотентный — безопасно перезапускать, пропускает уже существующие столбцы
  - Текущие миграции: players.is_ready, players.user_id, user_characters.sessions_played
  - Подключён в main.py после Base.metadata.create_all()

2026-02-04: Исправлены ошибки 500 при создании сессий и персонажей
  - Причина: столбцы user_id (players) и sessions_played (user_characters) отсутствовали в SQLite
  - create_all() не добавляет столбцы в существующие таблицы — теперь покрыто миграциями

2026-02-04: Исправлен скроллинг на всех страницах
  - Убран overflow: hidden с body и #app в base.css — это блокировало прокрутку на всех страницах
  - #app теперь использует min-height: 100vh вместо фиксированной высоты
  - GMLayout и PlayerLayout сохраняют overflow: hidden (полноэкранный интерфейс с картой)
  - GMLobbyView и PlayerLobbyView: убраны лишние overflow-y: auto (скроллится body)

2026-02-04: Dashboard — главная страница как дашборд со статистикой
  - Frontend: HomeView переделан в Dashboard с quick actions, обзором статистики и топ-5 играемых персонажей
  - Frontend: Quick actions — создание сессии (GM), присоединение к сессии, создание персонажа (Player)
  - Frontend: Обзор — карточки: сессий сыграно, персонажей, NPC
  - Frontend: Секция "Самые играемые персонажи" — ранжирование по sessions_played с заглушкой при пустых данных
  - Frontend: Тип UserStats, метод authApi.getStats()
  - Backend: Поле sessions_played в модели UserCharacter — инкрементируется при join session с персонажем
  - Backend: API endpoint GET /api/users/me/stats — total_characters, total_npcs, total_sessions, top_characters
  - Backend: Pydantic-схема UserStatsResponse

2026-02-04: Создание, редактирование, импорт персонажей/карт и улучшения UX
  - Frontend: CreateCharacterView — форма создания персонажа/NPC с выбором шаблона класса и inline-валидацией
  - Frontend: EditCharacterView — редактирование существующего персонажа/NPC с предзаполнением формы
  - Frontend: CreateMapView — форма создания карты с настройками размеров и сетки
  - Frontend: ConfirmModal — переиспользуемый диалог подтверждения (удаление, выход)
  - Frontend: ImportNpcModal — импорт NPC из профиля в активную сессию
  - Frontend: ImportMapModal — загрузка карты из профиля в активную сессию
  - Frontend: ProfileView обновлён: навигация вместо плейсхолдеров, кнопки редактирования, подтверждение удаления
  - Frontend: JoinSessionView: ссылка на создание персонажа, предупреждение при входе без персонажа
  - Frontend: Кнопка "Покинуть сессию" с подтверждением во всех session views (GM/Player Lobby/Game)
  - Frontend: UserCharacterCard: добавлены prop editable и emit edit
  - Frontend: NPCSection: кнопка "Из профиля" для импорта NPC
  - Frontend: GMLobbyView: кнопка "Загрузить карту из профиля"
  - Frontend: Session store: добавлен characterId ref
  - Frontend: Router: маршруты create-character, edit-character, create-map
  - Backend: create_session устанавливает user_id для GM Player

2026-02-03: Личная страница пользователя (Profile) и user-level сущности
  - Backend: Модель UserCharacter (персонажи пользователя, не привязанные к сессии, поддержка NPC)
  - Backend: Модель UserMap (карты пользователя, не привязанные к сессии)
  - Backend: Pydantic-схемы для CRUD операций с UserCharacter и UserMap
  - Backend: API роутеры /api/me/characters и /api/me/maps с полным CRUD
  - Backend: get_optional_current_user dependency для опциональной авторизации
  - Backend: При join session с user_character_id — копирование UserCharacter в сессионный Character
  - Frontend: ProfileView (/profile) с секциями персонажей, карт, NPC в зависимости от роли
  - Frontend: JoinSessionView (/join) с выбором персонажа перед входом в сессию
  - Frontend: Компоненты AddCard, UserCharacterCard, UserMapCard
  - Frontend: Profile store (Pinia) для управления user-level сущностями
  - Frontend: Обновлён session store для передачи user_character_id при join
  - Frontend: Ссылка "Мой профиль" на главной странице

2026-02-03: Система регистрации и авторизации пользователей
  - Backend: Модель User (username, display_name, hashed_password, role)
  - Backend: Pydantic-схемы UserRegister, UserLogin, UserResponse, AuthResponse
  - Backend: API роутер /api/users с эндпоинтами register, login, me
  - Backend: Хеширование паролей через passlib/bcrypt, JWT токены с sub "user:{id}"
  - Backend: Dependency get_current_user для защиты эндпоинтов
  - Backend: Добавлено поле user_id (FK, nullable) в модель Player для будущей привязки
  - Frontend: Auth store (Pinia) с register, login, logout, fetchMe
  - Frontend: LoginView и RegisterView с выбором роли (Игрок/GM)
  - Frontend: Router guards — незалогиненные пользователи перенаправляются на /login
  - Frontend: HomeView показывает имя пользователя и кнопку выхода

2026-02-03: Реализована интерактивная карта (Canvas/Konva.js)
  - Frontend: Добавлены библиотеки konva и vue-konva
  - Frontend: Компонент GameMap с поддержкой зума, панорамирования и слоев (фон, сетка, токены)
  - Frontend: Компонент MapToken с отображением имени и цвета
  - Frontend: Интеграция карты в интерфейс GM (создание, управление) и Игрока (только просмотр)
  - Backend: Модели Map и MapToken, API эндпоинты для управления картами
  - Backend: WebSocket события (map_changed, token_added, token_updated, token_removed) для синхронизации
  - Real-time: Перемещение токенов GM-ом мгновенно отображается у игроков
  - Ограничение прав: Игроки видят карту в режиме readonly (не могут двигать токены)

2026-02-02: Техническое обслуживание репозитория
  - Создан .gitignore для исключения pycache, venv, баз данных и node_modules
  - Удалены ранее отслеживаемые файлы __pycache__ из индекса Git

2026-02-02: Настройка окружения для локальной разработки в Docker
  - Создан backend.dev.Dockerfile с поддержкой горячей перезагрузки (uvicorn --reload)
  - Создан frontend.dev.Dockerfile для запуска Vite в контейнере
  - Создан docker-compose.dev.yml для связки сервисов с использованием volumes
  - Обновлен CLAUDE.md командами для запуска Docker-окружения

2026-02-01: Система аутентификации JWT и улучшение API
  - Backend: Реализована JWT аутентификация (Access & Refresh tokens)
  - Backend: Добавлена зависимость python-jose и passlib
  - Backend: Защищены все эндпоинты (session, characters, combat, dice, templates, persistence) через Bearer токены
  - Backend: Добавлен эндпоинт /api/session/auth/refresh для обновления токенов
  - Frontend: Реализованы Axios interceptors для автоматической вставки токенов и обновления при 401 ошибке
  - Frontend: Обновлены Pinia сторы (session, characters, combat, dice) для работы с новой схемой авторизации
  - Frontend: Убрана ручная передача токенов в методы API клиентов
  - Документация: Создан файл docs/auth.md с описанием работы JWT системы
  - Bugfix: Исправлены синтаксические ошибки и дублирование событий WebSocket в API эндпоинтах
  - Bugfix: Исправлена ошибка "missing token" при создании персонажа из шаблона
  - Bugfix: Исправлен роутинг SPA на сервере для корректной работы путей при деплое на VPS

2026-02-01: Подготовка к деплою (Docker)
  - Создан Dockerfile для мульти-этапной сборки (frontend + backend)
  - Создан docker-compose.yml для запуска на VPS
  - Добавлена раздача статики фронтенда через FastAPI в app/main.py
  - Настроен .dockerignore

2026-02-01: Код проекта залит в репозиторий GitHub
  - Настроен удаленный репозиторий origin: https://github.com/qqForest/DnD-Lite.git
  - Основная ветка main отправлена на сервер

2026-02-01: Улучшения UI системы боя и инициативы
  - Frontend: CombatTab - вкладка "Бой" в левом сайдбаре GM
  - Frontend: InitiativeBar - горизонтальная полоса инициативы сверху
  - Frontend: InitiativeBar показывает карточки персонажей слева направо
  - Frontend: Кнопка "Начать бой" перенесена в CombatTab
  - Frontend: Список инициативы теперь в вертикальном виде в CombatTab
  - Frontend: GMLayout обновлён с новой grid-областью для initiative-bar
  - UX: Плавные анимации для карточек инициативы

2026-02-01: Реализована система боя с инициативой
  - Backend: модель InitiativeRoll для хранения бросков инициативы
  - Backend: API endpoints POST/GET /api/combat/initiative
  - Backend: упрощён POST /api/combat/start (character_ids опционален)
  - Backend: GET /api/combat теперь включает initiative_list
  - Backend: WebSocket событие initiative_rolled отправляется только GM
  - Frontend: Pinia store combat.ts для управления состоянием боя
  - Frontend: InitiativeRollModal - модальное окно для броска игрока
  - Frontend: InitiativeList - список инициативы для GM с медалями
  - Frontend: интеграция в PlayerView и GMView
  - GM видит кнопку "Начать бой" → игроки получают модалку → GM видит результаты
  - Приватные броски (только игрок и GM видят результат)

2026-02-01: Документация системы боя и инициативы
  - Создан docs/combat-initiative.md с полной спецификацией
  - Описана механика: GM запускает бой → игроки бросают d20 → сортировка по инициативе
  - Приватные броски инициативы (видны только игроку и GM)
  - Автоматическое модальное окно для игроков при начале боя
  - GM видит список всех бросков отсортированный по убыванию
  - Архитектура: новые модели CombatState, InitiativeRoll
  - API endpoints и WebSocket события
  - Порядок реализации из 10 шагов

2026-02-01: Исправления системы бросков кубиков
  - Backend: добавлено поле formula в DiceResult схему
  - Backend: добавлено поле timestamp в DiceResult (автоматическое заполнение)
  - Backend: formula корректно формируется из dice notation
  - Frontend: убрано дублирование показа RollResult (теперь только через WebSocket)
  - RollResult автоматически показывается всем подключенным клиентам
  - Все игроки и GM видят кто бросил кубик (player_name в результате)
  - Исправлен сайдбар игрока (добавлен cursor: pointer)

2026-02-01: Переработан интерфейс игрока (PlayerView)
  - Карта теперь занимает всё пространство между топ и боттом барами (без padding)
  - Добавлен выдвижной сайдбар (PlayerSidebar) с информацией о сессии
  - Кнопка меню слева сверху в PlayerTopBar для открытия сайдбара
  - "Информация о сессии" перенесена в сайдбар
  - Переделана система бросков - одна кнопка "Бросок" открывает модалку (как у GM)
  - PlayerDiceSelector теперь компактный (кнопка + последний результат)
  - Добавлена поддержка RollResult модального окна для игрока
  - Плавная анимация выдвижения сайдбара (slide from left)
  - Клик по последнему броску открывает детали

2026-02-01: Улучшения UX системы бросков кубиков
  - RollResult автоматически закрывается через 1.5 секунды
  - Добавлена плавная анимация закрытия окна результата (fade-out + scale)
  - Исправлено дублирование бросков в истории (был баг с WebSocket)
  - Теперь показывается только последний бросок в нижней панели (вместо 3)
  - Убран таймер при ручном закрытии результата
  - Двухфазное закрытие: анимация → скрытие компонента

2026-02-01: Переработана система бросков кубиков для компактности
  - DiceRollModal - модальное окно для выбора кубика и броска
  - Одна кнопка "Бросок" в BottomBar вместо всех кубиков
  - Модалка с красивой сеткой кубиков (d4-d100)
  - Поле модификатора и кастомной формулы в модалке
  - История последних 3 бросков справа, кликабельна для просмотра деталей
  - Компактный и удобный интерфейс

2026-02-01: Реализован основной GM интерфейс после начала игры
  - GMLayout с TopBar, LeftPanel, BottomBar и main area
  - TopBar - показывает код сессии, количество игроков, статус подключения
  - LeftPanel - табы: Игроки, События, Бой, Статистика (вкладки с заглушками)
  - BottomBar - DiceSelector + последние 3 броска
  - PlayersTab в левой панели для просмотра игроков
  - Интеграция с системой бросков кубиков
  - RollResult модальное окно показывается при броске
  - Адаптивный layout для мобильных устройств

2026-02-01: Реализована система бросков кубиков
  - DiceButton - кнопка выбора кубика с визуальной индикацией
  - DiceSelector - панель выбора и броска кубиков (d4, d6, d8, d10, d12, d20, d100)
  - RollResult - модальное окно с анимацией результата броска
  - RollHistory - история последних бросков с временными метками
  - Поддержка модификаторов (+/-) и пользовательских формул
  - Детекция критических успехов (20 на d20) и провалов (1 на d20)
  - WebSocket синхронизация результатов между всеми участниками
  - Обновлен dice store с методами roll(), hideResult(), clearHistory()
  - Временно добавлено в GM лобби для тестирования

2026-02-01: Исправлен скроллинг в лобби
  - Добавлен max-height и overflow-y: auto для PlayersLobbyList
  - Добавлен max-height и overflow-y: auto для NPCSection
  - Добавлен max-height и overflow-y: auto для CharacterSelection
  - Стилизован scrollbar для единого дизайна (тонкий, полупрозрачный)

2026-02-01: Исправлена проблема синхронизации WebSocket на VPS
  - Исправлена проблема синхронизации WebSocket на VPS (динамическое определение URL).
  - Предотвращено дублирование обработчиков событий WebSocket в Pinia сторах.
  - Улучшено управление жизненным циклом WebSocket подключений.

2026-01-27: Добавлены шаблоны классов D&D 5e
  - 12 классов: Fighter, Wizard, Rogue, Cleric, Barbarian, Paladin, Bard, Druid, Monk, Sorcerer, Warlock
  - Каждый шаблон включает: характеристики, HP, стартовые предметы и заклинания
  - API endpoints: GET /api/templates, GET /api/templates/{id},
    POST /api/templates/create
  - Русские и английские названия/описания

2026-01-27: Добавлена система сохранения сессий (persistence)
  - Новый модуль app/services/persistence/ с Registry паттерном
  - Сериализаторы для Player, Character, Item, Spell, Combat
  - API endpoints: /api/session/export, /api/session/export/download,
    /api/session/import, /api/session/validate
  - Поддержка версионирования формата и миграций
  - Документация в docs/persistence.md

2026-01-27: Создан базовый фронтенд для GM интерфейса
  - Vue 3 + TypeScript + Vite проект
  - Design tokens и базовая дизайн-система
  - Pinia stores: session, characters, dice
  - API клиент с Axios и WebSocket сервис
  - Базовые компоненты: BaseButton, BasePanel, BaseInput, BaseModal
  - Компоненты персонажей: CharacterCard, HPBar
  - GM Layout с TopBar, LeftPanel, BottomBar
  - HomeView для создания/входа в сессию
  - GMView с интеграцией всех компонентов
  - Vue Router с navigation guards
  - Интеграция с REST API и WebSocket для реального времени

2026-01-27: Интеграция Templates API и UI создания персонажей
  - Добавлены TypeScript типы для шаблонов классов
  - Templates API интеграция (list, get, createCharacter)
  - Метод createFromTemplate() в characters store
  - Компоненты: ClassTemplateCard, TemplateSelector
  - CreateCharacterModal с двухшаговым процессом создания
  - Кнопка создания персонажа в PlayersTab
  - Toast уведомления для успеха/ошибки операций
  - Визуальное выделение классов цветами из design tokens

2026-01-27: Реализовано лобби сессии для GM
  - Backend: добавлено поле session_started в модель Session
  - Миграция БД: добавлена колонка session_started в таблицу sessions
  - API endpoint POST /api/session/start для старта сессии
  - GMLobbyView - страница лобби с настройками перед игрой
  - SessionCodeDisplay - отображение кода сессии с копированием
  - PlayersLobbyList - список игроков с их персонажами (разворачиваемый)
  - NPCSection - управление NPC с созданием и удалением
  - SessionSettings - экспорт/импорт сессии и статистика
  - StartGameButton - кнопка начала игры с переходом на основной интерфейс
  - Роутинг: /gm/lobby для лобби, автоматические редиректы по состоянию сессии
  - Кнопка создания персонажа перенесена из PlayersTab в NPCSection
  - Toast компонент для уведомлений пользователя

2026-01-27: Реализован интерфейс игрока MVP
  - PlayerLayout - layout компонент для интерфейса игрока с CSS Grid структурой
  - PlayerTopBar - компактный заголовок с кодом сессии, статусом подключения и именем игрока
  - CharacterSheet - компонент для отображения персонажей игрока с возможностью выбора
  - PlayerDiceSelector - упрощенный селектор кубиков для игрока с отображением последнего результата
  - PlayerView - полная реализация интерфейса игрока с интеграцией всех компонентов
  - WebSocket интеграция для обновлений в реальном времени (персонажи, кубики, статус сессии)
  - Адаптивный дизайн для мобильных и десктоп устройств
  - Заглушка карты для будущей реализации интерактивной карты

2026-01-27: Добавлен выбор персонажа и статус готовности в лобби
  - Backend: добавлено поле is_ready в модель Player и миграция БД
  - API endpoint POST /api/session/ready для установки статуса готовности игрока
  - PlayerLobbyView - страница лобби игрока с выбором/созданием персонажа и кнопкой готовности
  - CharacterSelection - компонент для выбора существующего или создания нового персонажа
  - ReadyButton - кнопка переключения статуса готовности (готов/не готов)
  - PlayersLobbyList - добавлен индикатор готовности игроков для GM с подсчетом готовых
  - WebSocket событие player_ready для обновления статуса в реальном времени
  - Роутинг: игроки попадают в /play/lobby до начала игры, затем редирект на /play
  - Обновлен HomeView: после присоединения редирект на лобби игрока
