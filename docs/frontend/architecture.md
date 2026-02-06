# Frontend Architecture

Архитектура Vue приложения DnD Lite GM.

## Технологический стек

| Технология | Назначение |
|------------|------------|
| **Vue 3** | UI фреймворк (Composition API + `<script setup>`) |
| **Vite** | Сборщик и dev server |
| **Pinia** | State management |
| **Vue Router** | Роутинг с guards |
| **TypeScript** | Типизация |
| **Konva.js** | Рендеринг карты (vue-konva) |
| **Axios** | HTTP клиент с interceptors |
| **Lucide** | Иконки |
| **Google Fonts** | Шрифт Cinzel (D&D стиль) |

## Структура проекта

```
frontend/
├── index.html              # Google Fonts Cinzel preconnect + link
├── vite.config.ts
├── tsconfig.json
├── package.json
│
├── src/
│   ├── main.ts             # Entry point
│   ├── App.vue             # Root component
│   │
│   ├── assets/css/
│   │   ├── tokens.css      # Design tokens (CSS custom properties)
│   │   ├── base.css        # Reset, typography, scrollbar
│   │   └── utilities.css   # Utility classes
│   │
│   ├── router/
│   │   └── index.ts        # Vue Router + navigation guards
│   │
│   ├── stores/             # Pinia stores (Composition API)
│   │   ├── auth.ts         # Регистрация, логин, logout, JWT
│   │   ├── session.ts      # Сессия, WebSocket, игроки, ready
│   │   ├── characters.ts   # Сессионные персонажи
│   │   ├── combat.ts       # Бой, инициатива
│   │   ├── dice.ts         # Броски кубиков
│   │   ├── map.ts          # Карты, токены, WS handlers
│   │   └── profile.ts      # Библиотека персонажей/карт (вне сессий)
│   │
│   ├── composables/
│   │   ├── useWebSocket.ts # WS подключение + reconnect
│   │   ├── useSwipe.ts     # Свайп-жесты (Pointer Events)
│   │   ├── useToast.ts     # Toast уведомления
│   │   └── useAuth.ts      # Token management
│   │
│   ├── services/
│   │   ├── api.ts          # Axios клиент + interceptors + все API endpoints
│   │   └── websocket.ts    # WebSocket service (EventEmitter, reconnect)
│   │
│   ├── types/
│   │   ├── models.ts       # Domain models (User, Character, Session, Map...)
│   │   ├── api.ts          # API response/request types
│   │   └── events.ts       # WebSocket event types
│   │
│   ├── data/
│   │   └── tokenIcons.ts   # 15 SVG иконок для токенов карты
│   │
│   ├── views/
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   ├── HomeView.vue            # Dashboard со статистикой
│   │   ├── ProfileView.vue         # Профиль (карусель, сайдбар)
│   │   ├── JoinSessionView.vue     # Присоединение (карусель, код)
│   │   ├── GMLobbyView.vue         # Лобби GM
│   │   ├── GMView.vue              # Основной интерфейс GM
│   │   ├── PlayerLobbyView.vue     # Лобби игрока (flip-карточка, готовность)
│   │   ├── PlayerView.vue          # Основной интерфейс игрока
│   │   ├── CreateCharacterView.vue
│   │   ├── EditCharacterView.vue
│   │   └── CreateMapView.vue
│   │
│   └── components/
│       ├── common/          # BaseButton, BaseInput, BaseModal, BasePanel,
│       │                    # ConfirmModal, Toast
│       ├── profile/         # CharacterFlipCard, CharacterCarousel,
│       │                    # ProfileTopBar, ProfileSidebar,
│       │                    # UserCharacterCard, UserMapCard, AddCard
│       ├── player/          # PlayerSidebar, PlayerTopBar,
│       │                    # PlayerLobbySidebar, PlayerLobbyTopBar,
│       │                    # ReadyButton, CharacterSelection
│       ├── gm/              # GMLayout, PlayersTab, NPCSection,
│       │                    # PlayersLobbyList, SessionCodeDisplay,
│       │                    # CreateSessionModal, ImportNpcModal, ImportMapModal
│       ├── character/       # CharacterCard, CharacterSheet, HPBar
│       ├── dice/            # DiceRollModal, RollResult, RollHistory
│       ├── combat/          # CombatTab, InitiativeBar, InitiativeRollModal
│       ├── map/             # GameMap (Konva.js), MapToken, AddTokenModal
│       └── templates/       # ClassTemplateCard, TemplateSelector
```

