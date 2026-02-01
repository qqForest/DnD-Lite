# Frontend Architecture

Архитектура Vue приложения DnD Lite GM.

## Технологический стек

| Технология | Назначение |
|------------|------------|
| **Vue 3** | UI фреймворк (Composition API) |
| **Vite** | Сборщик и dev server |
| **Pinia** | State management |
| **Vue Router** | Роутинг |
| **TypeScript** | Типизация |
| **Canvas API** | Рендеринг карты |

## Структура проекта

```
frontend/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
│
├── public/
│   ├── favicon.ico
│   └── fonts/
│
├── src/
│   ├── main.ts                 # Entry point
│   ├── App.vue                 # Root component
│   │
│   ├── assets/
│   │   ├── css/
│   │   │   ├── tokens.css      # Design tokens
│   │   │   ├── base.css        # Reset, typography
│   │   │   └── utilities.css   # Utility classes
│   │   └── icons/              # SVG иконки (если не Lucide)
│   │
│   ├── router/
│   │   └── index.ts            # Vue Router config
│   │
│   ├── stores/                 # Pinia stores
│   │   ├── session.ts          # Сессия, игроки
│   │   ├── characters.ts       # Персонажи
│   │   ├── combat.ts           # Состояние боя
│   │   ├── map.ts              # Состояние карты
│   │   ├── dice.ts             # Броски кубиков
│   │   └── ui.ts               # UI состояние (панели, модалки)
│   │
│   ├── composables/            # Reusable logic
│   │   ├── useWebSocket.ts     # WebSocket connection
│   │   ├── useGestures.ts      # Touch gestures
│   │   ├── useCanvas.ts        # Canvas rendering
│   │   ├── useDice.ts          # Dice rolling logic
│   │   └── useAuth.ts          # Token management
│   │
│   ├── services/               # API & external services
│   │   ├── api.ts              # REST API client
│   │   └── websocket.ts        # WebSocket service
│   │
│   ├── types/                  # TypeScript types
│   │   ├── models.ts           # Domain models
│   │   ├── api.ts              # API types
│   │   └── events.ts           # WebSocket events
│   │
│   ├── layouts/
│   │   ├── GMLayout.vue
│   │   └── PlayerLayout.vue
│   │
│   ├── views/                  # Page components
│   │   ├── HomeView.vue        # Главная (создать/войти)
│   │   ├── GMView.vue          # GM интерфейс
│   │   └── PlayerView.vue      # Player интерфейс
│   │
│   └── components/
│       ├── common/             # Shared components
│       │   ├── BaseButton.vue
│       │   ├── BaseInput.vue
│       │   ├── BasePanel.vue
│       │   ├── BaseModal.vue
│       │   └── Toast.vue
│       │
│       ├── gm/                 # GM-specific
│       │   ├── TopBar.vue
│       │   ├── LeftPanel.vue
│       │   ├── PlayersTab.vue
│       │   ├── EventLog.vue
│       │   ├── CombatTracker.vue
│       │   └── SessionSettings.vue
│       │
│       ├── player/             # Player-specific
│       │   ├── CharacterSheet.vue
│       │   ├── CharacterHeader.vue
│       │   ├── StatsBar.vue
│       │   ├── ItemsList.vue
│       │   └── SpellsList.vue
│       │
│       ├── dice/
│       │   ├── DiceSelector.vue
│       │   ├── DiceCarousel.vue
│       │   ├── DiceButton.vue
│       │   ├── RollResult.vue
│       │   └── RollHistory.vue
│       │
│       ├── map/
│       │   ├── CanvasMap.vue
│       │   ├── MapControls.vue
│       │   ├── Token.vue
│       │   └── GridOverlay.vue
│       │
│       └── character/          # Shared character components
│           ├── CharacterCard.vue
│           ├── HPBar.vue
│           └── AbilityScore.vue
```

---

