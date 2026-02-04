<template>
  <div class="player-lobby-view">
    <div class="lobby-container">
      <header class="lobby-header">
        <h1 class="lobby-title">Лобби игрока</h1>
        <div class="header-info">
          <span v-if="sessionStore.isConnected" class="connection-status connected">
            ● Подключено
          </span>
          <span v-else class="connection-status disconnected">
            ○ Отключено
          </span>
          <BaseButton variant="ghost" size="sm" @click="showLeaveModal = true">
            Покинуть
          </BaseButton>
        </div>
      </header>

      <SessionCodeDisplay />

      <BasePanel v-if="myCharacter" variant="elevated" class="character-preview">
        <template #header>
          <h3 class="panel-title">Ваш персонаж</h3>
        </template>
        <CharacterCard :character="myCharacter" />
      </BasePanel>

      <ReadyButton />

      <div class="waiting-status">
        <BasePanel variant="glass">
          <div class="status-content">
            <Clock :size="24" />
            <div>
              <p class="status-title">Ожидание начала игры</p>
              <p class="status-description">GM начнет игру, когда все будут готовы</p>
            </div>
          </div>
        </BasePanel>
      </div>
    </div>

    <ConfirmModal
      v-model="showLeaveModal"
      title="Покинуть сессию?"
      message="Вы уверены, что хотите покинуть текущую сессию?"
      confirm-text="Покинуть"
      :danger="true"
      @confirm="handleLeave"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Clock } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useWebSocket } from '@/composables/useWebSocket'
import { wsService } from '@/services/websocket'
import SessionCodeDisplay from '@/components/gm/SessionCodeDisplay.vue'
import CharacterCard from '@/components/character/CharacterCard.vue'
import ReadyButton from '@/components/player/ReadyButton.vue'
import BasePanel from '@/components/common/BasePanel.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const router = useRouter()
const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()

const showLeaveModal = ref(false)

const myCharacter = computed(() => {
  if (!sessionStore.currentPlayer) return null
  const chars = charactersStore.byPlayer(sessionStore.currentPlayer.id)
  return chars.length > 0 ? chars[0] : null
})

useWebSocket()

function handleLeave() {
  sessionStore.clearSession()
  router.push({ name: 'profile' })
}

onMounted(async () => {
  // Проверка аутентификации
  if (!sessionStore.isAuthenticated) {
    router.push({ name: 'home' })
    return
  }

  // Если GM пытается зайти на страницу игрока - редирект
  if (sessionStore.isGm) {
    router.push({ name: 'gm-lobby' })
    return
  }

  // Если сессия уже начата, редирект на основной интерфейс
  await sessionStore.fetchSessionState()
  if (sessionStore.sessionStarted) {
    router.push({ name: 'player' })
    return
  }

  // Загрузка данных
  try {
    await sessionStore.fetchPlayers()
    await charactersStore.fetchAll()
  } catch (error) {
    console.error('Failed to load lobby data:', error)
  }

  // Настройка WebSocket handlers
  setupWebSocketHandlers()
})

function setupWebSocketHandlers() {
  // Handlers для персонажей
  charactersStore.setupWebSocketHandlers()

  // Handler для начала сессии
  wsService.on('session_started', () => {
    sessionStore.sessionStarted = true
    if (sessionStore.sessionState) {
      sessionStore.sessionState.session_started = true
    }
    router.push({ name: 'player' })
  })
}
</script>

<style scoped>
.player-lobby-view {
  min-height: 100vh;
  padding: var(--spacing-6);
  background: var(--color-bg-primary);
}

.lobby-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.lobby-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-4);
}

.lobby-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-semibold);
  margin: 0;
  color: var(--color-text-primary);
}

.header-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.connection-status {
  font-size: var(--font-size-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.connection-status.connected {
  color: var(--color-success);
}

.connection-status.disconnected {
  color: var(--color-text-muted);
}

.panel-title {
  margin: 0;
}

.waiting-status {
  margin-top: var(--spacing-4);
}

.status-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
}

.status-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--spacing-1) 0;
  color: var(--color-text-primary);
}

.status-description {
  font-size: var(--font-size-sm);
  margin: 0;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .player-lobby-view {
    padding: var(--spacing-4);
  }

  .lobby-title {
    font-size: var(--font-size-2xl);
  }
}
</style>