---

## Routing

```typescript
// Основные маршруты (src/router/index.ts)

// Публичные (requiresUser: false)
{ path: '/login',    name: 'login',    component: LoginView }
{ path: '/register', name: 'register', component: RegisterView }

// Требуют аккаунт (meta: { requiresUser: true })
{ path: '/',        name: 'home',     component: HomeView }
{ path: '/profile', name: 'profile',  component: ProfileView }
{ path: '/join',    name: 'join',     component: JoinSessionView }
{ path: '/create-character', name: 'create-character' }
{ path: '/edit-character/:id', name: 'edit-character' }
{ path: '/create-map', name: 'create-map' }

// Требуют сессионный токен (meta: { requiresAuth: true })
{ path: '/gm/lobby',  name: 'gm-lobby',     role: 'gm' }
{ path: '/gm',        name: 'gm',           role: 'gm' }
{ path: '/play/lobby', name: 'player-lobby', role: 'player' }
{ path: '/play',       name: 'player',       role: 'player' }
```

**Navigation guards:**
- Незалогиненные → `/login`
- Без сессии + `requiresAuth` → `/`
- GM на player routes → redirect на GM
- Player на GM routes → redirect на player
- Сессия начата + лобби → redirect на игру

---

## State Management (Pinia, Composition API)

Все stores используют `defineStore` с setup function:

```typescript
export const useSessionStore = defineStore('session', () => {
  const token = ref(localStorage.getItem('token') || '')
  const code = ref('')
  const players = ref<Player[]>([])
  const isConnected = ref(false)
  const isGm = ref(false)
  const isReady = computed(() => currentPlayer.value?.is_ready ?? false)

  async function joinSession(code: string, name: string, characterId?: number) { ... }
  async function setReady(isReady: boolean) { ... }
  function setupWebSocketHandlers() { ... }

  return { token, code, players, isConnected, isGm, isReady, joinSession, setReady, ... }
})
```

---

## WebSocket Integration

```typescript
// src/services/websocket.ts — EventEmitter-based service
class WebSocketService {
  connect(token: string): void
  disconnect(): void
  on(event: string, handler: Function): void
  off(event: string, handler: Function): void
  send(event: string, data: any): void
  isActiveFor(token: string): boolean
}

export const wsService = new WebSocketService()
```

**Паттерн подключения:**
1. `sessionStore.connectWebSocket()` → `wsService.connect(token)`
2. `sessionStore.setupWebSocketHandlers()` → `wsService.on('event', handler)`
3. `useWebSocket()` composable → авто-подключение + reconnect в компонентах

**События сервера (20):** `player_joined`, `player_left`, `player_ready`, `player_movement_changed`, `session_started`, `dice_result`, `character_created`, `character_updated`, `character_deleted`, `combat_started`, `combat_ended`, `turn_changed`, `hp_changed`, `initiative_rolled`, `map_created`, `map_changed`, `token_added`, `token_updated`, `token_removed`, `ping`

**События клиента (3):** `roll_dice`, `chat`, `pong`

---

## Аутентификация

Двухуровневая JWT система:

1. **Аккаунт:** `POST /auth/register` или `/auth/login` → `access_token` + `refresh_token`
2. **Сессия:** `POST /session` или `/session/join` → перезаписывает токены сессионными

Axios interceptors:
- Request: автоматически добавляет `Authorization: Bearer <token>`
- Response 401: авто-обновление через `refresh_token`, retry запроса

При выходе из сессии (`clearSession()`) восстанавливаются user-level токены из `userAccessToken`/`userRefreshToken`.

---

## Карта (Konva.js)

```vue
<!-- GameMap.vue -->
<v-stage :config="stageConfig" @wheel="handleZoom" @pointerdown="handlePan">
  <v-layer>                              <!-- Фон -->
    <v-image v-if="bgImage" :config="bgConfig" />
    <v-rect :config="bgFallback" />
  </v-layer>
  <v-layer>                              <!-- Сетка -->
    <v-line v-for="line in gridLines" :config="line" />
  </v-layer>
  <v-layer>                              <!-- Токены -->
    <MapToken v-for="token in tokens" :token="token" @dragend="updatePosition" />
  </v-layer>
</v-stage>
```

- Zoom: колесо мыши / pinch
- Pan: drag по пустому месту
- Токены: drag (GM — все; игрок — свой при `can_move`)
- Контекстное меню: ПКМ на токене (GM only)