## Routing

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/gm',
    name: 'gm',
    component: () => import('@/views/GMView.vue'),
    meta: { requiresAuth: true, role: 'gm' }
  },
  {
    path: '/play',
    name: 'player',
    component: () => import('@/views/PlayerView.vue'),
    meta: { requiresAuth: true, role: 'player' }
  },
  {
    path: '/join/:code',
    name: 'join',
    component: () => import('@/views/JoinView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'home' })
  } else if (to.meta.role && authStore.role !== to.meta.role) {
    next({ name: authStore.role === 'gm' ? 'gm' : 'player' })
  } else {
    next()
  }
})
```

---

## State Management (Pinia)

### Session Store

```typescript
// src/stores/session.ts
import { defineStore } from 'pinia'

interface Player {
  id: number
  name: string
  isGm: boolean
  isOnline: boolean
}

interface SessionState {
  id: number | null
  code: string | null
  token: string | null
  isGm: boolean
  players: Player[]
  isConnected: boolean
}

export const useSessionStore = defineStore('session', {
  state: (): SessionState => ({
    id: null,
    code: null,
    token: localStorage.getItem('token'),
    isGm: false,
    players: [],
    isConnected: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentPlayer: (state) => state.players.find(p =>
      p.isGm === state.isGm
    ),
    otherPlayers: (state) => state.players.filter(p => !p.isGm)
  },

  actions: {
    async createSession() {
      const response = await api.post('/session')
      this.code = response.data.code
      this.token = response.data.gm_token
      this.isGm = true
      localStorage.setItem('token', this.token)
    },

    async joinSession(code: string, name: string) {
      const response = await api.post('/session/join', { code, name })
      this.token = response.data.token
      this.code = code
      this.isGm = false
      localStorage.setItem('token', this.token)
    },

    // WebSocket handlers
    onPlayerJoined(player: Player) {
      this.players.push(player)
    },

    onPlayerLeft(playerId: number) {
      this.players = this.players.filter(p => p.id !== playerId)
    }
  }
})
```

### Characters Store

```typescript
// src/stores/characters.ts
import { defineStore } from 'pinia'
import type { Character } from '@/types/models'

export const useCharactersStore = defineStore('characters', {
  state: () => ({
    characters: [] as Character[],
    selectedId: null as number | null,
    loading: false
  }),

  getters: {
    selected: (state) =>
      state.characters.find(c => c.id === state.selectedId),

    byPlayer: (state) => (playerId: number) =>
      state.characters.filter(c => c.playerId === playerId)
  },

  actions: {
    async fetchAll() {
      this.loading = true
      try {
        const response = await api.get('/characters')
        this.characters = response.data
      } finally {
        this.loading = false
      }
    },

    async createFromTemplate(templateId: string, name: string) {
      const response = await api.post('/templates/create', {
        template_id: templateId,
        name
      })
      this.characters.push(response.data)
      return response.data
    },

    // WebSocket handler
    onCharacterUpdated(character: Character) {
      const index = this.characters.findIndex(c => c.id === character.id)
      if (index !== -1) {
        this.characters[index] = character
      }
    }
  }
})
```

### Map Store

```typescript
// src/stores/map.ts
import { defineStore } from 'pinia'

interface Token {
  id: string
  characterId: number | null
  x: number
  y: number
  color: string
  size: number
}

interface MapState {
  zoom: number
  offsetX: number
  offsetY: number
  gridSize: number
  showGrid: boolean
  tokens: Token[]
  selectedTokenId: string | null
}

export const useMapStore = defineStore('map', {
  state: (): MapState => ({
    zoom: 1,
    offsetX: 0,
    offsetY: 0,
    gridSize: 50,
    showGrid: true,
    tokens: [],
    selectedTokenId: null
  }),

  getters: {
    selectedToken: (state) =>
      state.tokens.find(t => t.id === state.selectedTokenId),

    visibleArea: (state) => ({
      x: -state.offsetX / state.zoom,
      y: -state.offsetY / state.zoom,
      width: window.innerWidth / state.zoom,
      height: window.innerHeight / state.zoom
    })
  },

  actions: {
    pan(deltaX: number, deltaY: number) {
      this.offsetX += deltaX
      this.offsetY += deltaY
    },

    setZoom(zoom: number, centerX: number, centerY: number) {
      const zoomDelta = zoom / this.zoom
      this.offsetX = centerX - (centerX - this.offsetX) * zoomDelta
      this.offsetY = centerY - (centerY - this.offsetY) * zoomDelta
      this.zoom = Math.max(0.5, Math.min(3, zoom))
    },

    moveToken(tokenId: string, x: number, y: number) {
      const token = this.tokens.find(t => t.id === tokenId)
      if (token) {
        token.x = x
        token.y = y
      }
    }
  }
})
```

---

## WebSocket Integration

```typescript
// src/services/websocket.ts
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useDiceStore } from '@/stores/dice'

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnects = 5

  connect(token: string) {
    const url = `${import.meta.env.VITE_WS_URL}/ws?token=${token}`
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      useSessionStore().isConnected = true
    }

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      this.handleMessage(message)
    }

    this.ws.onclose = () => {
      useSessionStore().isConnected = false
      this.attemptReconnect(token)
    }
  }

  private handleMessage(message: { event: string; data: any }) {
    const sessionStore = useSessionStore()
    const charactersStore = useCharactersStore()
    const diceStore = useDiceStore()

    switch (message.event) {
      case 'player_joined':
        sessionStore.onPlayerJoined(message.data)
        break
      case 'player_left':
        sessionStore.onPlayerLeft(message.data.player_id)
        break
      case 'character_updated':
        charactersStore.onCharacterUpdated(message.data.character)
        break
      case 'dice_result':
        diceStore.onDiceResult(message.data)
        break
      case 'combat_started':
        // ...
        break
    }
  }

  send(event: string, data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ event, data }))
    }
  }

  private attemptReconnect(token: string) {
    if (this.reconnectAttempts < this.maxReconnects) {
      this.reconnectAttempts++
      setTimeout(() => this.connect(token), 2000 * this.reconnectAttempts)
    }
  }
}

export const wsService = new WebSocketService()
```

---

## Canvas Map Architecture

```typescript
// src/composables/useCanvas.ts
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useMapStore } from '@/stores/map'

export function useCanvas(canvasRef: Ref<HTMLCanvasElement | null>) {
  const mapStore = useMapStore()
  let ctx: CanvasRenderingContext2D | null = null
  let animationFrameId: number | null = null

  // Layers (bottom to top)
  const layers = {
    background: new BackgroundLayer(),
    grid: new GridLayer(),
    tokens: new TokensLayer(),
    effects: new EffectsLayer(),
    ui: new UILayer()
  }

  function render() {
    if (!ctx || !canvasRef.value) return

    const { width, height } = canvasRef.value

    // Clear
    ctx.clearRect(0, 0, width, height)

    // Apply transform
    ctx.save()
    ctx.translate(mapStore.offsetX, mapStore.offsetY)
    ctx.scale(mapStore.zoom, mapStore.zoom)

    // Render layers
    layers.background.render(ctx, mapStore)
    if (mapStore.showGrid) {
      layers.grid.render(ctx, mapStore)
    }
    layers.tokens.render(ctx, mapStore)
    layers.effects.render(ctx, mapStore)

    ctx.restore()

    // UI layer in screen space
    layers.ui.render(ctx, mapStore)

    animationFrameId = requestAnimationFrame(render)
  }

  onMounted(() => {
    if (canvasRef.value) {
      ctx = canvasRef.value.getContext('2d')
      resizeCanvas()
      render()
    }
  })

  onUnmounted(() => {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
    }
  })

  function resizeCanvas() {
    if (canvasRef.value) {
      const dpr = window.devicePixelRatio || 1
      const rect = canvasRef.value.getBoundingClientRect()
      canvasRef.value.width = rect.width * dpr
      canvasRef.value.height = rect.height * dpr
      ctx?.scale(dpr, dpr)
    }
  }

  return {
    layers,
    resizeCanvas
  }
}
```

---

## API Client

```typescript
// src/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api'
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.params = { ...config.params, token }
  }
  return config
})

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export { api }
```

---

## Environment Variables

```env
# .env.development
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000

# .env.production
VITE_API_URL=/api
VITE_WS_URL=wss://your-domain.com
```
